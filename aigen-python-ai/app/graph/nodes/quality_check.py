"""
代码质量检查节点 - LLM 驱动的代码审查

对应 Java 端: CodeQualityCheckNode.java + CodeQualityCheckService.java

检查流程:
1. 扫描生成代码目录，读取所有代码文件
2. 调用 LLM 检查代码质量（语法、逻辑、安全、最佳实践）
3. 返回结构化的质检结果（是否通过、错误列表、改进建议）
"""

import json
import logging
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.graph.state import AgentState
from app.services.llm_service import get_reasoning_llm

logger = logging.getLogger(__name__)

# 需要检查的文件扩展名（对应 Java: CODE_EXTENSIONS）
_CODE_EXTENSIONS = {".html", ".htm", ".css", ".js", ".json", ".vue", ".ts", ".jsx", ".tsx"}

# 需要跳过的目录名（对应 Java: shouldSkipFile）
_SKIP_DIRS = {"node_modules", "dist", "target", ".git", ".vscode", ".idea"}


class QualityCheckResult(BaseModel):
    """LLM 质量检查返回的结构化结果。"""
    is_valid: bool = Field(description="代码是否通过质量检查")
    score: float = Field(default=0.0, description="质量评分 (0-100)")
    errors: list[str] = Field(default_factory=list, description="发现的问题列表")
    suggestions: list[str] = Field(default_factory=list, description="改进建议列表")


async def quality_check_node(state: AgentState) -> dict:
    """
    代码质量检查节点。

    对应 Java: CodeQualityCheckNode.create()

    检查维度:
        - 语法正确性（HTML 结构、JS 语法、CSS 规则）
        - 代码可运行性（能否直接在浏览器中打开）
        - UI 完整性（是否实现了用户需求的核心功能）
        - 安全性（是否有 XSS、不安全的 eval 等问题）

    异常处理:
        - 若质检服务异常，直接视为通过（is_valid=True），继续工作流
        （对应 Java: catch 块中 isValid=true 逻辑）

    返回:
        更新 quality_result 字段的状态字典
    """
    generated_code_dir = state.get("generated_code_dir")
    logger.info("[QualityCheck] 开始代码质量检查，目录: %s", generated_code_dir)

    quality_result = {
        "is_valid": True,
        "score": 80.0,
        "errors": [],
        "suggestions": [],
        "feedback": "OK",
    }

    try:
        # ==================== 第一步: 读取并拼接代码文件 ====================
        code_content = _read_code_files(generated_code_dir)

        if not code_content.strip():
            logger.warning("[QualityCheck] 未找到可检查的代码文件")
            quality_result = {
                "is_valid": False,
                "score": 0.0,
                "errors": ["未找到可检查的代码文件"],
                "suggestions": ["请确保代码生成成功"],
                "feedback": "未找到代码文件",
            }
            return {"current_step": "quality_check", "quality_result": quality_result}

        # ==================== 第二步: LLM 代码质量检查 ====================
        check_llm = get_reasoning_llm(streaming=False)
        # 限制提交给 LLM 的代码长度（避免超 token 限制）
        code_snippet = code_content[:8000] if len(code_content) > 8000 else code_content

        messages = [
            SystemMessage(content=(
                "你是一个专业的代码质量审查专家。\n"
                "请对以下代码进行质量检查，以 JSON 格式返回结果。\n\n"
                "检查维度：\n"
                "1. 语法正确性（HTML 结构、JS 语法、CSS 规则等）\n"
                "2. 代码可运行性（能否直接在浏览器打开或构建成功）\n"
                "3. 功能完整性（是否实现了基本的页面功能）\n"
                "4. 代码质量（代码是否整洁，有无明显 bug）\n\n"
                "JSON 格式：\n"
                "{\n"
                '  "is_valid": true/false,\n'
                '  "score": 0-100,\n'
                '  "errors": ["错误1", "错误2"],     // 严重问题，必须修复才能通过\n'
                '  "suggestions": ["建议1", "建议2"] // 优化建议，不影响通过\n'
                "}\n"
                "注意：只有存在严重的语法错误或功能缺失时才设置 is_valid=false，"
                "小的代码风格问题不应阻止通过。"
            )),
            HumanMessage(content=f"请检查以下代码：\n\n{code_snippet}"),
        ]

        response = await check_llm.ainvoke(messages)
        response_text = response.content.strip()

        # 解析 JSON 结果
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        result_data = json.loads(response_text)
        quality_result = {
            "is_valid": bool(result_data.get("is_valid", True)),
            "score": float(result_data.get("score", 80.0)),
            "errors": result_data.get("errors", []),
            "suggestions": result_data.get("suggestions", []),
            "feedback": "通过" if result_data.get("is_valid") else "发现问题",
        }

        logger.info(
            "[QualityCheck] 质检完成 - 通过: %s, 评分: %.1f, 问题数: %d",
            quality_result["is_valid"],
            quality_result["score"],
            len(quality_result["errors"]),
        )

    except (json.JSONDecodeError, KeyError) as e:
        # JSON 解析失败，视为通过（避免工作流中断）
        logger.warning("[QualityCheck] 质检结果解析失败，视为通过: %s", e)
    except Exception as e:
        # 异常直接跳到下一步（对应 Java: catch 块的 isValid=true）
        logger.error("[QualityCheck] 质检异常（已降级为通过）: %s", e, exc_info=True)

    return {
        "current_step": "quality_check",
        "quality_result": quality_result,
    }


def _read_code_files(code_dir: str | None) -> str:
    """
    读取目录下所有代码文件并拼接为单一字符串。

    对应 Java: CodeQualityCheckNode.readAndConcatenateCodeFiles()

    参数:
        code_dir: 代码目录路径

    返回:
        所有代码文件的拼接内容
    """
    if not code_dir:
        return ""

    directory = Path(code_dir)
    if not directory.exists() or not directory.is_dir():
        logger.error("[QualityCheck] 代码目录不存在: %s", code_dir)
        return ""

    content_parts = ["# 项目文件结构和代码内容\n"]

    for file_path in sorted(directory.rglob("*")):
        # 跳过目录
        if file_path.is_dir():
            continue
        # 跳过特殊目录
        if any(skip in file_path.parts for skip in _SKIP_DIRS):
            continue
        # 跳过隐藏文件
        if file_path.name.startswith("."):
            continue
        # 只检查代码文件
        if file_path.suffix.lower() not in _CODE_EXTENSIONS:
            continue

        try:
            relative_path = file_path.relative_to(directory)
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            content_parts.append(f"## 文件: {relative_path}\n\n{content}\n")
        except Exception:
            continue

    return "\n".join(content_parts)
