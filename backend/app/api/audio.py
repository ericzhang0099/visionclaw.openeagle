"""
Audio API - 语音识别与合成
使用MiniMax语音API
"""
from fastapi import APIRouter, UploadFile, File, Form
import aiofiles
import os
from uuid import uuid4
import httpx
import base64

from app.core.config import settings

router = APIRouter()

# MiniMax API配置
MINIMAX_API_KEY = "sk-cp-lAg96b64ITHi7kzT-E2iDunuuhF7iMT5TgFiQBYMlsJEkVcSOgK_Ms_dR9ghE7zwUkBzf-09jiyOkTwAC5RHmF3lUGfnjcuTevRNHQwIfeeiroKIXDMRFg0"
MINIMAX_API_URL = "https://api.minimax.chat/v1"


@router.post("/audio/recognize")
async def recognize_audio(audio: UploadFile = File(...)):
    """语音识别 - 使用MiniMax API"""
    file_id = str(uuid4())
    file_ext = os.path.splitext(audio.filename)[1] or '.wav'
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}")
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await audio.read()
        await f.write(content)
    
    # 调用MiniMax语音识别API
    text = await recognize_with_minimax(file_path)

    return {
        "code": 0,
        "data": {
            "text": text,
            "confidence": 0.9,
            "language": "zh"
        }
    }


@router.post("/audio/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    voice: str = Form("male-qn-qingse"),
    speed: float = Form(1.0),
):
    """语音合成 - 使用MiniMax TTS API"""
    audio_data = await synthesize_with_minimax(text, voice, speed)

    return {
        "code": 0,
        "data": {
            "audio": audio_data,
            "sample_rate": 32000,
            "format": "wav"
        }
    }


@router.post("/audio/events")
async def detect_audio_events(audio: UploadFile = File(...)):
    """检测音频事件"""
    return {
        "code": 0,
        "data": {
            "events": [
                {"type": "speech", "start": 0.0, "end": 1.5, "confidence": 0.9}
            ]
        }
    }


async def recognize_with_minimax(file_path: str) -> str:
    """调用MiniMax语音识别API"""
    try:
        # 读取音频文件并转为base64
        with open(file_path, 'rb') as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MINIMAX_API_URL}/audio/transcription",
                headers={
                    "Authorization": f"Bearer {MINIMAX_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "file": audio_base64,
                    "model": "speech-01-preview",
                    "language": "zh"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("text", "识别失败")
            else:
                return f"API错误: {response.status_code}"
                
    except Exception as e:
        return f"识别失败: {str(e)}"


async def synthesize_with_minimax(text: str, voice: str, speed: float) -> str:
    """调用MiniMax语音合成API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MINIMAX_API_URL}/audio generation",
                headers={
                    "Authorization": f"Bearer {MINIMAX_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "speech-01-turbo",
                    "text": text,
                    "voice_setting": {
                        "voice_id": voice
                    },
                    "speed": speed
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("audio", "")
            else:
                return ""
                
    except Exception as e:
        return ""
