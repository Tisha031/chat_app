import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base
import enum

class RoomRole(str, enum.Enum):
    admin = "admin"
    member = "member"

class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    is_private = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    members = relationship("RoomMember", back_populates="room", cascade="all, delete")
    messages = relationship("Message", back_populates="room", cascade="all, delete")

class RoomMember(Base):
    __tablename__ = "room_members"

    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(RoomRole), default=RoomRole.member)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    room = relationship("Room", back_populates="members")
    user = relationship("User", back_populates="room_memberships")