package org.muchen.aigen.service.impl;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.collection.CollUtil;
import cn.hutool.core.io.FileUtil;
import cn.hutool.core.util.RandomUtil;
import cn.hutool.core.util.StrUtil;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.mybatisflex.core.query.QueryWrapper;
import com.mybatisflex.spring.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.muchen.aigen.ai.AiCodeGenTypeRoutingService;
import org.muchen.aigen.constant.AppConstant;
import org.muchen.aigen.core.AiCodeGeneratorFacade;
import org.muchen.aigen.core.builder.VueProjectBuilder;
import org.muchen.aigen.core.handler.StreamHandlerExecutor;
import org.muchen.aigen.exception.BusinessException;
import org.muchen.aigen.exception.ErrorCode;
import org.muchen.aigen.exception.ThrowUtils;
import org.muchen.aigen.langgraph4j.CodeGenWorkflow;
import org.muchen.aigen.model.dto.app.AppAddRequest;
import org.muchen.aigen.model.dto.app.AppQueryRequest;
import org.muchen.aigen.model.dto.app.AppVO;
import org.muchen.aigen.model.entity.App;
import org.muchen.aigen.mapper.AppMapper;
import org.muchen.aigen.model.entity.User;
import org.muchen.aigen.model.enums.ChatHistoryMessageTypeEnum;
import org.muchen.aigen.model.enums.CodeGenTypeEnum;
import org.muchen.aigen.model.vo.UserVO;
import org.muchen.aigen.service.AppService;
import org.muchen.aigen.service.ChatHistoryService;
import org.muchen.aigen.service.ScreenshotService;
import org.muchen.aigen.service.UserService;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import java.io.File;
import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 应用 服务层实现。
 *
 * @author Muchen
 */
@Slf4j
@Service
public class AppServiceImpl extends ServiceImpl<AppMapper, App>  implements AppService{

    @Resource
    private UserService userService;

    @Resource
    private AiCodeGeneratorFacade aiCodeGeneratorFacade;

    @Resource
    private ChatHistoryService chatHistoryService;

    @Resource
    private StreamHandlerExecutor streamHandlerExecutor;

    @Resource
    private VueProjectBuilder vueProjectBuilder;

    @Resource
    private ScreenshotService screenshotService;

    @Resource
    private AiCodeGenTypeRoutingService aiCodeGenTypeRoutingService;

    @Resource
    private CodeGenWorkflow codeGenWorkflow;

    @Override
    public Long createApp(AppAddRequest appAddRequest, User loginUser) {
        // ... (保持原有逻辑)
        String initPrompt = appAddRequest.getInitPrompt();
        ThrowUtils.throwIf(StrUtil.isBlank(initPrompt), ErrorCode.PARAMS_ERROR, "初始化 prompt 不能为空");
        App app = new App();
        BeanUtil.copyProperties(appAddRequest, app);
        app.setUserId(loginUser.getId());
        app.setAppName(initPrompt.substring(0, Math.min(initPrompt.length(), 12)));
        CodeGenTypeEnum selectedCodeGenType = aiCodeGenTypeRoutingService.routeCodeGenType(initPrompt);
        app.setCodeGenType(selectedCodeGenType.getValue());
        boolean result = this.save(app);
        ThrowUtils.throwIf(!result, ErrorCode.OPERATION_ERROR);
        log.info("应用创建成功，ID: {}, 类型: {}", app.getId(), selectedCodeGenType.getValue());
        return app.getId();
    }

    @Override
    public AppVO getAppVO(App app) {
        if (app == null) {
            return null;
        }
        AppVO appVO = new AppVO();
        BeanUtil.copyProperties(app, appVO);
        Long userId = app.getUserId();
        if (userId != null) {
            User user = userService.getById(userId);
            UserVO userVO = userService.getUserVO(user);
            appVO.setUser(userVO);
        }
        return appVO;
    }

