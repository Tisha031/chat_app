import uuid
import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class RoomRole(str, enum.Enum):
    admin = "admin"
    member = "member"

class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    is_private = Column(Boolean, default=False)
    is_direct = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    lock_password = Column(String, nullable=True)
    is_public_server = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members = relationship("RoomMember", back_populates="room")
    messages = relationship("Message", back_populates="room")


class RoomMember(Base):
    __tablename__ = "room_members"

    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(RoomRole), default=RoomRole.member)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="members")
    user = relationship("User", back_populates="room_memberships")