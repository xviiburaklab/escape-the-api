from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class RoomBase(BaseModel):
    type: str
    title: Optional[str] = None
    clue: Optional[str] = None
    answer: str
    hint: Optional[str] = None
    room_order: int
    active: bool = True

class RoomCreate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SessionResponse(BaseModel):
    id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_room: int
    request_count: int
    config: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

class AnswerSubmit(BaseModel):
    answer: str
