"""
VisionClaw Backend - FastAPI Application
"""
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api import memory, agents, sessions, chat, vision, audio, health, websocket
from app.core.config import settings
from app.core.database import engine, Base

# 同步引擎用于创建表
from sqlalchemy import create_engine
sync_engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))

app = FastAPI(
    title="VisionClaw API",
    description="VisionClaw Backend API for Vision Intelligence Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(memory.router, prefix="/api/v1", tags=["Memory"])
app.include_router(agents.router, prefix="/api/v1", tags=["Agents"])
app.include_router(sessions.router, prefix="/api/v1", tags=["Sessions"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(vision.router, prefix="/api/v1", tags=["Vision"])
app.include_router(audio.router, prefix="/api/v1", tags=["Audio"])


# WebSocket端点（直接定义）
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class WSManager:
    connections: List[WebSocket] = []
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)
    
    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)
    
    async def send(self, msg: str, ws: WebSocket):
        await ws.send_text(msg)

ws_manager = WSManager()

# 当前连接的客户端类型
client_types = {}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    client_id = id(ws)
    client_types[client_id] = "unknown"
    
    try:
        while True:
            data = await ws.receive_text()
            
            try:
                import json
                msg = json.loads(data)
                msg_type = msg.get("type", "unknown")
                
                if msg_type == "video_frame":
                    # 处理视频帧 - 可以调用视觉模型
                    result = await process_video_frame(msg.get("data"))
                    await ws.send_text(json.dumps({
                        "type": "video_result",
                        "result": result
                    }))
                    
                elif msg_type == "audio":
                    # 处理音频 - 可以调用语音识别
                    result = await process_audio(msg.get("data"))
                    await ws.send_text(json.dumps({
                        "type": "audio_result", 
                        "result": result
                    }))
                    
                elif msg_type == "text":
                    # 处理文本对话
                    response = await call_llm_from_ws(msg.get("content", ""))
                    await ws.send_text(json.dumps({
                        "type": "text_response",
                        "content": response
                    }))
                    
                elif msg_type == "heartbeat":
                    # 心跳
                    await ws.send_text(json.dumps({
                        "type": "heartbeat_ack"
                    }))
                    
                else:
                    await ws.send_text(json.dumps({
                        "type": "echo",
                        "original": data
                    }))
                    
            except Exception as e:
                await ws.send_text(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
                
    except WebSocketDisconnect:
        client_types.pop(client_id, None)


async def process_video_frame(frame_data: str) -> dict:
    """处理视频帧（示例）"""
    # TODO: 接入实际的视觉模型
    # 可以用LLaVA、Qwen-VL等
    return {
        "description": "这是一帧视频画面",
        "objects": ["物体1", "物体2"],
        "scene": "室内"
    }


async def process_audio(audio_data: str) -> dict:
    """处理音频（示例）"""
    # TODO: 接入实际的语音识别模型
    return {
        "text": "这是语音识别结果",
        "language": "zh"
    }


async def call_llm_from_ws(message: str) -> str:
    """通过WebSocket调用LLM"""
    # 复用chat API的LLM调用
    from app.api.chat import call_llm
    return await call_llm(message, {})


# 智能体配置存储（内存中）
current_agent_config = {}


@app.post("/api/v1/agent/config")
async def set_agent_config(config: dict):
    """保存智能体配置"""
    global current_agent_config
    current_agent_config = config
    return {"status": "ok", "message": "配置已保存"}


@app.get("/api/v1/agent/config")
async def get_agent_config():
    """获取智能体配置"""
    return current_agent_config or {}


@app.on_event("startup")
async def startup_event():
    """启动时执行"""
    # 尝试连接Redis
    try:
        from app.core.redis import redis_client
        await redis_client.ping()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️ Redis连接失败: {e}")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "VisionClaw API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时执行"""
    from app.core.redis import redis_client
    await redis_client.close()
    print("✅ Redis disconnected")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "VisionClaw API",
        "version": "1.0.0",
        "docs": "/docs"
    }
