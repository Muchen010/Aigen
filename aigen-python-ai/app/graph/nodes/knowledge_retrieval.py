"""
知识检索节点 - RAG 向量检索补充技术上下文

对应 Java 端: KnowledgeRetrievalNode.java

若 RAG 服务未配置，自动跳过此节点，不中断工作流。
检索到的知识片段将在 CodeGeneratorNode 中注入到提示词中。

当前阶段: rag_service.py 为占位实现，暂返回空。
Phase 2 完善: 接入 PGVector / FAISS 等向量数据库。
"""

import logging

from app.graph.state import AgentState
from app.services.rag_service import retrieve_knowledge

logger = logging.getLogger(__name__)

# 最大检索结果数（对应 Java: MAX_RESULTS = 3）
_MAX_RAG_RESULTS = 3
# 最低相似度阈值（对应 Java: MIN_SCORE = 0.7）
_MIN_SCORE = 0.7


async def knowledge_retrieval_node(state: AgentState) -> dict:
    """
    知识检索节点 (RAG)。

    对应 Java: KnowledgeRetrievalNode.create()

    检索策略:
        - 以原始用户需求作为查询文本
        - 从向量知识库中检索最相关的 top-K 文档片段
        - 将结果拼接后存入 state, 供 code_generator 节点注入 Prompt

    安全设计:
        - 若 RAG 服务未启用/异常，降级为空知识块，不中断整体流程
        （对应 Java: catch Bean 获取异常时的 warn + return）
    """
    original_prompt = state.get("original_prompt", "")
    logger.info("[KnowledgeRetrieval] 开始 RAG 知识检索...")

    retrieved_knowledge = ""

    try:
        # 调用 RAG 服务进行语义检索
        results = await retrieve_knowledge(
            query=original_prompt,
            top_k=_MAX_RAG_RESULTS,
        )

        if not results:
            logger.info("[KnowledgeRetrieval] 未检索到相关知识库内容")
        else:
            # 将检索结果拼接为知识块（对应 Java 的 Collectors.joining）
            knowledge_chunks = [item.get("content", "") for item in results if item.get("content")]
            retrieved_knowledge = "\n\n".join(knowledge_chunks)
            logger.info("[KnowledgeRetrieval] 成功检索到 %d 条相关知识", len(knowledge_chunks))

    except Exception as e:
        # 知识检索失败，降级为空（不中断工作流）
        logger.warning("[KnowledgeRetrieval] RAG 检索异常（已降级为普通生成）: %s", e)
        retrieved_knowledge = ""

    return {
        "current_step": "knowledge_retrieval",
        "retrieved_knowledge": retrieved_knowledge,
    }
