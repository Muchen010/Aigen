package org.muchen.aigen.client;

import cn.hutool.core.util.IdUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.Map;

/**
 * Python AI 服务 HTTP 客户端
 *
 * <p>封装所有 Java 端对 Python AI 服务的 HTTP 调用。
 * 替代原有的 CodeGenWorkflow、AiCodeGeneratorFacade 等 Java AI 组件。
 *
 * <p>接口清单:
 * <ul>
 *   <li>GET  /api/v1/ai/workflow/generate  — 触发代码生成工作流 (SSE 流式)</li>
 *   <li>GET  /api/v1/ai/health             — 健康检查</li>
 * </ul>
 */
@Slf4j
@Component
public class PythonAiServiceClient {

    /** Python AI 服务的基础 URL，从 application.yml 读取 */
    @Value("${python.ai.service.url:http://127.0.0.1:8100}")
    private String pythonAiServiceUrl;

    /** 服务间内部通讯密钥，Python 端用于验证请求来源 */
    @Value("${python.ai.service.internal-secret:}")
    private String internalSecret;

    /**
     * 触发代码生成工作流，以 SSE 流形式转发 Python AI 服务的输出。
     *
     * <p>该方法将 Python 端的 SSE 事件流直接转发到前端，
     * Java 端本身不解析 SSE 内容，只充当代理层。
     *
     * @param appId          应用 ID
     * @param userId         用户 ID
     * @param prompt         用户提示词
     * @param codeGenType    代码生成类型 (html / multi_file / vue_project)
     * @return               来自 Python AI 服务的 SSE 事件流
     */
    public Flux<String> streamWorkflow(Long appId, Long userId, String prompt, String codeGenType) {
        // 为本次任务生成唯一 taskId
        String taskId = IdUtil.fastSimpleUUID();

        log.info("[PythonAiClient] 触发工作流，AppId: {}, TaskId: {}, Type: {}", appId, taskId, codeGenType);

        WebClient client = buildWebClient();

        return client.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/api/v1/ai/workflow/generate")
                        .queryParam("task_id", taskId)
                        .queryParam("app_id", appId)
                        .queryParam("user_id", userId)
                        .queryParam("prompt", prompt)
                        .queryParam("code_gen_type", codeGenType)
                        .build())
                .retrieve()
                // 将 text/event-stream 响应解析为字符串流
                .bodyToFlux(String.class)
                .timeout(Duration.ofMinutes(10))
                .doOnError(e -> log.error("[PythonAiClient] 工作流流式调用异常: {}", e.getMessage(), e))
                .onErrorResume(e -> Flux.just("data: {\"event\":\"workflow_error\",\"message\":\"" + e.getMessage() + "\"}\n\n"));
    }

    /**
     * 健康检查：确认 Python AI 服务是否可用。
     *
     * @return 若服务健康返回 true，否则返回 false
     */
    public boolean healthCheck() {
        try {
            WebClient client = buildWebClient();
            Map<?, ?> response = client.get()
                    .uri("/api/v1/ai/health")
                    .retrieve()
                    .bodyToMono(new ParameterizedTypeReference<Map<?, ?>>() {})
                    .timeout(Duration.ofSeconds(5))
                    .block();
            return response != null && "ok".equals(response.get("status"));
        } catch (Exception e) {
            log.warn("[PythonAiClient] 健康检查失败: {}", e.getMessage());
            return false;
        }
    }

    /**
     * 构建配置了内部认证 Header 的 WebClient 实例。
     */
    private WebClient buildWebClient() {
        WebClient.Builder builder = WebClient.builder()
                .baseUrl(pythonAiServiceUrl)
                // 设置较大的 buffer 以支持长 SSE 流
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(10 * 1024 * 1024));

        // 注入服务间内部密钥（若已配置）
        if (internalSecret != null && !internalSecret.isBlank()) {
            builder.defaultHeader("X-Internal-Secret", internalSecret);
        }

        return builder.build();
    }
}
