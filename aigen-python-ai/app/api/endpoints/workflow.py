"""
工作流 SSE 端点 - AI 代码生成流式接口 (Phase 2 完整实现)

对应 Java 端: AppController.chatToGenCode() → PythonAiServiceClient.streamWorkflow()

本端点接收 Java 服务的调用，启动 LangGraph StateGraph 工作流，
通过 SSE 流实时将每个节点的执行状态推送给 Java 端（再由 Java 转发给前端）。

SSE 事件格式（与 Java PythonAiServiceClient 解析格式一致）:
  event: workflow_start       → 工作流启动
  event: step_start           → 节点开始执行
  event: step_completed       → 节点执行完成
  event: code_chunk           → 代码流式输出 token
  event: workflow_completed   → 工作流完成
  event: workflow_error       → 工作流异常
"""

import json
import logging

from fastapi import APIRouter, Depends, Query
from sse_starlette.sse import EventSourceResponse

from app.api.deps import verify_internal_token
from app.graph.state import AgentState
from app.graph.workflow import build_workflow

logger = logging.getLogger(__name__)

router = APIRouter()


def _sse_event(event_type: str, data: dict) -> dict:
    """
    构造标准 SSE 事件格式。

    Java 端的 WebClient 以 `bodyToFlux(String.class)` 接收，
    sse-starlette 会将此格式序列化为标准 text/event-stream 格式：
      event: <event_type>
      data: <json_string>

    参数:
        event_type: 事件类型字符串
        data: 事件数据字典

    返回:
        sse-starlette 可直接使用的事件字典
    """
    return {
        "event": event_type,
        "data": json.dumps(data, ensure_ascii=False),
    }


