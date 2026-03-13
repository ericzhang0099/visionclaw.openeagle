"""
数据库模型 - Session和Message
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class SessionStatus(enum.Enum):
    """会话状态"""
    ACTIVE = "active"
    ENDED = "ended"


class MessageRole(enum.Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(enum.Enum):
    """消息类型"""
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"


class Session(Base):
    """会话模型"""
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    user_id = Column(String(36), nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    meta = Column(JSON, default={})
    created_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Session {self.id} {self.status}>"


class Message(Base):
    """消息模型"""
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    type = Column(Enum(MessageType), default=MessageType.TEXT)
    content = Column(Text, nullable=False)
    meta = Column(JSON, default={})
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<Message {self.id} {self.role.value}>"
