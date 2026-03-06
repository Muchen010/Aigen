"""
LangGraph 状态图定义 - 代码生成工作流

对应 Java 端: CodeGenWorkflow.java

Phase 2 实现: 所有节点均已接入真实 LLM 调用和工具调用逻辑。
图拓扑结构与 Java 端完全对应。
"""

from langgraph.graph import END, StateGraph

from app.graph.nodes.code_generator import code_generator_node
from app.graph.nodes.image_collector import image_collector_node
from app.graph.nodes.knowledge_retrieval import knowledge_retrieval_node
from app.graph.nodes.project_builder import project_builder_node
from app.graph.nodes.prompt_enhancer import prompt_enhancer_node
from app.graph.nodes.quality_check import quality_check_node
from app.graph.nodes.router import router_node
from app.graph.state import AgentState


def route_after_quality_check(state: AgentState) -> str:
    """
    质量检查后的条件路由。

    对应 Java 端: CodeGenWorkflow.routeAfterQualityCheck()

    路由逻辑:
        - "build"       → 质检通过，需要 npm 构建 (vue_project)
        - "skip_build"  → 质检通过，无需构建 (html / multi_file)
        - "fail"        → 质检失败，重新生成代码（最多 3 次）

    返回:
        下一个节点的标识符
    """
    quality_result = state.get("quality_result")

    # 质检失败，尝试重新生成
    if not quality_result or not quality_result.get("is_valid"):
        retry_count = state.get("retry_count", 0)
        if retry_count >= 3:
            # 超过最大重试次数，强制通过，防止无限循环
            return "skip_build"
        return "fail"

    # 质检通过，根据项目类型决定是否需要构建
    generation_type = state.get("generation_type", "html")
    if generation_type == "vue_project":
        return "build"
    return "skip_build"


def build_workflow() -> StateGraph:
    """
    构建完整的代码生成工作流图。

    对应 Java 端: CodeGenWorkflow.createWorkflow()

    图拓扑结构:

        START → image_collector → prompt_enhancer → router
              → knowledge_retrieval → code_generator → quality_check
              → [条件路由]
                  ├── "build"      → project_builder → END
                  ├── "skip_build" → END
                  └── "fail"       → code_generator (重试)
    """
    graph = StateGraph(AgentState)

    # ==================== 添加节点 ====================
    graph.add_node("image_collector", image_collector_node)
    graph.add_node("prompt_enhancer", prompt_enhancer_node)
    graph.add_node("router", router_node)
    graph.add_node("knowledge_retrieval", knowledge_retrieval_node)
    graph.add_node("code_generator", code_generator_node)
    graph.add_node("quality_check", quality_check_node)
    graph.add_node("project_builder", project_builder_node)

    # ==================== 线性边 (按执行顺序) ====================
    graph.set_entry_point("image_collector")
    graph.add_edge("image_collector", "prompt_enhancer")
    graph.add_edge("prompt_enhancer", "router")
    graph.add_edge("router", "knowledge_retrieval")
    graph.add_edge("knowledge_retrieval", "code_generator")
    graph.add_edge("code_generator", "quality_check")

    # ==================== 条件边: 质量检查后的分支路由 ====================
    graph.add_conditional_edges(
        "quality_check",
        route_after_quality_check,
        {
            "build": "project_builder",    # 质检通过 → 构建 Vue 项目
            "skip_build": END,             # 质检通过 → 直接结束
            "fail": "code_generator",      # 质检失败 → 重新生成
        },
    )

    graph.add_edge("project_builder", END)

    return graph.compile()
