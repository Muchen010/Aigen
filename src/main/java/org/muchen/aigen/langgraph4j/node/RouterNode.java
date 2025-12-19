package org.muchen.aigen.langgraph4j.node;

import lombok.extern.slf4j.Slf4j;
import org.bsc.langgraph4j.action.AsyncNodeAction;
import org.bsc.langgraph4j.prebuilt.MessagesState;
import org.muchen.aigen.ai.AiCodeGenTypeRoutingService;
import org.muchen.aigen.langgraph4j.state.WorkflowContext;
import org.muchen.aigen.langgraph4j.utils.SpringContextUtil;
import org.muchen.aigen.model.enums.CodeGenTypeEnum;

import static org.bsc.langgraph4j.action.AsyncNodeAction.node_async;

@Slf4j
public class RouterNode {

    public static AsyncNodeAction<MessagesState<String>> create() {
        return node_async(state -> {
            WorkflowContext context = WorkflowContext.getContext(state);
            log.info("执行节点: 智能路由");

            CodeGenTypeEnum generationType = context.getGenerationType();

            // 1. 如果 Context 中已经预设了类型，直接使用
            if (generationType != null) {
                log.info("使用上下文预设的代码生成类型: {} ({})", generationType.getValue(), generationType.getText());
            } else {
                // 2. 否则调用 AI 进行判断
                try {
                    AiCodeGenTypeRoutingService routingService = SpringContextUtil.getBean(AiCodeGenTypeRoutingService.class);
                    generationType = routingService.routeCodeGenType(context.getOriginalPrompt());
                    log.info("AI智能路由完成，选择类型: {} ({})", generationType.getValue(), generationType.getText());
                } catch (Exception e) {
                    log.error("AI智能路由失败，使用默认HTML类型: {}", e.getMessage());
                    generationType = CodeGenTypeEnum.HTML;
                }
            }

            // 更新状态
            context.setCurrentStep("智能路由");
            context.setGenerationType(generationType);
            return WorkflowContext.saveContext(context);
        });
    }
}