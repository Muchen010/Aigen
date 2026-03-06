"""
Agent 状态定义模块

对应 Java 端: WorkflowContext.java

定义了在 LangGraph 所有节点之间流转的共享状态 (TypedDict)。
每个字段都映射到 Java 端 WorkflowContext 的对应属性。
"""

from typing import Annotated, Optional

from langgraph.graph import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """
    代码生成工作流共享状态。

    字段映射关系 (Java → Python):
      - appId              → app_id
      - userId             → user_id
      - generationType     → generation_type
      - originalPrompt     → original_prompt
      - enhancedPrompt     → enhanced_prompt
      - currentStep        → current_step
      - imageList          → collected_images
      - retrievedKnowledge → retrieved_knowledge
      - generatedCodeDir   → generated_code_dir
      - buildResultDir     → build_result_dir
      - qualityResult      → quality_result
    """

    # LangGraph 消息历史 (通过 add_messages 支持消息累积)
    messages: Annotated[list, add_messages]

    # --- 来自 Java 端的上下文 (工作流启动时传入) ---
    app_id: int
    user_id: int
    generation_type: str        # "html" | "multi_file" | "vue_project"
    original_prompt: str

    # --- 工作流执行过程中填充 ---
    enhanced_prompt: Optional[str]          # 提示词增强节点输出
    current_step: str                       # 当前正在执行的节点名称
    collected_images: Optional[list]        # 素材收集节点输出的图片列表
    retrieved_knowledge: Optional[str]      # RAG 检索到的知识文本块
    generated_code_dir: Optional[str]       # 代码生成节点输出的目录路径
    build_result_dir: Optional[str]         # 项目构建节点输出的构建产物目录
    quality_result: Optional[dict]          # 质量检查节点的检查结果
    retry_count: int                        # 质检失败后的重试次数
