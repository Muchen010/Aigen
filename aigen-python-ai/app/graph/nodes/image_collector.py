"""
素材收集节点 - 并发收集网站所需的图片资源

对应 Java 端: ImageCollectorNode.java

工作流程:
1. 调用 LLM 分析用户需求，生成图片收集计划
2. 并发调用 Pexels / Undraw / DashScope / Mermaid 工具收集素材
3. 将收集到的图片列表写入 AgentState
"""

import asyncio
import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.state import AgentState
from app.services.llm_service import get_reasoning_llm
from app.tools.image_tools import generate_logo, generate_mermaid_diagram, search_illustrations, search_images

logger = logging.getLogger(__name__)


async def image_collector_node(state: AgentState) -> dict:
    """
    素材收集节点。

    对应 Java: ImageCollectorNode.create()

    步骤:
        1. LLM 分析需求，生成图片收集计划（需要哪些类型的图片）
        2. 并发执行 Pexels 搜索 + Undraw 搜索（Logo 和 Mermaid 按需调用）
        3. 汇总结果写入 state.collected_images
    """
    original_prompt = state.get("original_prompt", "")
    logger.info("[ImageCollector] 开始收集素材，原始需求: %s...", original_prompt[:50])

    collected_images: list[dict] = []

    try:
        # ==================== 第一步: LLM 生成图片收集计划 ====================
        plan_llm = get_reasoning_llm(streaming=False)
        plan_messages = [
            SystemMessage(content=(
                "你是一个图片素材规划专家。\n"
                "请根据用户的网站需求，分析需要哪些类型的图片素材，以 JSON 格式输出收集计划。\n"
                "JSON 格式如下：\n"
                "{\n"
                '  "content_queries": ["英文关键词1", "英文关键词2"],  // Pexels 搜索词（1-3个）\n'
                '  "illustration_queries": ["英文关键词1"],           // Undraw 搜索词（0-2个）\n'
                '  "need_logo": true,                               // 是否需要 Logo\n'
                '  "logo_description": "Logo 描述",                 // 如果需要 Logo\n'
                '  "need_diagram": false,                           // 是否需要架构图\n'
                '  "mermaid_code": "",                              // 如果需要架构图，填写 Mermaid 代码\n'
                '  "diagram_description": ""                        // 架构图描述\n'
                "}\n"
                "注意：content_queries 使用英文以获得更好的搜索效果。"
                "如果需求非常简单（如纯文本页面），所有查询可以为空数组。"
            )),
            HumanMessage(content=f"用户网站需求：{original_prompt}"),
        ]

        plan_response = await plan_llm.ainvoke(plan_messages)
        plan_text = plan_response.content.strip()

        # 解析 JSON 计划（兼容 markdown 代码块）
        if "```json" in plan_text:
            plan_text = plan_text.split("```json")[1].split("```")[0].strip()
        elif "```" in plan_text:
            plan_text = plan_text.split("```")[1].split("```")[0].strip()

        plan = json.loads(plan_text)
        logger.info("[ImageCollector] 图片收集计划: %s", plan)

        # ==================== 第二步: 并发执行图片收集任务 ====================
        tasks = []

        # Pexels 内容图片搜索
        for query in plan.get("content_queries", []):
            tasks.append(_search_pexels(query))

        # Undraw 插画搜索
        for query in plan.get("illustration_queries", []):
            tasks.append(_search_undraw(query))

        # Logo 生成（如果需要）
        if plan.get("need_logo") and plan.get("logo_description"):
            tasks.append(_generate_logo_async(plan["logo_description"]))

        # Mermaid 架构图（如果需要）
        if plan.get("need_diagram") and plan.get("mermaid_code"):
            tasks.append(_generate_diagram_async(
                plan["mermaid_code"],
                plan.get("diagram_description", "架构图")
            ))

        # 并发等待所有任务（对应 Java 的 CompletableFuture.allOf）
        if tasks:
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results_list:
                if isinstance(result, list):
                    collected_images.extend(result)
                elif result and not isinstance(result, Exception):
                    collected_images.append(result)

        logger.info("[ImageCollector] 并发收集完成，共收集 %d 张图片", len(collected_images))

    except json.JSONDecodeError as e:
        # JSON 解析失败，尝试基本的 Pexels 搜索
        logger.warning("[ImageCollector] 计划解析失败，降级为基本搜索: %s", e)
        try:
            result_str = await asyncio.get_event_loop().run_in_executor(
                None, lambda: search_images.invoke({"query": original_prompt[:50], "count": 6})
            )
            result = json.loads(result_str)
            if isinstance(result, list):
                collected_images.extend(result)
        except Exception:
            pass
    except Exception as e:
        logger.error("[ImageCollector] 素材收集异常: %s", e, exc_info=True)

    return {
        "current_step": "image_collector",
        "collected_images": collected_images,
    }


async def _search_pexels(query: str) -> list[dict]:
    """异步调用 Pexels 图片搜索工具。"""
    try:
        loop = asyncio.get_event_loop()
        result_str = await loop.run_in_executor(
            None, lambda: search_images.invoke({"query": query, "count": 6})
        )
        result = json.loads(result_str)
        return result if isinstance(result, list) else []
    except Exception as e:
        logger.warning("[ImageCollector] Pexels 搜索失败 (query=%s): %s", query, e)
        return []


async def _search_undraw(query: str) -> list[dict]:
    """异步调用 Undraw 插画搜索工具。"""
    try:
        loop = asyncio.get_event_loop()
        result_str = await loop.run_in_executor(
            None, lambda: search_illustrations.invoke({"query": query, "count": 6})
        )
        result = json.loads(result_str)
        return result if isinstance(result, list) else []
    except Exception as e:
        logger.warning("[ImageCollector] Undraw 搜索失败 (query=%s): %s", query, e)
        return []


async def _generate_logo_async(description: str) -> dict | None:
    """异步调用 Logo 生成工具。"""
    try:
        loop = asyncio.get_event_loop()
        result_str = await loop.run_in_executor(
            None, lambda: generate_logo.invoke({"description": description})
        )
        result = json.loads(result_str)
        if isinstance(result, list) and result:
            return result[0]
        return None
    except Exception as e:
        logger.warning("[ImageCollector] Logo 生成失败: %s", e)
        return None


async def _generate_diagram_async(mermaid_code: str, description: str) -> dict | None:
    """异步调用 Mermaid 架构图生成工具。"""
    try:
        loop = asyncio.get_event_loop()
        result_str = await loop.run_in_executor(
            None, lambda: generate_mermaid_diagram.invoke({
                "mermaid_code": mermaid_code,
                "description": description,
            })
        )
        result = json.loads(result_str)
        if isinstance(result, dict) and "error" not in result:
            return result
        return None
    except Exception as e:
        logger.warning("[ImageCollector] Mermaid 生成失败: %s", e)
        return None