@router.get("/generate", dependencies=[Depends(verify_internal_token)])
async def generate_code_stream(
    task_id: str = Query(..., description="任务ID (由 Java 端签发)"),
    prompt: str = Query(..., description="用户自然语言需求"),
    code_gen_type: str = Query("html", description="代码生成类型: html / multi_file / vue_project"),
    app_id: int = Query(..., description="应用ID"),
    user_id: int = Query(..., description="用户ID"),
):
    """
    SSE 流式代码生成接口（Phase 2: 完整 LangGraph 工作流）。

    Phase 2 实现:
    - 使用真实的 LangGraph StateGraph 执行完整工作流
    - 每个节点通过状态轮询推送 SSE 事件
    - 全链路接入: 图片收集 → 提示词增强 → 路由 → RAG → 代码生成 → 质检 → 构建

    请求参数由 Java 端 PythonAiServiceClient.streamWorkflow() 传入。
    """
    logger.info(
        "[WorkflowEndpoint] 收到工作流请求 - TaskId: %s, AppId: %s, Type: %s",
        task_id, app_id, code_gen_type
    )

    async def event_generator():
        """
        LangGraph 工作流 SSE 事件生成器。

        使用 astream_events API 逐节点推送进度，同时将代码
        生成 token 流式转发给前端。
        """
        try:
            # ==================== 启动事件 ====================
            yield _sse_event("workflow_start", {
                "message": "Agent 工作流已启动",
                "taskId": task_id,
                "codeGenType": code_gen_type,
                "appId": app_id,
            })

            # ==================== 初始化工作流状态 ====================
            initial_state: AgentState = {
                "messages": [],
                "app_id": app_id,
                "user_id": user_id,
                "generation_type": code_gen_type,
                "original_prompt": prompt,
                "enhanced_prompt": None,
                "current_step": "init",
                "collected_images": None,
                "retrieved_knowledge": None,
                "generated_code_dir": None,
                "build_result_dir": None,
                "quality_result": None,
                "retry_count": 0,
            }

            # ==================== 编译并执行 LangGraph 工作流 ====================
            workflow = build_workflow()

            # 节点名称 → 中文标签映射（对应 Java 端 workflowStreamAdapter 的 case）
            _step_labels = {
                "image_collector": "图片收集",
                "prompt_enhancer": "提示词增强",
                "router": "智能路由",
                "knowledge_retrieval": "知识检索",
                "code_generator": "代码生成",
                "quality_check": "质量检查",
                "project_builder": "项目构建",
            }

            # 使用 astream_events 逐事件监听图的执行（LangGraph API）
            async for event in workflow.astream_events(initial_state, version="v2"):
                event_name = event.get("event", "")
                node_name = event.get("name", "")

                # --- 节点开始执行 ---
                if event_name == "on_chain_start" and node_name in _step_labels:
                    label = _step_labels[node_name]
                    logger.info("[WorkflowEndpoint] 节点开始: %s", node_name)
                    yield _sse_event("step_start", {
                        "currentStep": label,
                        "nodeName": node_name,
                        "message": f"正在执行: {label}...",
                    })

                # --- 节点执行完成 ---
                elif event_name == "on_chain_end" and node_name in _step_labels:
                    label = _step_labels[node_name]
                    output = event.get("data", {}).get("output", {})
                    logger.info("[WorkflowEndpoint] 节点完成: %s", node_name)

                    step_data = {
                        "currentStep": label,
                        "nodeName": node_name,
                        "message": f"{label}完成",
                    }

                    # 附加节点特定信息
                    if node_name == "image_collector":
                        images = output.get("collected_images") or []
                        step_data["imageCount"] = len(images)
                    elif node_name == "router":
                        step_data["codeGenType"] = output.get("generation_type", code_gen_type)
                    elif node_name == "code_generator":
                        step_data["codeDir"] = output.get("generated_code_dir", "")
                    elif node_name == "quality_check":
                        qr = output.get("quality_result") or {}
                        step_data["qualityResult"] = {
                            "is_valid": qr.get("is_valid", True),
                            "score": qr.get("score", 0),
                        }
                    elif node_name == "project_builder":
                        step_data["buildDir"] = output.get("build_result_dir", "")

                    yield _sse_event("step_completed", step_data)

                # --- LLM 流式 token（代码生成节点的 token 流）---
                elif event_name == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        yield _sse_event("code_chunk", {"token": chunk.content})

            # ==================== 工作流完成 ====================
            logger.info("[WorkflowEndpoint] 工作流完成 - TaskId: %s", task_id)
            yield _sse_event("workflow_completed", {
                "message": "代码生成工作流执行完成",
                "taskId": task_id,
            })

        except Exception as e:
            logger.error("[WorkflowEndpoint] 工作流异常: %s", e, exc_info=True)
            yield _sse_event("workflow_error", {
                "error": str(e),
                "message": "工作流执行失败",
                "taskId": task_id,
            })

    return EventSourceResponse(event_generator())


def _build_code_gen_system_prompt(code_gen_type: str) -> str:
    """
    根据代码生成类型构造 System Prompt（兼容旧端点，已被 LangGraph 工作流替代）。

    保留此函数以便手动调试用途。
    """
    base_rules = (
        "你是一个专业的前端代码生成专家。\n"
        "请根据用户需求生成高质量的代码，要求：\n"
        "1. 代码规范、结构清晰、注释完整\n"
        "2. 使用现代化的设计风格（渐变色、圆角、阴影、动画）\n"
        "3. 响应式布局，适配移动端和桌面端\n"
        "4. 代码可直接运行，无需额外配置\n"
    )
    if code_gen_type == "html":
        return base_rules + "5. 生成完整的单页 HTML 文件，包含内联的 CSS 和 JavaScript\n"
    elif code_gen_type == "multi_file":
        return base_rules + "5. 使用 --- FILE: 路径 --- ... --- END FILE --- 格式输出多文件\n"
    elif code_gen_type == "vue_project":
        return base_rules + "5. 生成 Vue 3 + Vite + TypeScript 项目，使用 Composition API\n"
    return base_rules