    @Override
    public QueryWrapper getQueryWrapper(AppQueryRequest appQueryRequest) {
        if (appQueryRequest == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "请求参数为空");
        }
        Long id = appQueryRequest.getId();
        String appName = appQueryRequest.getAppName();
        String cover = appQueryRequest.getCover();
        String initPrompt = appQueryRequest.getInitPrompt();
        String codeGenType = appQueryRequest.getCodeGenType();
        String deployKey = appQueryRequest.getDeployKey();
        Integer priority = appQueryRequest.getPriority();
        Long userId = appQueryRequest.getUserId();
        String sortField = appQueryRequest.getSortField();
        String sortOrder = appQueryRequest.getSortOrder();
        return QueryWrapper.create()
                .eq("id", id)
                .like("appName", appName)
                .like("cover", cover)
                .like("initPrompt", initPrompt)
                .eq("codeGenType", codeGenType)
                .eq("deployKey", deployKey)
                .eq("priority", priority)
                .eq("userId", userId)
                .orderBy(sortField, "ascend".equals(sortOrder));
    }

    @Override
    public List<AppVO> getAppVOList(List<App> appList) {
        if (CollUtil.isEmpty(appList)) {
            return new ArrayList<>();
        }
        Set<Long> userIds = appList.stream()
                .map(App::getUserId)
                .collect(Collectors.toSet());
        Map<Long, UserVO> userVOMap = userService.listByIds(userIds).stream()
                .collect(Collectors.toMap(User::getId, userService::getUserVO));
        return appList.stream().map(app -> {
            AppVO appVO = getAppVO(app);
            UserVO userVO = userVOMap.get(app.getUserId());
            appVO.setUser(userVO);
            return appVO;
        }).collect(Collectors.toList());
    }

    @Override
    public Flux<String> chatToGenCode(Long appId, String message, User loginUser) {
        // 1. 参数校验
        ThrowUtils.throwIf(appId == null || appId < 0, ErrorCode.PARAMS_ERROR, "应用Id错误");
        ThrowUtils.throwIf(StrUtil.isBlank(message), ErrorCode.PARAMS_ERROR, "提示词不能为空");

        // 2. 查询应用信息
        App app = this.getById(appId);
        ThrowUtils.throwIf(app == null, ErrorCode.PARAMS_ERROR, "应用不存在");

        // 3. 权限校验
        if (!app.getUserId().equals(loginUser.getId())) {
            throw new BusinessException(ErrorCode.NO_AUTH_ERROR, "无权限访问应用");
        }

        // 4. 获取代码生成类型
        String codeGenTypeStr = app.getCodeGenType();
        CodeGenTypeEnum codeGenTypeEnum = CodeGenTypeEnum.getEnumByValue(codeGenTypeStr);
        if (codeGenTypeEnum == null) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "不支持的代码生成类型");
        }

        // 5. 记录用户消息到历史
        chatHistoryService.addChatMessage(appId, message, ChatHistoryMessageTypeEnum.USER.getValue(), loginUser.getId());

        // 6. 调用 Agent 工作流 (替换原本的 Facade 调用)
        // 注意：executeWorkflowWithFlux 方法签名已在第一阶段修改，支持传入 appId, message, user, type
        Flux<String> workflowFlux = codeGenWorkflow.executeWorkflowWithFlux(appId, message, loginUser, codeGenTypeEnum);

        // 7. 适配流输出并处理历史记录保存
        return workflowFlux
                .map(this::workflowStreamAdapter) // 适配器：将 SSE 事件转为前端友好的文本
                .doOnComplete(() -> {
                    // 工作流结束后，保存一条系统消息表示完成
                    String finishMsg = "代码生成流程执行完毕。";
                    chatHistoryService.addChatMessage(appId, finishMsg, ChatHistoryMessageTypeEnum.AI.getValue(), loginUser.getId());
                })
                .doOnError(e -> {
                    log.error("Agent 工作流执行异常", e);
                    chatHistoryService.addChatMessage(appId, "系统异常：" + e.getMessage(), ChatHistoryMessageTypeEnum.AI.getValue(), loginUser.getId());
                });
    }

    /**
     * 工作流流式转换适配器
     * 将 LangGraph 的 SSE 事件转换为前端可读的文本提示
     */
    private String workflowStreamAdapter(String sseEvent) {
        // sseEvent 格式示例:
        // event: step_completed
        // data: {"currentStep":"图片收集", "stepNumber":1}

        try {
            // 简单解析，提取 data 部分的 JSON
            if (StrUtil.isBlank(sseEvent) || !sseEvent.contains("data:")) {
                return "";
            }

            String[] lines = sseEvent.split("\n");
            String eventType = "";
            String jsonStr = "";

            for (String line : lines) {
                if (line.startsWith("event:")) {
                    eventType = line.substring(6).trim();
                } else if (line.startsWith("data:")) {
                    jsonStr = line.substring(5).trim();
                }
            }

            if (StrUtil.isBlank(jsonStr)) return "";

            JSONObject data = JSONUtil.parseObj(jsonStr);

            // 根据事件类型生成对用户友好的提示
            if ("workflow_start".equals(eventType)) {
                return "🚀 收到需求，Agent 智能体已启动...\n";
            } else if ("step_completed".equals(eventType)) {
                String stepName = data.getStr("currentStep");
                // 可以在这里加一些 emoji 让过程更生动
                return switch (stepName) {
                    case "图片收集" -> "🖼️ 素材收集完成，已保存到项目目录。\n";
                    case "提示词增强" -> "✨ 需求分析与提示词优化完成。\n";
                    case "智能路由" -> "🧠 已规划最佳代码生成路径。\n";
                    case "代码生成" -> "💻 代码编写与文件写入完成。\n";
                    case "质量检查" -> "✅ 代码质量检测通过。\n";
                    case "项目构建" -> "🔨 项目编译构建完成。\n";
                    default -> "➡️ 步骤完成: " + stepName + "\n";
                };
            } else if ("workflow_completed".equals(eventType)) {
                return "\n✨ 所有工作流执行完毕！\n";
            } else if ("workflow_error".equals(eventType)) {
                return "❌ 执行出错: " + data.getStr("error") + "\n";
            }

            return ""; // 忽略其他未知事件
        } catch (Exception e) {
            // 解析失败直接忽略，避免破坏流
            return "";
        }
    }

    @Override
    public String deployApp(Long appId, User loginUser) {
        // ... (保持原有逻辑)
        ThrowUtils.throwIf(appId == null || appId <= 0, ErrorCode.PARAMS_ERROR, "应用 ID 不能为空");
        ThrowUtils.throwIf(loginUser == null, ErrorCode.NOT_LOGIN_ERROR, "用户未登录");
        App app = this.getById(appId);
        ThrowUtils.throwIf(app == null, ErrorCode.NOT_FOUND_ERROR, "应用不存在");
        if (!app.getUserId().equals(loginUser.getId())) {
            throw new BusinessException(ErrorCode.NO_AUTH_ERROR, "无权限部署该应用");
        }
        String deployKey = app.getDeployKey();
        if (StrUtil.isBlank(deployKey)) {
            deployKey = RandomUtil.randomString(6);
        }
        String codeGenType = app.getCodeGenType();
        String sourceDirName = codeGenType + "_" + appId;
        String sourceDirPath = AppConstant.CODE_OUTPUT_ROOT_DIR + File.separator + sourceDirName;
        File sourceDir = new File(sourceDirPath);
        if (!sourceDir.exists() || !sourceDir.isDirectory()) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "应用代码不存在，请先生成代码");
        }
        // Vue 项目特殊处理
        CodeGenTypeEnum codeGenTypeEnum = CodeGenTypeEnum.getEnumByValue(codeGenType);
        if (codeGenTypeEnum == CodeGenTypeEnum.VUE_PROJECT) {
            File distDir = new File(sourceDirPath, "dist");
            if (!distDir.exists()) {
                boolean buildSuccess = vueProjectBuilder.buildProject(sourceDirPath);
                ThrowUtils.throwIf(!buildSuccess, ErrorCode.SYSTEM_ERROR, "Vue 项目构建失败");
            }
            sourceDir = distDir;
        }
        String deployDirPath = AppConstant.CODE_DEPLOY_ROOT_DIR + File.separator + deployKey;
        try {
            FileUtil.copyContent(sourceDir, new File(deployDirPath), true);
        } catch (Exception e) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "部署失败：" + e.getMessage());
        }
        App updateApp = new App();
        updateApp.setId(appId);
        updateApp.setDeployKey(deployKey);
        updateApp.setDeployedTime(LocalDateTime.now());
        boolean updateResult = this.updateById(updateApp);
        ThrowUtils.throwIf(!updateResult, ErrorCode.OPERATION_ERROR, "更新应用部署信息失败");
        String appDeployUrl = String.format("%s/%s/", AppConstant.CODE_DEPLOY_HOST, deployKey);
        generateAppScreenshotAsync(appId, appDeployUrl);
        return appDeployUrl;
    }

    @Override
    public void generateAppScreenshotAsync(Long appId, String appUrl) {
        // ... (保持原有逻辑)
        Thread.startVirtualThread(() -> {
            String screenshotUrl = screenshotService.generateAndUploadScreenshot(appUrl);
            App updateApp = new App();
            updateApp.setId(appId);
            updateApp.setCover(screenshotUrl);
            boolean updated = this.updateById(updateApp);
            ThrowUtils.throwIf(!updated, ErrorCode.OPERATION_ERROR, "更新应用封面字段失败");
        });
    }

    @Override
    public boolean removeById(Serializable id) {
        if (id == null) {
            return false;
        }
        Long appId = Long.valueOf(id.toString());
        if (appId <= 0) {
            return false;
        }
        try {
            chatHistoryService.deleteByAppId(appId);
        } catch (Exception e) {
            log.error("删除应用关联对话历史失败: {}", e.getMessage());
        }
        return super.removeById(id);
    }
}
