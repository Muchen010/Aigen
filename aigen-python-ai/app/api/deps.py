"""
API 依赖注入模块

提供端点共享的依赖注入函数，包括：
  - 服务间 Token 校验 (Java 调用 Python 时的认证)
  - 用户身份验证 (通过 Redis 共享 Session)
"""

from fastapi import Header, HTTPException

from app.config import settings


async def verify_internal_token(
    x_internal_secret: str = Header(None, alias="X-Internal-Secret"),
) -> bool:
    """
    验证服务间内部通讯令牌。

    当 Java 后端直接调用 Python AI 服务时，
    通过 X-Internal-Secret 请求头进行身份验证。

    在开发环境（未配置 secret）下跳过验证。

    参数:
        x_internal_secret: 请求头中的内部通讯密钥

    返回:
        验证是否通过

    异常:
        HTTPException(403): 令牌无效
    """
    if not settings.JAVA_CORE_INTERNAL_SECRET:
        # 开发环境未配置密钥时跳过验证
        return True
    if x_internal_secret != settings.JAVA_CORE_INTERNAL_SECRET:
        raise HTTPException(status_code=403, detail="内部服务令牌无效")
    return True
