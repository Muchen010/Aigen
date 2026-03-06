"""
提示词增强节点 - 将图片素材信息融合到用户提示词中

对应 Java 端: PromptEnhancerNode.java

将收集到的图片资源 URL 和描述追加到原始提示词中，
使代码生成 LLM 能够将这些图片合理嵌入到生成的页面中。
"""

import logging

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def prompt_enhancer_node(state: AgentState) -> dict:
    """
    提示词增强节点。

    对应 Java: PromptEnhancerNode.create()

    将图片素材信息追加到原始提示词，让代码生成节点能够：
    1. 在正确位置嵌入收集到的图片资源
    2. 使用真实的 URL 而不是占位符

    返回:
        更新 enhanced_prompt 字段的状态字典
    """
    original_prompt = state.get("original_prompt", "")
    collected_images = state.get("collected_images") or []
    logger.info("[PromptEnhancer] 开始增强提示词，已收集 %d 张图片", len(collected_images))

    # 从图片列表构造增强内容（对应 Java 的 imageListStr 拼接逻辑）
    enhanced_prompt = original_prompt

    if collected_images:
        image_block = "\n\n## 可用素材资源\n"
        image_block += "请在生成网站时使用以下图片资源，将这些图片合理地嵌入到网站的相应位置中。\n"

        # 按类型分组展示图片资源
        svg_images = [img for img in collected_images if img.get("svg_content")]
        url_images = [img for img in collected_images if img.get("url") and not img.get("svg_content")]

        # URL 类型图片（Pexels、Undraw SVG 链接、Logo URL）
        for img in url_images:
            category = img.get("category", "content")
            description = img.get("description", "图片")
            url = img.get("url", "")
            if url:
                image_block += f"- {_get_category_label(category)}: {description}（{url}）\n"

        # 内联 SVG 图片（Mermaid 架构图）
        for img in svg_images:
            description = img.get("description", "架构图")
            svg_content = img.get("svg_content", "")
            image_block += (
                f"- 架构图: {description}\n"
                f"  SVG内容（直接嵌入 HTML）:\n"
                f"  {svg_content[:500]}...\n"
            )

        enhanced_prompt = original_prompt + image_block

    logger.info("[PromptEnhancer] 提示词增强完成，增强后长度: %d 字符", len(enhanced_prompt))

    return {
        "current_step": "prompt_enhancer",
        "enhanced_prompt": enhanced_prompt,
    }


def _get_category_label(category: str) -> str:
    """将图片分类转换为中文标签。"""
    labels = {
        "content": "内容图片",
        "illustration": "插画素材",
        "logo": "Logo 图片",
        "architecture": "架构图",
    }
    return labels.get(category, "图片")
