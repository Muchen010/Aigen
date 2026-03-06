"""
API 路由聚合注册模块

将所有子路由挂载到统一的 api_router 下。
在 main.py 中以 /api/v1/ai 前缀注册。
"""

from fastapi import APIRouter

from app.api.endpoints import chat, health, workflow

api_router = APIRouter()

# 健康检查
api_router.include_router(health.router, tags=["Health"])

# LLM 对话测试 (开发调试用)
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])

# 工作流 - AI 代码生成
api_router.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])
