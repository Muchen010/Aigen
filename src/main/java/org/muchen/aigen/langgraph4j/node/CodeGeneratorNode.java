package org.muchen.aigen.langgraph4j.node;

import lombok.extern.slf4j.Slf4j;
import org.bsc.langgraph4j.action.AsyncNodeAction;
import org.bsc.langgraph4j.prebuilt.MessagesState;
import org.muchen.aigen.constant.AppConstant;
import org.muchen.aigen.core.AiCodeGeneratorFacade;
import org.muchen.aigen.langgraph4j.model.QualityResult;
import org.muchen.aigen.langgraph4j.state.WorkflowContext;
import org.muchen.aigen.langgraph4j.utils.SpringContextUtil;
import org.muchen.aigen.model.enums.CodeGenTypeEnum;
import reactor.core.publisher.Flux;

import java.io.File;
import java.time.Duration;

import static org.bsc.langgraph4j.action.AsyncNodeAction.node_async;

@Slf4j
public class CodeGeneratorNode {

    public static AsyncNodeAction<MessagesState<String>> create() {
        return node_async(state -> {
            WorkflowContext context = WorkflowContext.getContext(state);
            log.info("执行节点: 代码生成");

            // 1. 准备参数
            String userMessage = buildUserMessage(context); // 使用抽取的方法构建消息（包含质检修复逻辑）
            CodeGenTypeEnum generationType = context.getGenerationType();
            Long appId = context.getAppId();

            // 2. 获取服务并生成
            AiCodeGeneratorFacade codeGeneratorFacade = SpringContextUtil.getBean(AiCodeGeneratorFacade.class);
            log.info("开始生成代码，AppId: {}, 类型: {}", appId, generationType.getValue());

            // 3. 调用流式生成 (Facade 内部会调用 Saver 将代码写入到 AppConstant.CODE_OUTPUT_ROOT_DIR + type_appId)
            Flux<String> codeStream = codeGeneratorFacade.generateAndSaveCodeStream(userMessage, generationType, appId);

            // 4. 等待生成完成 (注意：生产环境可能需要更复杂的超时处理)
            codeStream.blockLast(Duration.ofMinutes(10));

            // 5. 计算生成目录路径 (必须与 CodeFileSaverExecutor 中的逻辑保持一致)
            // 路径格式: /root/dir/type_appId
            String sourceDirName = generationType.getValue() + "_" + appId;
            String generatedCodeDir = AppConstant.CODE_OUTPUT_ROOT_DIR + File.separator + sourceDirName;

            log.info("AI 代码生成完成，生成目录: {}", generatedCodeDir);

            // 更新状态
            context.setCurrentStep("代码生成");
            context.setGeneratedCodeDir(generatedCodeDir);
            return WorkflowContext.saveContext(context);
        });
    }

    /**
     * 构造用户消息，如果存在质检失败结果则添加错误修复信息
     */
    private static String buildUserMessage(WorkflowContext context) {
        String userMessage = context.getEnhancedPrompt();
        // 检查是否存在质检失败结果
        QualityResult qualityResult = context.getQualityResult();
        if (isQualityCheckFailed(qualityResult)) {
            // 直接将错误修复信息作为新的提示词（起到了修改的作用）
            userMessage = buildErrorFixPrompt(qualityResult);
        }
        return userMessage;
    }

    /**
     * 判断质检是否失败
     */
    private static boolean isQualityCheckFailed(QualityResult qualityResult) {
        return qualityResult != null &&
                !qualityResult.getIsValid() &&
                qualityResult.getErrors() != null &&
                !qualityResult.getErrors().isEmpty();
    }

    /**
     * 构造错误修复提示词
     */
    private static String buildErrorFixPrompt(QualityResult qualityResult) {
        StringBuilder errorInfo = new StringBuilder();
        errorInfo.append("\n\n## 上次生成的代码存在以下问题，请修复：\n");
        // 添加错误列表
        qualityResult.getErrors().forEach(error ->
                errorInfo.append("- ").append(error).append("\n"));
        // 添加修复建议（如果有）
        if (qualityResult.getSuggestions() != null && !qualityResult.getSuggestions().isEmpty()) {
            errorInfo.append("\n## 修复建议：\n");
            qualityResult.getSuggestions().forEach(suggestion ->
                    errorInfo.append("- ").append(suggestion).append("\n"));
        }
        errorInfo.append("\n请根据上述问题和建议重新生成代码，确保修复所有提到的问题。");
        return errorInfo.toString();
    }

}
