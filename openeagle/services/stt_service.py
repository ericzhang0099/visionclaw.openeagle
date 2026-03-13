"""
真实语音识别服务 - 使用OpenAI Whisper
"""

import os
import tempfile
import time
from pathlib import Path
from typing import Optional

# 尝试导入whisper，如果失败则使用模拟
try:
    import whisper
    WHISPER_AVAILABLE = True
    print("[STT] Whisper loaded successfully")
except ImportError:
    WHISPER_AVAILABLE = False
    print("[STT] Whisper not available, using mock")


class STTService:
    """语音识别服务"""
    
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self._loaded = False
        # 延迟加载：不在初始化时加载模型
    
    def _load_model(self):
        """加载Whisper模型（延迟加载）"""
        if self._loaded:
            return
            
        if WHISPER_AVAILABLE:
            try:
                print(f"[STT] Loading Whisper model: {self.model_name}")
                start = time.time()
                self.model = whisper.load_model(self.model_name)
                print(f"[STT] Model loaded in {time.time() - start:.2f}s")
            except Exception as e:
                print(f"[STT] Failed to load model: {e}")
                self.model = None
        
        self._loaded = True
    
    async def recognize(self, audio_path: str, language: Optional[str] = None) -> dict:
        """
        识别音频文件
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码 (如 'zh', 'en')
            
        Returns:
            识别结果字典
        """
        # 延迟加载模型
        self._load_model()
        
        if not WHISPER_AVAILABLE or self.model is None:
            # 模拟模式
            return {
                "text": "[模拟] 这是模拟的语音识别结果",
                "confidence": 0.95,
                "language": language or "zh",
                "duration": 3.5
            }
        
        try:
            start = time.time()
            
            # 调用Whisper
            result = self.model.transcribe(
                audio_path,
                language=language,
                fp16=False  # CPU运行
            )
            
            duration = time.time() - start
            print(f"[STT] Recognition completed in {duration:.2f}s")
            
            return {
                "text": result["text"].strip(),
                "confidence": result.get("confidence", 0.9),
                "language": result.get("language", language or "auto"),
                "duration": result.get("duration", 0)
            }
            
        except Exception as e:
            print(f"[STT] Recognition error: {e}")
            raise


# 全局服务实例
stt_service = STTService(model_name="base")
