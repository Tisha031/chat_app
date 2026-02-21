from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False

class RoomResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    is_private: bool
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}

class RoomMemberResponse(BaseModel):
    user_id: UUID
    room_id: UUID
    role: str
    joined_at: datetime

    model_config = {"from_attributes": True}