"""
应用配置管理模块

基于 Pydantic Settings，从 .env 文件和环境变量中加载配置。
对应 Java 端: application.yml + 各种 Config 类
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局应用配置，从 .env 文件或环境变量中加载。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- 应用基础配置 ---
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8100
    APP_DEBUG: bool = True

    # --- DashScope 大模型配置 ---
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_MODEL: str = "qwen-plus"
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # --- Redis 配置 (与 Java 端共享) ---
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # --- Java 核心业务服务 ---
    JAVA_CORE_BASE_URL: str = "http://127.0.0.1:8080"
    JAVA_CORE_INTERNAL_SECRET: str = ""

    # --- Pexels 图片搜索 ---
    PEXELS_API_KEY: str = ""

    # --- 代码输出目录 ---
    CODE_OUTPUT_ROOT_DIR: str = "./output"

    # --- 跨域配置 ---
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        """将逗号分隔的跨域来源字符串解析为列表。"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def redis_url(self) -> str:
        """构建 Redis 连接 URL。"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
