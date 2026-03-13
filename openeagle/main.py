"""
VisionClaw Audio Service - FastAPI入口
提供语音识别(STT)和语音合成(TTS) API
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.audio import router as audio_router
from core.middleware import RequestIDMiddleware, SimpleRateLimitMiddleware
from core.metrics import metrics_collector

# 服务状态跟踪
_service_status = {
    "start_time": time.time(),
    "request_count": 0,
    "error_count": 0
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    print("[Audio Service] Starting up...")
    _service_status["start_time"] = time.time()
    yield
    print("[Audio Service] Shutting down...")


app = FastAPI(
    title="VisionClaw Audio Service",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求ID追踪
app.add_middleware(RequestIDMiddleware)

# 限流保护 (每分钟60个请求)
app.add_middleware(SimpleRateLimitMiddleware, requests_per_minute=60)

# 注册路由
app.include_router(audio_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """增强健康检查 - 返回详细服务状态"""
    # 检查STT服务状态
    try:
        from services.stt_service import WHISPER_AVAILABLE
        stt_status = "available" if WHISPER_AVAILABLE else "mock"
    except:
        stt_status = "unavailable"
    
    # 检查TTS服务状态
    try:
        from services.tts_service import PIPER_AVAILABLE
        tts_status = "available" if PIPER_AVAILABLE else "mock"
    except:
        tts_status = "unavailable"
    
    uptime = time.time() - _service_status["start_time"]
    
    return {
        "status": "healthy",
        "service": "audio",
        "version": "0.1.0",
        "timestamp": int(time.time()),
        "uptime_seconds": int(uptime),
        "services": {
            "stt": stt_status,
            "tts": tts_status
        },
        "stats": {
            "request_count": _service_status["request_count"],
            "error_count": _service_status["error_count"]
        }
    }


@app.get("/metrics")
async def get_metrics():
    """获取服务指标"""
    uptime = time.time() - _service_status["start_time"]
    
    # 获取详细指标
    detailed_metrics = metrics_collector.get_summary()
    
    return {
        "uptime_seconds": int(uptime),
        "request_count": _service_status["request_count"],
        "error_count": _service_status["error_count"],
        "error_rate": _service_status["error_count"] / max(_service_status["request_count"], 1),
        "detailed": detailed_metrics
    }


@app.get("/metrics/endpoints")
async def get_endpoint_metrics():
    """获取端点详细指标"""
    return metrics_collector.get_summary()


@app.post("/metrics/reset")
async def reset_metrics():
    """重置指标（仅用于测试）"""
    metrics_collector.reset()
    return {"message": "Metrics reset successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
