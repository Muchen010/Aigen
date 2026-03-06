"""
健康检查端点

对应 Java 端: HealthController.java
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """服务健康检查端点，用于容器探针和监控。"""
    return {
        "status": "ok",
        "service": "aigen-python-ai",
        "version": "0.1.0",
    }
