"""
智能路由节点 - 根据用户需求选择最优的代码生成类型

对应 Java 端: RouterNode.java + AiCodeGenTypeRoutingService.java

路由逻辑:
1. 如果 AgentState 中已预设 generation_type，直接使用
2. 否则调用 LLM 分析需求，智能判断最适合的生成类型
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.state import AgentState
from app.models.enums import CodeGenType
from app.services.llm_service import get_reasoning_llm

logger = logging.getLogger(__name__)


async def router_node(state: AgentState) -> dict:
    """
    智能路由节点。

    对应 Java: RouterNode.create() + AiCodeGenTypeRoutingService.routeCodeGenType()

    路由规则:
        - html:         单页 HTML，需求简单，无需构建系统
        - multi_file:   多文件项目（HTML + CSS + JS），需求中等复杂
        - vue_project:  Vue 3 + Vite 项目，需求复杂，需要组件化

    返回:
        更新 generation_type 字段的状态字典
    """
    # 如果已有预设类型，直接使用（对应 Java: context.getGenerationType() != null）
    existing_type = state.get("generation_type", "")
    if existing_type in [t.value for t in CodeGenType]:
        logger.info("[Router] 使用预设的代码生成类型: %s", existing_type)
        return {"current_step": "router"}

    # 调用 LLM 进行智能路由判断（对应 Java: AiCodeGenTypeRoutingService）
    original_prompt = state.get("original_prompt", "")
    logger.info("[Router] 开始 AI 智能路由分析...")

    try:
        routing_llm = get_reasoning_llm(streaming=False)
        messages = [
            SystemMessage(content=(
                "你是一个代码生成类型路由专家。\n"
                "请根据用户的需求，判断最适合的代码生成类型，只输出以下三个值之一：\n\n"
                "- html: 适用场景 - 简单的单页展示、个人主页、活动页、Landing Page\n"
                "- multi_file: 适用场景 - 需要多个文件但不需要构建工具的项目（原生 HTML/CSS/JS）\n"
                "- vue_project: 适用场景 - 复杂的 Web 应用、需要组件化、路由、状态管理的项目\n\n"
                "只输出类型名称，不要有任何其他内容。"
            )),
            HumanMessage(content=f"用户需求：{original_prompt}"),
        ]

        response = await routing_llm.ainvoke(messages)
        routed_type = response.content.strip().lower()

        # 验证路由结果是否合法
        valid_types = [t.value for t in CodeGenType]
        if routed_type not in valid_types:
            logger.warning("[Router] LLM 返回了无效类型 '%s'，降级为 html", routed_type)
            routed_type = CodeGenType.HTML.value

        logger.info("[Router] AI 智能路由完成，选择类型: %s", routed_type)
        return {
            "current_step": "router",
            "generation_type": routed_type,
        }

    except Exception as e:
        # 路由失败，降级为 HTML（对应 Java: catch 块中的 HTML 兜底）
        logger.error("[Router] AI 智能路由失败，降级为 html: %s", e)
        return {
            "current_step": "router",
            "generation_type": CodeGenType.HTML.value,
        }
