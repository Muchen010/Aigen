"""
代码生成节点 - 工作流核心节点，调用 LLM + 文件工具生成代码

对应 Java 端: CodeGeneratorNode.java + AiCodeGeneratorFacade.java

核心逻辑:
1. 构建用户消息（注入 RAG 知识 + 质检修复逻辑）
2. 根据 generation_type 选择对应的生成策略
3. 调用 LLM 生成代码并保存到磁盘
"""

import logging
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.graph.state import AgentState
from app.models.enums import CodeGenType
from app.services.code_generator import (
    _build_system_prompt,
    parse_html_code,
    parse_multi_file_code,
    save_code_to_disk,
)
from app.services.llm_service import get_code_gen_llm
from app.tools.file_tools import make_file_tools

logger = logging.getLogger(__name__)


async def code_generator_node(state: AgentState) -> dict:
    """
    代码生成节点（核心节点）。

    对应 Java: CodeGeneratorNode.create() + AiCodeGeneratorFacade.generateAndSaveCodeStream()

    生成策略:
        - html/multi_file: 直接 LLM 生成并解析输出，写入文件
        - vue_project:     LLM + Tool Calling（文件工具），由 LLM 决定写哪些文件

    参数注入逻辑:
        - 正常模式: 使用 enhanced_prompt
        - 质检失败模式: 在 prompt 中附加错误信息和修复建议

    返回:
        更新 generated_code_dir 的状态字典
    """
    app_id = state.get("app_id", 0)
    generation_type = state.get("generation_type", CodeGenType.HTML.value)
    logger.info("[CodeGenerator] 开始生成代码，AppId: %s, 类型: %s", app_id, generation_type)

    # ==================== 第一步: 构建用户消息 ====================
    user_message = _build_user_message(state)

    # ==================== 第二步: 根据类型执行生成策略 ====================
    generated_code_dir: str | None = None

    try:
        if generation_type == CodeGenType.VUE_PROJECT.value:
            # Vue 项目: 使用 Tool Calling，LLM 自己决定写哪些文件
            generated_code_dir = await _generate_vue_with_tools(user_message, app_id)
        else:
            # HTML / 多文件: 直接生成并解析
            generated_code_dir = await _generate_and_save(user_message, generation_type, app_id)

    except Exception as e:
        logger.error("[CodeGenerator] 代码生成异常: %s", e, exc_info=True)

    logger.info("[CodeGenerator] 代码生成完成，输出目录: %s", generated_code_dir)

    return {
        "current_step": "code_generator",
        "generated_code_dir": generated_code_dir,
    }


def _build_user_message(state: AgentState) -> str:
    """
    构造用户消息，集成 RAG 知识注入和质检修复逻辑。

    对应 Java: CodeGeneratorNode.buildUserMessage()

    优先级:
        1. 若质检失败 → 使用错误修复 Prompt
        2. 其他情况 → 使用 enhanced_prompt
        3. 前置注入 RAG 检索到的知识片段
    """
    quality_result = state.get("quality_result")

    # 判断是否为质检失败后的修复模式
    if _is_quality_check_failed(quality_result):
        base_message = _build_error_fix_prompt(quality_result)
    else:
        base_message = state.get("enhanced_prompt") or state.get("original_prompt", "")

    # 注入 RAG 知识（如果有）
    retrieved_knowledge = state.get("retrieved_knowledge", "")
    if retrieved_knowledge and retrieved_knowledge.strip():
        logger.info("[CodeGenerator] 检测到 RAG 知识上下文，正在注入 Prompt...")
        knowledge_injection = (
            "\n\n### 补充技术参考资料 (RAG Knowledge Base)\n"
            "以下是从知识库中检索到的最新技术文档，请在编写代码时**优先遵循**以下规范和 API 用法：\n\n"
            f"{retrieved_knowledge}\n\n"
            "--------------------------------------------------\n"
        )
        base_message = knowledge_injection + "\n\n" + base_message

    return base_message


def _is_quality_check_failed(quality_result: dict | None) -> bool:
    """判断质检是否失败（有明确错误信息的失败）。"""
    if not quality_result:
        return False
    if quality_result.get("is_valid"):
        return False
    errors = quality_result.get("errors", [])
    return bool(errors)


def _build_error_fix_prompt(quality_result: dict) -> str:
    """构造错误修复提示词，告知 LLM 上次生成的问题。"""
    lines = ["\n\n## 上次生成的代码存在以下问题，请修复：\n"]
    for error in quality_result.get("errors", []):
        lines.append(f"- {error}")
    suggestions = quality_result.get("suggestions", [])
    if suggestions:
        lines.append("\n## 修复建议：\n")
        for suggestion in suggestions:
            lines.append(f"- {suggestion}")
    lines.append("\n请根据上述问题和建议重新生成代码，确保修复所有提到的问题。")
    return "\n".join(lines)


async def _generate_and_save(user_message: str, generation_type: str, app_id: int) -> str:
    """
    直接生成 HTML / 多文件代码并保存到磁盘。

    对应 Java: AiCodeGeneratorFacade 中 HTML 和 MultiFile 两个分支。
    """
    llm = get_code_gen_llm()
    system_prompt = _build_system_prompt(generation_type)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    # 聚合流式输出
    full_output = ""
    async for chunk in llm.astream(messages):
        if chunk.content:
            full_output += chunk.content

    # 解析并保存代码
    if generation_type == CodeGenType.HTML.value:
        code_content = parse_html_code(full_output)
    else:
        code_content = parse_multi_file_code(full_output)

    output_dir = save_code_to_disk(code_content, generation_type, app_id)
    return str(output_dir)


async def _generate_vue_with_tools(user_message: str, app_id: int) -> str:
    """
    使用 Tool Calling 生成 Vue 项目代码。

    LLM 可以自主调用文件工具（write_file、read_file 等），
    逐步构建完整的 Vue 项目结构。

    对应 Java: AiCodeGeneratorFacade 中 VueProject 分支 + Agent 工具调用。
    """
    from langchain_core.messages import AIMessage, ToolMessage

    # 获取为该 app_id 绑定的文件工具
    file_tools = make_file_tools(app_id)

    # 给 LLM 绑定工具
    llm = get_code_gen_llm()
    llm_with_tools = llm.bind_tools(file_tools)
    tool_map = {t.name: t for t in file_tools}

    # 构造系统提示词
    system_prompt = _build_system_prompt(CodeGenType.VUE_PROJECT.value)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    # 创建项目根目录
    project_dir = Path(settings.CODE_OUTPUT_ROOT_DIR) / f"vue_project_{app_id}"
    project_dir.mkdir(parents=True, exist_ok=True)

    # Tool Calling 循环（LLM 不断调用工具直到完成）
    max_rounds = 20  # 最多 20 轮工具调用，防止无限循环
    for round_num in range(max_rounds):
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)

        # 如果没有工具调用，说明生成完成
        if not response.tool_calls:
            logger.info("[CodeGenerator] Vue 项目生成完成，共执行 %d 轮工具调用", round_num + 1)
            break

        # 执行工具调用
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            if tool_name in tool_map:
                try:
                    tool_result = tool_map[tool_name].invoke(tool_args)
                    logger.info("[CodeGenerator] 工具调用: %s -> %s", tool_name, str(tool_result)[:100])
                except Exception as e:
                    tool_result = f"工具调用失败: {e}"
            else:
                tool_result = f"未知工具: {tool_name}"

            # 将工具结果添加到消息链
            messages.append(
                ToolMessage(content=str(tool_result), tool_call_id=tool_id)
            )

    return str(project_dir)
