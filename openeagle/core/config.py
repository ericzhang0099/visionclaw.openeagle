"""
VisionClaw Audio Service - 配置管理模块

使用Pydantic Settings管理应用配置，支持环境变量覆盖
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List


class Settings:
    """
    应用配置类（简化版，不使用pydantic-settings）
    """
    
    # 服务基本信息
    service_name: str = "VisionClaw Audio Service"
    version: str = "0.1.0"
    environment: str = "development"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    
    # CORS配置
    cors_origins: List[str] = ["*"]
    
    # 语音识别配置
    whisper_model: str = "base"
    whisper_device: str = "auto"
    
    # 语音合成配置
    piper_model_path: str = "./models/piper"
    piper_default_voice: str = "zh_CN"
    
    # 音频处理配置
    max_audio_size: int = 50  # MB
    temp_dir: str = "./temp"
    
    def __init__(self):
        """从环境变量读取配置"""
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", self.port))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.whisper_model = os.getenv("WHISPER_MODEL", self.whisper_model)
        self.piper_model_path = os.getenv("PIPER_MODEL_PATH", self.piper_model_path)
        self.max_audio_size = int(os.getenv("MAX_AUDIO_SIZE", self.max_audio_size))
    
    @property
    def temp_directory(self) -> Path:
        """获取临时目录路径对象"""
        path = Path(self.temp_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def piper_model_directory(self) -> Path:
        """获取Piper模型目录路径对象"""
        path = Path(self.piper_model_path)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings()
