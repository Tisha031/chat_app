from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.room import Room, RoomMember, RoomRole
from app.models.message import Message
from app.schemas.room import RoomCreate
from uuid import UUID

async def create_room(data: RoomCreate, user_id: UUID, db: AsyncSession) -> Room:
    # check name not taken
    result = await db.execute(select(Room).where(Room.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Room name already exists")

    room = Room(
        name=data.name,
        description=data.description,
        is_private=data.is_private,
        created_by=user_id
    )
    db.add(room)
    await db.flush()

    # creator becomes admin member
    member = RoomMember(room_id=room.id, user_id=user_id, role=RoomRole.admin)
    db.add(member)
    await db.flush()

    return room

async def join_room(room_id: UUID, user_id: UUID, db: AsyncSession) -> RoomMember:
    # check room exists
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # check not already member
    result = await db.execute(
        select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already a member")

    member = RoomMember(room_id=room_id, user_id=user_id, role=RoomRole.member)
    db.add(member)
    await db.flush()
    return member

async def leave_room(room_id: UUID, user_id: UUID, db: AsyncSession):
    result = await db.execute(
        select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="You are not a member")

    await db.delete(member)

async def get_rooms(db: AsyncSession):
    result = await db.execute(select(Room).where(Room.is_private == False))
    return result.scalars().all()

async def get_room_messages(room_id: UUID, db: AsyncSession, limit: int = 50):
    result = await db.execute(
        select(Message)
        .where(Message.room_id == room_id, Message.is_deleted == False)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

async def search_messages(room_id: UUID, query: str, db: AsyncSession):
    result = await db.execute(
        select(Message)
        .where(
            Message.room_id == room_id,
            Message.is_deleted == False,
            Message.content.ilike(f"%{query}%")
        )
        .order_by(Message.created_at.desc())
        .limit(20)
    )
    return result.scalars().all()