"""
LLM 服务模块 - DashScope / OpenAI 兼容协议的大模型管理

对应 Java 端: ReasoningStreamingChatModelConfig.java

提供统一的 LLM 客户端，支持：
  - 通用对话 (流式/非流式)
  - 低温推理 (用于路由决策、质量检查等需要确定性输出的场景)
  - 结构化输出 (with_structured_output)
"""

from langchain_openai import ChatOpenAI

from app.config import settings


def get_chat_llm(
    model: str | None = None,
    temperature: float = 0.7,
    streaming: bool = True,
) -> ChatOpenAI:
    """
    获取通用对话 LLM 实例。

    使用 DashScope 的 OpenAI 兼容端点，可直接使用 langchain-openai
    全套工具链（tool calling、structured output 等）。

    参数:
        model: 模型名称覆盖，默认使用 settings.DASHSCOPE_MODEL
        temperature: 采样温度，越高越有创造性
        streaming: 是否启用流式响应

    返回:
        配置好的 ChatOpenAI 实例
    """
    return ChatOpenAI(
        model=model or settings.DASHSCOPE_MODEL,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.DASHSCOPE_BASE_URL,
        temperature=temperature,
        streaming=streaming,
    )


def get_reasoning_llm(
    model: str | None = None,
    streaming: bool = True,
) -> ChatOpenAI:
    """
    获取推理专用 LLM 实例。

    使用较低的温度以获得更确定性的输出，
    适用于代码质量检查、智能路由决策等场景。

    参数:
        model: 模型名称覆盖
        streaming: 是否启用流式响应

    返回:
        低温配置的 ChatOpenAI 实例
    """
    return ChatOpenAI(
        model=model or settings.DASHSCOPE_MODEL,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.DASHSCOPE_BASE_URL,
        temperature=0.1,
        streaming=streaming,
    )


def get_code_gen_llm(
    model: str | None = None,
) -> ChatOpenAI:
    """
    获取代码生成专用 LLM 实例。

    使用中等温度，平衡创造性与准确性，
    专门用于 CodeGeneratorNode 中的代码生成任务。

    参数:
        model: 模型名称覆盖

    返回:
        代码生成优化配置的 ChatOpenAI 实例
    """
    return ChatOpenAI(
        model=model or settings.DASHSCOPE_MODEL,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.DASHSCOPE_BASE_URL,
        temperature=0.3,
        streaming=True,
    )
