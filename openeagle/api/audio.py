"""
音频API路由 - 提供STT和TTS接口
"""

import base64
import io
import os
import tempfile
import time
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

router = APIRouter(prefix="/audio", tags=["audio"])


# ============ 请求/响应模型 ============

class STTResponse(BaseModel):
    """语音识别响应"""
    code: int = 0
    message: str = "success"
    data: dict = Field(default_factory=dict)
    timestamp: int = Field(default_factory=lambda: int(time.time()))


class TTSRequest(BaseModel):
    """语音合成请求"""
    text: str = Field(..., min_length=1, max_length=500, description="要合成的文本")
    voice: Optional[str] = Field(default="zh_CN", description="语音类型")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="语速")


class TTSResponse(BaseModel):
    """语音合成响应"""
    code: int = 0
    message: str = "success"
    data: dict = Field(default_factory=dict)
    timestamp: int = Field(default_factory=lambda: int(time.time()))


# ============ 导入真实服务 ============

try:
    from services.stt_service import stt_service
    from services.tts_service import tts_service
    print("[API] Using real STT/TTS services")
except ImportError as e:
    print(f"[API] Failed to import services: {e}, using mock")
    # 降级到模拟服务
    class MockSTTService:
        async def recognize(self, audio_path: str, language: Optional[str] = None) -> dict:
            return {
                "text": "[模拟] 这是模拟的语音识别结果",
                "confidence": 0.95,
                "language": language or "zh",
                "duration": 3.5
            }

    class MockTTSService:
        async def synthesize(self, text: str, voice: str = "zh_CN", speed: float = 1.0) -> bytes:
            return b"RIFF\x26\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00" \
                   b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x02\x00\x00\x00\x00\x00"

    stt_service = MockSTTService()
    tts_service = MockTTSService()


# ============ API端点 ============

@router.post("/recognize", response_model=STTResponse)
async def speech_to_text(
    audio: UploadFile = File(..., description="音频文件"),
    language: Optional[str] = Form(default=None, description="语言代码")
):
    """
    语音识别 (STT)
    
    将音频文件转换为文本
    """
    tmp_path = None
    try:
        # 验证文件类型
        allowed_types = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/mp4", "audio/x-m4a"]
        if audio.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"不支持的音频格式: {audio.content_type}")
        
        # 读取并验证文件大小
        content = await audio.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB限制
            raise HTTPException(status_code=413, detail="文件过大，最大支持10MB")
        
        # 自动转换音频格式为WAV
        try:
            from utils.audio_converter import convert_audio
            content = convert_audio(content, target_sample_rate=16000)
        except Exception as e:
            print(f"[Audio] Conversion warning: {e}")
            # 转换失败继续使用原始数据
        
        # 保存临时文件（使用上下文管理器确保清理）
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # 调用识别服务
        result = await stt_service.recognize(tmp_path, language)
        
        return STTResponse(
            code=0,
            message="success",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # 记录详细错误，但返回简化信息
        print(f"[STT Error] {e}")
        raise HTTPException(status_code=500, detail="语音识别服务暂时不可用")
    finally:
        # 确保临时文件被清理
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass


@router.post("/synthesize", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    语音合成 (TTS)
    
    将文本转换为语音
    """
    try:
        # 调用合成服务
        audio_data = await tts_service.synthesize(
            text=request.text,
            voice=request.voice,
            speed=request.speed
        )
        
        # Base64编码
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return TTSResponse(
            code=0,
            message="success",
            data={
                "audio": audio_base64,
                "format": "wav",
                "sample_rate": 16000,
                "duration": len(request.text) * 0.3  # 估算时长
            }
        )
        
    except Exception as e:
        # 记录详细错误，但返回简化信息
        print(f"[TTS Error] {e}")
        raise HTTPException(status_code=500, detail="语音合成服务暂时不可用")


@router.get("/info")
async def get_audio_info():
    """获取音频服务信息"""
    return {
        "code": 0,
        "message": "success",
        "data": {
            "stt_available": True,
            "tts_available": True,
            "supported_formats": ["wav", "mp3", "m4a"],
            "supported_languages": ["zh", "en"],
            "max_file_size": "10MB"
        },
        "timestamp": int(time.time())
    }
