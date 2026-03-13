"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "VisionClaw"
    DEBUG: bool = True
    
    # 数据库 - 使用SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:///./vision_claw.db"
    
    # Redis - 使用内存模拟
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 安全
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # LLM配置
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "sk-cp-lAg96b64ITHi7kzT-E2iDunuuhF7iMT5TgFiQBYMlsJEkVcSOgK_Ms_dR9ghE7zwUkBzf-09jiyOkTwAC5RHmF3lUGfnjcuTevRNHQwIfeeiroKIXDMRFg0")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")
    
    # OpenAI配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-cp-lAg96b64ITHi7kzT-E2iDunuuhF7iMT5TgFiQBYMlsJEkVcSOgK_Ms_dR9ghE7zwUkBzf-09jiyOkTwAC5RHmF3lUGfnjcuTevRNHQwIfeeiroKIXDMRFg0")
    
    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    
    class Config:
        env_file = ".env"


settings = Settings()
