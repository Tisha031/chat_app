from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False
    is_locked: bool = False
    lock_password: Optional[str] = None

class RoomLockVerify(BaseModel):
    password: str

class RoomResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    is_private: bool
    is_direct: bool = False
    is_locked: bool = False
    is_public_server: bool = False
    created_by: Optional[UUID]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class DirectMessageCreate(BaseModel):
    target_username: str