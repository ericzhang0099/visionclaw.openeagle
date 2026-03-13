"""
Chat API - 模拟版
"""
from fastapi import APIRouter
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

@router.post("")
async def chat(request: ChatRequest):
    """聊天接口 - 模拟回复"""
    # 简单的模拟回复
    replies = [
        "收到你的消息了！",
        "你好！有什么我可以帮你的？",
        "我正在运行VisionClaw后端",
        "这是一个测试回复",
    ]
    import random
    reply = random.choice(replies)
    
    return {
        "code": 0,
        "data": {
            "message": f"{reply} 你说: {request.message}",
            "session_id": request.session_id or str(uuid4())
        }
    }

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    return await chat(request)

# 供WebSocket调用的函数
async def call_llm(message: str, context: dict) -> str:
    """调用LLM（供WebSocket使用）"""
    # 直接返回模拟回复
    replies = [
        "收到你的消息了！",
        "我正在处理你的请求",
        "这是一个测试回复",
    ]
    import random
    return random.choice(replies)
