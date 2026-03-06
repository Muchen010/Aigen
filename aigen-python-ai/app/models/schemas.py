"""
Pydantic 请求/响应模型定义

对应 Java 端:
  - langgraph4j/model/ (QualityResult, ImageCollectionPlan, ImageResource 等)
  - ai/model/ (HtmlCodeResult, MultiFileCodeResult 等)
"""

from pydantic import BaseModel, Field


# ==================== 工作流模型 (← Java langgraph4j/model/) ====================


class QualityResult(BaseModel):
    """代码质量检查结果。对应 Java: QualityResult.java"""

    is_valid: bool = Field(description="代码是否通过质量检查")
    feedback: str = Field(default="", description="质量反馈 / 错误详情")
    score: float = Field(default=0.0, description="质量评分 (0-100)")


class ImageResource(BaseModel):
    """收集到的图片资源。对应 Java: ImageResource.java"""

    url: str = Field(description="图片 URL")
    description: str = Field(default="", description="图片描述")
    source: str = Field(default="pexels", description="图片来源 (pexels/undraw/wanx)")


class ImageCollectionPlan(BaseModel):
    """图片收集计划。对应 Java: ImageCollectionPlan.java"""

    categories: list[str] = Field(default_factory=list, description="图片分类")
    keywords: list[str] = Field(default_factory=list, description="搜索关键词")
    count: int = Field(default=5, description="每类收集数量")


# ==================== 代码结果模型 (← Java ai/model/) ====================


class HtmlCodeResult(BaseModel):
    """HTML 代码生成结果。对应 Java: HtmlCodeResult.java"""

    html: str = Field(description="生成的 HTML 代码")
    css: str = Field(default="", description="生成的 CSS 代码")
    js: str = Field(default="", description="生成的 JavaScript 代码")


class MultiFileCodeResult(BaseModel):
    """多文件代码生成结果。对应 Java: MultiFileCodeResult.java"""

    files: dict[str, str] = Field(
        default_factory=dict,
        description="文件映射，key=文件路径，value=文件内容",
    )


# ==================== API 请求/响应模型 ====================


class WorkflowRequest(BaseModel):
    """发起代码生成工作流的请求体。"""

    task_id: str = Field(description="任务 ID (由 Java 核心服务签发)")
    app_id: int = Field(description="应用 ID")
    user_id: int = Field(description="用户 ID")
    prompt: str = Field(description="用户自然语言需求")
    code_gen_type: str = Field(default="html", description="生成类型: html / multi_file / vue_project")


class WorkflowCallbackRequest(BaseModel):
    """Python AI 服务回调 Java 核心服务的请求体 (工作流完成时)。"""

    task_id: str
    app_id: int
    status: str = Field(description="completed / failed")
    output_dir: str = Field(default="", description="生成的代码保存目录")
    error_message: str = Field(default="")
