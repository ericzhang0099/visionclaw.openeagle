"""
WebSocket API
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""
    active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理消息，可以调用LLM
            await manager.send_personal_message(f"收到: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
