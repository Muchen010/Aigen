"""
图片素材工具集 - 收集和生成网站所需的图片资源

对应 Java 端:
  - langgraph4j/tools/ImageSearchTool.java    → search_images (Pexels API)
  - langgraph4j/tools/UndrawIllustrationTool.java → search_illustrations (Undraw)
  - langgraph4j/tools/LogoGeneratorTool.java   → generate_logo (DashScope 文生图)
  - langgraph4j/tools/MermaidDiagramTool.java  → generate_mermaid_diagram (mmdc CLI)
"""

import json
import subprocess
import tempfile
from pathlib import Path

import httpx
from langchain_core.tools import tool

from app.config import settings


@tool
def search_images(query: str, count: int = 12) -> str:
    """
    通过 Pexels API 搜索内容相关的图片，用于网站内容展示。

    对应 Java: ImageSearchTool.searchContentImages()

    参数:
        query: 搜索关键词（建议使用英文以获得更好效果）
        count: 返回图片数量，默认 12 张

    返回:
        JSON 格式的图片列表，每项包含 url 和 description
    """
    if not settings.PEXELS_API_KEY:
        return json.dumps({"error": "未配置 PEXELS_API_KEY，跳过图片搜索"}, ensure_ascii=False)

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": settings.PEXELS_API_KEY},
                params={"query": query, "per_page": min(count, 20), "page": 1},
            )
            response.raise_for_status()
            data = response.json()

        images = [
            {
                "category": "content",
                "description": photo.get("alt", query),
                "url": photo["src"]["medium"],
                "source": "pexels",
            }
            for photo in data.get("photos", [])
        ]
        return json.dumps(images, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Pexels API 调用失败: {e}"}, ensure_ascii=False)


@tool
def search_illustrations(query: str, count: int = 12) -> str:
    """
    通过 Undraw 搜索插画图片，用于网站美化和装饰。

    对应 Java: UndrawIllustrationTool.searchIllustrations()
    Undraw 提供免费的 SVG 插画，风格统一，适合科技类网站。

    参数:
        query: 搜索关键词
        count: 返回插画数量，默认 12 张

    返回:
        JSON 格式的插画列表，每项包含 url 和 description
    """
    try:
        api_url = f"https://undraw.co/_next/data/SNHhDZgzZi3Ah8uuKvVO7/search/{query}.json?term={query}"
        with httpx.Client(timeout=10.0) as client:
            response = client.get(api_url)
            if not response.is_success:
                return json.dumps([], ensure_ascii=False)

        data = response.json()
        page_props = data.get("pageProps", {})
        initial_results = page_props.get("initialResults", [])

        images = [
            {
                "category": "illustration",
                "description": item.get("title", "插画"),
                "url": item.get("media", ""),
                "source": "undraw",
            }
            for item in initial_results[:count]
            if item.get("media")
        ]
        return json.dumps(images, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Undraw 搜索失败: {e}"}, ensure_ascii=False)


@tool
def generate_logo(description: str) -> str:
    """
    调用 DashScope 文生图接口，根据描述生成 Logo 图片。

    对应 Java: LogoGeneratorTool.generateLogos()
    使用通义万象模型生成 512x512 的 Logo 图片。

    参数:
        description: Logo 设计描述，如名称、行业、风格等，尽量详细

    返回:
        JSON 格式的 Logo 图片列表，每项包含 url 和 description
    """
    if not settings.DASHSCOPE_API_KEY:
        return json.dumps({"error": "未配置 DASHSCOPE_API_KEY，跳过 Logo 生成"}, ensure_ascii=False)

    try:
        import dashscope
        from dashscope.aigc.image_synthesis import ImageSynthesis

        dashscope.api_key = settings.DASHSCOPE_API_KEY

        # 构建 Logo 提示词（禁止文字，避免乱码）
        logo_prompt = f"生成 Logo，Logo 中禁止包含任何文字！Logo 介绍：{description}"

        response = ImageSynthesis.call(
            model="wan2.2-t2i-flash",
            prompt=logo_prompt,
            size="512*512",
            n=1,
        )

        images = []
        if response.status_code == 200 and response.output:
            for result in response.output.get("results", []):
                url = result.get("url", "")
                if url:
                    images.append({
                        "category": "logo",
                        "description": description,
                        "url": url,
                        "source": "dashscope",
                    })

        return json.dumps(images, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Logo 生成失败: {e}"}, ensure_ascii=False)


@tool
def generate_mermaid_diagram(mermaid_code: str, description: str) -> str:
    """
    将 Mermaid 代码转换为架构图图片（SVG 格式），用于展示系统结构。

    对应 Java: MermaidDiagramTool.generateMermaidDiagram()
    使用 mmdc (Mermaid CLI) 进行渲染，需要提前安装：
      npm install -g @mermaid-js/mermaid-cli

    参数:
        mermaid_code: Mermaid 图表代码（如 flowchart、sequenceDiagram 等）
        description: 架构图描述

    返回:
        JSON 格式的架构图信息，包含 svg_content 或错误信息
    """
    if not mermaid_code or not mermaid_code.strip():
        return json.dumps({"error": "Mermaid 代码为空"}, ensure_ascii=False)

    try:
        # 使用临时文件进行转换
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "diagram.mmd"
            output_file = Path(tmpdir) / "diagram.svg"

            # 写入 Mermaid 源码
            input_file.write_text(mermaid_code, encoding="utf-8")

            # 调用 mmdc 命令 (对应 Java 的 ProcessBuilder 执行)
            cmd_name = "mmdc.cmd" if os.name == "nt" else "mmdc"
            cmd = [cmd_name, "-i", str(input_file), "-o", str(output_file), "-b", "transparent"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return json.dumps(
                    {"error": f"mmdc 执行失败 (退出码 {result.returncode}): {result.stderr}"},
                    ensure_ascii=False,
                )

            if not output_file.exists():
                return json.dumps({"error": "mmdc 生成了空文件"}, ensure_ascii=False)

            # 读取 SVG 内容（内联到 HTML 中）
            svg_content = output_file.read_text(encoding="utf-8")

            return json.dumps(
                {
                    "category": "architecture",
                    "description": description,
                    "svg_content": svg_content,
                    "source": "mermaid",
                },
                ensure_ascii=False,
            )

    except FileNotFoundError:
        return json.dumps(
            {"error": "未找到 mmdc 命令，请先安装: npm install -g @mermaid-js/mermaid-cli"},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"error": f"Mermaid 图表生成失败: {e}"}, ensure_ascii=False)


# ==================== 图片工具列表（供 ImageCollectorNode 使用）====================
IMAGE_TOOLS = [search_images, search_illustrations, generate_logo, generate_mermaid_diagram]
