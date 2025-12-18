package org.muchen.aigen.controller;

import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.muchen.aigen.langgraph4j.CodeGenWorkflow;
import org.muchen.aigen.langgraph4j.state.WorkflowContext;
import org.muchen.aigen.model.entity.User;
import org.muchen.aigen.model.enums.CodeGenTypeEnum;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

/**
 * 工作流 SSE 控制器
 * 演示 LangGraph4j 工作流的流式输出功能
 */
@Deprecated
@RestController
@RequestMapping("/workflow")
@Slf4j
public class WorkflowSseController {

    @Resource
    private CodeGenWorkflow codeGenWorkflow;

    /**
     * Flux 流式执行工作流 (测试接口)
     * 使用模拟的 AppId 和 User 进行测试
     */
    @GetMapping(value = "/execute-flux", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> executeWorkflowWithFlux(@RequestParam String prompt) {
        log.info("收到 Flux 工作流测试请求: {}", prompt);

        // 构造模拟数据
        Long mockAppId = 99999L; // 测试用的虚拟 ID
        User mockUser = new User();
        mockUser.setId(1L);
        mockUser.setUserRole("admin");

        // 默认测试 HTML 生成，或者根据 prompt 简单判断
        CodeGenTypeEnum mockType = CodeGenTypeEnum.HTML;

        // 调用更新后的工作流接口
        return codeGenWorkflow.executeWorkflowWithFlux(mockAppId, prompt, mockUser, mockType);
    }

    /**
     * 同步执行工作流 (已废弃，简单返回空或抛错，或者同样适配新接口)
     */
    @PostMapping("/execute")
    public WorkflowContext executeWorkflow(@RequestParam String prompt) {
        throw new UnsupportedOperationException("同步接口已停用，请使用流式接口 /execute-flux 或通过应用界面访问");
    }
}
