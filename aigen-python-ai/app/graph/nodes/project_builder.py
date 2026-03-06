"""
项目构建节点 - Vue 项目 npm 构建

对应 Java 端: ProjectBuilderNode.java + VueProjectBuilder.java

仅在 generation_type 为 vue_project 时触发。
检测 package.json，执行 npm install + npm run build，
构建产物输出到 dist 目录。
"""

import logging
import subprocess
from pathlib import Path

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def project_builder_node(state: AgentState) -> dict:
    """
    项目构建节点。

    对应 Java: ProjectBuilderNode.create() + VueProjectBuilder.buildProject()

    构建流程:
        1. 检查 generated_code_dir 是否存在
        2. 检测是否有 package.json（Vue 项目标志）
        3. 执行 npm install（安装依赖）
        4. 执行 npm run build（构建生产版本）
        5. 将 build_result_dir 设置为 dist 目录

    在未找到 package.json 时跳过构建（静默处理）。
    在构建失败时记录日志但不中断工作流。

    返回:
        更新 build_result_dir 字段的状态字典
    """
    generated_code_dir = state.get("generated_code_dir")

    if not generated_code_dir:
        raise ValueError("构建失败：找不到生成的代码目录")

    build_result_dir = generated_code_dir
    project_path = Path(generated_code_dir)
    package_json = project_path / "package.json"

    if not package_json.exists():
        # 非 Vue 项目，跳过构建（对应 Java: log.info("非Vue项目或未找到package.json，跳过构建步骤")）
        logger.info("[ProjectBuilder] 未检测到 package.json，跳过构建步骤")
        return {"current_step": "project_builder", "build_result_dir": build_result_dir}

    logger.info("[ProjectBuilder] 检测到 Vue 项目，开始执行构建...")

    try:
        # ==================== npm install ====================
        logger.info("[ProjectBuilder] 执行 npm install...")
        install_result = subprocess.run(
            ["npm", "install", "--prefer-offline"],
            cwd=generated_code_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 分钟超时
        )

        if install_result.returncode != 0:
            logger.error("[ProjectBuilder] npm install 失败:\n%s", install_result.stderr)
            return {"current_step": "project_builder", "build_result_dir": build_result_dir}

        logger.info("[ProjectBuilder] npm install 成功")

        # ==================== npm run build ====================
        logger.info("[ProjectBuilder] 执行 npm run build...")
        build_result = subprocess.run(
            ["npm", "run", "build"],
            cwd=generated_code_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 分钟超时
        )

        if build_result.returncode != 0:
            logger.error("[ProjectBuilder] npm run build 失败:\n%s", build_result.stderr)
            raise RuntimeError(f"Vue 项目构建失败: {build_result.stderr[:500]}")

        # 构建成功，将结果目录指向 dist
        dist_dir = project_path / "dist"
        if dist_dir.exists() and dist_dir.is_dir():
            build_result_dir = str(dist_dir)
            logger.info("[ProjectBuilder] Vue 项目构建成功，dist 目录: %s", build_result_dir)
        else:
            logger.warning("[ProjectBuilder] 构建成功但未找到 dist 目录，使用原目录")

    except subprocess.TimeoutExpired:
        logger.error("[ProjectBuilder] npm 命令超时（5分钟）")
    except Exception as e:
        logger.error("[ProjectBuilder] 项目构建异常: %s", e, exc_info=True)

    return {
        "current_step": "project_builder",
        "build_result_dir": build_result_dir,
    }
