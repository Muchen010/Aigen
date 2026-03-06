"""
Aigen Python AI 服务 - FastAPI 应用入口

启动方式:
    uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings


@asynccontextmanager
async def lifespan(application: FastAPI):
    """应用生命周期钩子：启动与关闭时执行。"""
    # --- 启动 ---
    print(f"[START] Aigen AI Service starting on {settings.APP_HOST}:{settings.APP_PORT}")
    print(f"[ENV] Environment: {settings.APP_ENV}")
    print(f"[LLM] Model: {settings.DASHSCOPE_MODEL}")
    yield
    # --- 关闭 ---
    print("[STOP] Aigen AI Service shutting down")


app = FastAPI(
    title="Aigen AI Service",
    description="基于 LangGraph 的智能代码生成 Agent 工作流服务",
    version="0.1.0",
    lifespan=lifespan,
)

# 跨域配置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1/ai")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
    )
