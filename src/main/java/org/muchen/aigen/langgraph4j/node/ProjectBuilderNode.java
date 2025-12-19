package org.muchen.aigen.langgraph4j.node;

import lombok.extern.slf4j.Slf4j;
import org.bsc.langgraph4j.action.AsyncNodeAction;
import org.bsc.langgraph4j.prebuilt.MessagesState;
import org.muchen.aigen.core.builder.VueProjectBuilder;
import org.muchen.aigen.exception.BusinessException;
import org.muchen.aigen.exception.ErrorCode;
import org.muchen.aigen.langgraph4j.state.WorkflowContext;
import org.muchen.aigen.langgraph4j.utils.SpringContextUtil;

import java.io.File;

import static org.bsc.langgraph4j.action.AsyncNodeAction.node_async;

@Slf4j
public class ProjectBuilderNode {

    public static AsyncNodeAction<MessagesState<String>> create() {
        return node_async(state -> {
            WorkflowContext context = WorkflowContext.getContext(state);
            log.info("执行节点: 项目构建");

            String generatedCodeDir = context.getGeneratedCodeDir();
            if (generatedCodeDir == null) {
                throw new BusinessException(ErrorCode.SYSTEM_ERROR, "构建失败：找不到生成的代码目录");
            }

            String buildResultDir = generatedCodeDir;

            try {
                VueProjectBuilder vueBuilder = SpringContextUtil.getBean(VueProjectBuilder.class);
                File packageJson = new File(generatedCodeDir, "package.json");
                if (packageJson.exists()) {
                    log.info("检测到 Vue 项目，开始执行构建...");
                    boolean buildSuccess = vueBuilder.buildProject(generatedCodeDir);
                    if (buildSuccess) {
                        buildResultDir = generatedCodeDir + File.separator + "dist";
                        log.info("Vue 项目构建成功，dist 目录: {}", buildResultDir);
                    } else {
                        throw new BusinessException(ErrorCode.SYSTEM_ERROR, "Vue 项目构建失败");
                    }
                } else {
                    log.info("非 Vue 项目或未找到 package.json，跳过构建步骤");
                }
            } catch (Exception e) {
                log.error("项目构建异常: {}", e.getMessage(), e);
            }

            // 更新状态
            context.setCurrentStep("项目构建");
            context.setBuildResultDir(buildResultDir);
            return WorkflowContext.saveContext(context);
        });
    }
}