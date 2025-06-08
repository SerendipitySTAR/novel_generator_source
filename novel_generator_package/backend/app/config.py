"""
配置文件，包含系统所需的各种配置参数
"""
import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # 应用基本配置
    APP_NAME: str = "自动小说生成器"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于大模型和多智能体协作的全自动多轮交互式小说生成器"

    # API配置
    API_PREFIX: str = "/api"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8002

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)
    ENABLE_JSON_LOGS: bool = os.getenv("ENABLE_JSON_LOGS", "false").lower() == "true"

    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ENABLE_AUTHENTICATION: bool = os.getenv("ENABLE_AUTHENTICATION", "false").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))

    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/novel_generator")

    # LLM配置 - 使用本地vLLM服务器
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-dummy-key")  # vLLM不需要真实key
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "http://localhost:8321/v1")
    DEFAULT_LLM_MODEL: str = "gpt-4o-2024-08-06"  # 与vLLM服务器中的served-model-name一致
    DEFAULT_EMBEDDING_MODEL: str = "/media/sc/AI/self-llm/embed_model/sentence-transformers/all-MiniLM-L6-v2"
    
    # 向量数据库配置
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./vector_db")
    
    # 知识图谱配置
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # 智能体配置
    AGENT_TEMPERATURE: float = 0.7
    AGENT_TOP_P: float = 0.9
    AGENT_MAX_TOKENS: int = 4000

    # 各环节Token配置
    CONCEPT_MAX_TOKENS: int = 6000  # 概述生成
    CONCEPT_EXPAND_MAX_TOKENS: int = 8000  # 概述扩展
    WORLD_SETTING_MAX_TOKENS: int = 8000  # 世界观设定
    PLOT_OUTLINE_MAX_TOKENS: int = 10000  # 大纲生成
    CHARACTER_MAX_TOKENS: int = 8000  # 人物设定
    CHAPTER_MAX_TOKENS: int = 6000  # 章节生成
    CHAPTER_POLISH_MAX_TOKENS: int = 8000  # 章节润色
    PLOT_BRANCHES_MAX_TOKENS: int = 4000  # 剧情分支

    # 评分阈值
    QUALITY_THRESHOLD: int = 80
    MAX_RETRIES: int = 3

    # 章节生成配置
    DEFAULT_CHAPTER_LENGTH: int = 3000

    # 写作风格选项
    WRITING_STYLES: List[str] = [
        "详细生动",
        "简洁明快",
        "诗意抒情",
        "悬疑紧张",
        "幽默风趣",
        "古典优雅",
        "现代都市",
        "科幻硬核",
        "奇幻史诗",
        "自定义"
    ]

    # Redis配置（可选）
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)

    # 文件存储配置
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB

    # 邮件配置（可选）
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST", None)
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER", None)
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD", None)
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "false").lower() == "true"

    # 监控配置（可选）
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN", None)
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
