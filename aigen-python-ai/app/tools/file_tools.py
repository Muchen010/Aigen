"""
文件操作工具集 - AI 代码生成过程中使用的文件工具

对应 Java 端: ai/tools/File*.java (BaseTool + 5个文件工具)

LangChain @tool 装饰器将这些函数暴露给 LLM 的 Tool Calling 功能。
所有文件操作都限制在 `CODE_OUTPUT_ROOT_DIR/vue_project_{app_id}/` 沙箱目录内，
防止 AI 越权访问系统文件。
"""

import os
from pathlib import Path

from langchain_core.tools import tool

from app.config import settings

# ==================== 受保护的文件名列表 ====================
# 对应 Java: FileDeleteTool.isImportantFile()
_PROTECTED_FILES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "vite.config.js", "vite.config.ts", "vue.config.js",
    "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json",
    "index.html", "main.js", "main.ts", "App.vue", ".gitignore", "README.md",
}

# 需要跳过的目录和文件名
_IGNORED_NAMES = {
    "node_modules", ".git", "dist", "build", ".DS_Store",
    ".env", "target", ".mvn", ".idea", ".vscode", "coverage",
}

# 需要忽略的文件扩展名
_IGNORED_EXTENSIONS = {".log", ".tmp", ".cache", ".lock"}


def _resolve_path(relative_path: str, app_id: int) -> Path:
    """
    将相对路径解析为沙箱内的绝对路径。

    路径格式: CODE_OUTPUT_ROOT_DIR / vue_project_{app_id} / relative_path

    参数:
        relative_path: 文件相对路径
        app_id: 应用 ID

    返回:
        绝对路径
    """
    project_dir = Path(settings.CODE_OUTPUT_ROOT_DIR) / f"vue_project_{app_id}"
    return project_dir / relative_path


def make_file_tools(app_id: int) -> list:
    """
    为指定应用创建文件操作工具列表。

    通过闭包绑定 app_id，确保 AI 只能操作指定应用的沙箱目录。

    对应 Java: SpringContextUtil.getBean + @ToolMemoryId 机制

    参数:
        app_id: 应用 ID

    返回:
        绑定了 app_id 的文件工具列表
    """

    @tool
    def write_file(relative_file_path: str, content: str) -> str:
        """
        写入文件到指定路径。

        如果父目录不存在，会自动创建。
        对应 Java: FileWriteTool.writeFile()

        参数:
            relative_file_path: 文件的相对路径
            content: 要写入文件的内容
        """
        try:
            path = _resolve_path(relative_file_path, app_id)
            # 创建父目录（如果不存在）
            path.parent.mkdir(parents=True, exist_ok=True)
            # 写入文件内容
            path.write_text(content, encoding="utf-8")
            return f"文件写入成功: {relative_file_path}"
        except Exception as e:
            return f"文件写入失败: {relative_file_path}, 错误: {e}"

    @tool
    def read_file(relative_file_path: str) -> str:
        """
        读取指定路径的文件内容。

        对应 Java: FileReadTool.readFile()

        参数:
            relative_file_path: 文件的相对路径
        """
        try:
            path = _resolve_path(relative_file_path, app_id)
            if not path.exists() or not path.is_file():
                return f"错误：文件不存在或不是文件 - {relative_file_path}"
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return f"读取文件失败: {relative_file_path}, 错误: {e}"

    @tool
    def modify_file(relative_file_path: str, old_content: str, new_content: str) -> str:
        """
        修改文件内容，用新内容替换指定的旧内容。

        对应 Java: FileModifyTool.modifyFile()

        参数:
            relative_file_path: 文件的相对路径
            old_content: 要替换的旧内容
            new_content: 替换后的新内容
        """
        try:
            path = _resolve_path(relative_file_path, app_id)
            if not path.exists() or not path.is_file():
                return f"错误：文件不存在或不是文件 - {relative_file_path}"
            original = path.read_text(encoding="utf-8")
            if old_content not in original:
                return f"警告：文件中未找到要替换的内容，文件未修改 - {relative_file_path}"
            modified = original.replace(old_content, new_content)
            if original == modified:
                return f"信息：替换后文件内容未发生变化 - {relative_file_path}"
            path.write_text(modified, encoding="utf-8")
            return f"文件修改成功: {relative_file_path}"
        except Exception as e:
            return f"修改文件失败: {relative_file_path}, 错误: {e}"

    @tool
    def delete_file(relative_file_path: str) -> str:
        """
        删除指定路径的文件。

        受保护的重要文件（package.json、main.ts 等）不允许删除。
        对应 Java: FileDeleteTool.deleteFile()

        参数:
            relative_file_path: 文件的相对路径
        """
        try:
            path = _resolve_path(relative_file_path, app_id)
            if not path.exists():
                return f"警告：文件不存在，无需删除 - {relative_file_path}"
            if not path.is_file():
                return f"错误：指定路径不是文件，无法删除 - {relative_file_path}"
            # 安全检查：禁止删除重要文件
            if path.name.lower() in {f.lower() for f in _PROTECTED_FILES}:
                return f"错误：不允许删除重要文件 - {path.name}"
            path.unlink()
            return f"文件删除成功: {relative_file_path}"
        except Exception as e:
            return f"删除文件失败: {relative_file_path}, 错误: {e}"

    @tool
    def read_dir(relative_dir_path: str = "") -> str:
        """
        读取目录结构，获取指定目录下的所有文件和子目录信息。

        会自动忽略 node_modules、.git、dist 等目录。
        对应 Java: FileDirReadTool.readDir()

        参数:
            relative_dir_path: 目录的相对路径，为空则读取整个项目根目录
        """
        try:
            project_root = Path(settings.CODE_OUTPUT_ROOT_DIR) / f"vue_project_{app_id}"
            target = project_root / (relative_dir_path or "")

            if not target.exists() or not target.is_dir():
                return f"错误：目录不存在或不是目录 - {relative_dir_path}"

            lines = ["项目目录结构:"]

            def _walk(directory: Path, depth: int = 0):
                """递归遍历目录，忽略特殊目录和文件。"""
                indent = "  " * depth
                try:
                    entries = sorted(directory.iterdir(), key=lambda e: (e.is_file(), e.name))
                except PermissionError:
                    return

                for entry in entries:
                    # 忽略特殊名称
                    if entry.name in _IGNORED_NAMES or entry.name.startswith("."):
                        continue
                    # 忽略特殊扩展名
                    if any(entry.name.endswith(ext) for ext in _IGNORED_EXTENSIONS):
                        continue
                    if entry.is_dir():
                        lines.append(f"{indent}{entry.name}/")
                        _walk(entry, depth + 1)
                    else:
                        size = entry.stat().st_size
                        lines.append(f"{indent}{entry.name} ({size}B)")

            _walk(target)
            return "\n".join(lines)

        except Exception as e:
            return f"读取目录结构失败: {relative_dir_path}, 错误: {e}"

    return [write_file, read_file, modify_file, delete_file, read_dir]
