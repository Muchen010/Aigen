"""
代码生成服务层

对应 Java 端: AiCodeGeneratorFacade.java

封装代码生成的核心逻辑，包括：
  - 流式代码生成
  - 代码解析 (从 LLM 输出中提取有效代码)
  - 代码保存 (写入文件系统)

当前阶段 (Phase 1): 实现基础的代码生成和保存逻辑
后续 Phase 2: 集成到 LangGraph 节点中
"""

import os
import re
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.services.llm_service import get_code_gen_llm


async def generate_code_stream(
    prompt: str,
    code_gen_type: str,
    app_id: int,
):
    """
    流式生成代码。

    对应 Java 端: AiCodeGeneratorFacade.generateAndSaveCodeStream()

    参数:
        prompt: 增强后的用户提示词
        code_gen_type: 代码生成类型
        app_id: 应用 ID

    Yields:
        LLM 输出的每个 token
    """
    llm = get_code_gen_llm()

    # 根据类型构造 System Prompt
    system_prompt = _build_system_prompt(code_gen_type)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt),
    ]

    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content


def parse_html_code(raw_output: str) -> str:
    """
    从 LLM 输出中提取 HTML 代码。

    对应 Java 端: HtmlCodeParser.java

    LLM 可能返回带有 markdown 代码块标记的内容，
    此方法负责清理并提取纯净的 HTML 代码。

    参数:
        raw_output: LLM 的原始输出文本

    返回:
        提取后的纯净 HTML 代码
    """
    # 尝试从 ```html ... ``` 代码块中提取
    match = re.search(r"```html\s*\n(.*?)```", raw_output, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 尝试从 ``` ... ``` 通用代码块中提取
    match = re.search(r"```\s*\n(.*?)```", raw_output, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 如果包含 <!DOCTYPE 或 <html 标记，直接提取
    match = re.search(r"(<!DOCTYPE.*)", raw_output, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # 返回原始内容
    return raw_output.strip()


def parse_multi_file_code(raw_output: str) -> dict[str, str]:
    """
    从 LLM 输出中解析多文件代码。

    对应 Java 端: MultiFileCodeParser.java

    LLM 使用 --- FILE: path --- 和 --- END FILE --- 标记。

    参数:
        raw_output: LLM 的原始输出文本

    返回:
        字典，key 为文件路径，value 为文件内容
    """
    files = {}
    # 匹配 --- FILE: xxx --- ... --- END FILE --- 格式
    pattern = r"---\s*FILE:\s*(.+?)\s*---\s*\n(.*?)---\s*END FILE\s*---"
    matches = re.findall(pattern, raw_output, re.DOTALL)

    for file_path, content in matches:
        files[file_path.strip()] = content.strip()

    # 如果没有匹配到标准格式，尝试返回原始内容
    if not files:
        files["index.html"] = raw_output.strip()

    return files


def save_code_to_disk(
    code_content: str | dict[str, str],
    code_gen_type: str,
    app_id: int,
) -> Path:
    """
    将生成的代码保存到文件系统。

    对应 Java 端: CodeFileSaverExecutor + CodeFileSaverTemplate

    参数:
        code_content: 代码内容 (字符串或多文件字典)
        code_gen_type: 代码生成类型
        app_id: 应用 ID

    返回:
        保存目录的 Path 对象
    """
    # 构造输出目录: CODE_OUTPUT_ROOT_DIR / {type}_{appId}
    output_dir = Path(settings.CODE_OUTPUT_ROOT_DIR) / f"{code_gen_type}_{app_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    if isinstance(code_content, str):
        # 单文件模式 (HTML)
        output_file = output_dir / "index.html"
        output_file.write_text(code_content, encoding="utf-8")
    elif isinstance(code_content, dict):
        # 多文件模式
        for file_path, content in code_content.items():
            target_file = output_dir / file_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(content, encoding="utf-8")

    return output_dir


def _build_system_prompt(code_gen_type: str) -> str:
    """根据生成类型构造 System Prompt (内部方法)。"""
    base_rules = (
        "你是一个专业的前端代码生成专家。\n"
        "请根据用户需求生成高质量的代码，要求：\n"
        "1. 代码规范、结构清晰、注释完整\n"
        "2. 使用现代化的设计风格（渐变色、圆角、阴影、动画）\n"
        "3. 响应式布局，适配移动端和桌面端\n"
        "4. 代码可直接运行，无需额外配置\n"
    )

    if code_gen_type == "html":
        return (
            f"{base_rules}"
            "5. 生成完整的单页 HTML 文件，包含内联的 CSS 和 JavaScript\n"
            "6. 使用语义化 HTML5 标签\n"
            "7. 直接输出完整的 HTML 代码，以 <!DOCTYPE html> 开头\n"
        )
    elif code_gen_type == "multi_file":
        return (
            f"{base_rules}"
            "5. 生成多个文件，使用以下格式标记每个文件：\n"
            "   --- FILE: 文件路径 ---\n"
            "   文件内容\n"
            "   --- END FILE ---\n"
            "6. 至少包含 index.html、style.css、script.js\n"
        )
    elif code_gen_type == "vue_project":
        return (
            f"{base_rules}"
            "5. 生成 Vue 3 + Vite + TypeScript 项目代码\n"
            "6. 使用 Composition API (setup 语法糖)\n"
            "7. 使用以下格式标记每个文件：\n"
            "   --- FILE: 文件路径 ---\n"
            "   文件内容\n"
            "   --- END FILE ---\n"
        )
    else:
        return base_rules
