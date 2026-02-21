from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class MessageResponse(BaseModel):
    id: UUID
    room_id: UUID
    sender_id: UUID
    content: str
    message_type: str
    created_at: datetime

    model_config = {"from_attributes": True}