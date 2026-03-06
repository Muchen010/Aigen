"""
LLM 对话测试端点

提供简单的对话接口用于验证 DashScope LLM 连通性和流式输出。
此接口仅用于开发调试，不应暴露到生产环境。
"""

import json

from fastapi import APIRouter, Query
from langchain_core.messages import HumanMessage, SystemMessage
from sse_starlette.sse import EventSourceResponse

from app.services.llm_service import get_chat_llm

router = APIRouter()


@router.get("/stream")
async def chat_stream(
    message: str = Query(..., description="用户消息"),
    model: str = Query(None, description="模型名称 (可选，默认使用配置中的模型)"),
):
    """
    流式对话接口 - 验证 DashScope LLM 连通性。

    通过 SSE 逐 token 返回 LLM 的回复，用于测试：
    1. DashScope API Key 是否有效
    2. 流式输出是否正常工作
    3. 模型响应质量
    """

    async def event_generator():
        try:
            # 获取流式 LLM 实例
            llm = get_chat_llm(model=model, streaming=True)

            # 构造消息
            messages = [
                SystemMessage(content="你是 Aigen 智能代码生成助手，擅长前端开发和 Web 应用架构设计。"),
                HumanMessage(content=message),
            ]

            # 流式调用 LLM 并逐 token 返回
            full_response = ""
            async for chunk in llm.astream(messages):
                token = chunk.content
                if token:
                    full_response += token
                    yield {
                        "event": "token",
                        "data": json.dumps({"token": token}, ensure_ascii=False),
                    }

            # 流式完成，发送完整响应摘要
            yield {
                "event": "done",
                "data": json.dumps(
                    {
                        "message": "LLM 流式响应完成",
                        "total_length": len(full_response),
                    },
                    ensure_ascii=False,
                ),
            }

        except Exception as e:
            # 捕获异常并通过 SSE 返回错误信息
            yield {
                "event": "error",
                "data": json.dumps(
                    {"error": str(e), "message": "LLM 调用失败，请检查 API Key 和网络连接"},
                    ensure_ascii=False,
                ),
            }

    return EventSourceResponse(event_generator())


@router.get("/invoke")
async def chat_invoke(
    message: str = Query(..., description="用户消息"),
    model: str = Query(None, description="模型名称 (可选)"),
):
    """
    同步对话接口 - 一次性返回完整 LLM 回复。

    适用于不需要流式输出的场景，例如简单的分类、路由决策等。
    """
    try:
        # 获取非流式 LLM 实例
        llm = get_chat_llm(model=model, streaming=False)

        messages = [
            SystemMessage(content="你是 Aigen 智能代码生成助手，擅长前端开发和 Web 应用架构设计。"),
            HumanMessage(content=message),
        ]

        # 同步调用
        response = await llm.ainvoke(messages)

        return {
            "status": "ok",
            "content": response.content,
            "model": model or "default",
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "LLM 调用失败，请检查 API Key 和网络连接",
        }
