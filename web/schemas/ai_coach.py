from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CoachSession(BaseModel):
    session_id: str
    msg_count: int
    started_at: Optional[datetime] = None


class CoachMessage(BaseModel):
    log_id: Optional[int] = None
    session_id: str
    role: str
    message: str
    tokens_used: int = 0
    created_at: Optional[datetime] = None


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class QuickActionRequest(BaseModel):
    action_type: str
    session_id: Optional[str] = None


class NewSessionResponse(BaseModel):
    session_id: str
