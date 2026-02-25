from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.room import Room, RoomMember, RoomRole
from app.models.message import Message
from app.models.user import User
from fastapi import HTTPException
import bcrypt


async def create_room(data, user_id: str, db: AsyncSession):
    existing = await db.execute(select(Room).where(Room.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Room name already exists")

    lock_password_hash = None
    if data.is_locked and data.lock_password:
        lock_password_hash = bcrypt.hashpw(
            data.lock_password.encode(), bcrypt.gensalt()
        ).decode()

    room = Room(
        name=data.name,
        description=data.description,
        is_private=data.is_private,
        is_locked=data.is_locked,
        lock_password=lock_password_hash,
        created_by=user_id,
    )
    db.add(room)
    await db.flush()

    member = RoomMember(room_id=room.id, user_id=user_id, role=RoomRole.admin)
    db.add(member)
    await db.commit()
    await db.refresh(room)
    return room


async def verify_room_password(room_id: str, password: str, db: AsyncSession):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room.is_locked:
        return True
    if not bcrypt.checkpw(password.encode(), room.lock_password.encode()):
        raise HTTPException(status_code=403, detail="Wrong room password")
    return True


async def get_or_create_dm(current_user_id: str, target_username: str, db: AsyncSession):
    target = await db.execute(select(User).where(User.username == target_username))
    target_user = target.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    dm_name = f"dm-{'-'.join(sorted([str(current_user_id), str(target_user.id)]))}"
    existing = await db.execute(select(Room).where(Room.name == dm_name))
    room = existing.scalar_one_or_none()

    if not room:
        room = Room(
            name=dm_name,
            description=f"DM",
            is_private=True,
            is_direct=True,
            created_by=current_user_id,
        )
        db.add(room)
        await db.flush()
        for uid in [current_user_id, target_user.id]:
            db.add(RoomMember(room_id=room.id, user_id=uid, role=RoomRole.member))
        await db.commit()
        await db.refresh(room)

    return {"room": room, "target_user": target_user}


async def join_room(room_id: str, user_id: str, db: AsyncSession):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.is_locked:
        raise HTTPException(status_code=403, detail="Room is locked. Verify password first.")

    existing = await db.execute(
        select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id
        )
    )
    if existing.scalar_one_or_none():
        return room

    db.add(RoomMember(room_id=room_id, user_id=user_id, role=RoomRole.member))
    await db.commit()
    return room


async def leave_room(room_id: str, user_id: str, db: AsyncSession):
    result = await db.execute(
        select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id
        )
    )
    member = result.scalar_one_or_none()
    if member:
        await db.delete(member)
        await db.commit()


async def get_rooms(db: AsyncSession):
    result = await db.execute(
        select(Room).where(Room.is_private == False, Room.is_direct == False)
    )
    return result.scalars().all()


async def get_room_messages(room_id: str, db: AsyncSession, limit: int = 50):
    result = await db.execute(
        select(Message, User.username)
        .join(User, Message.sender_id == User.id)
        .where(Message.room_id == room_id, Message.is_deleted == False)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    rows = result.all()
    messages = []
    for msg, username in rows:
        messages.append({
            "id": str(msg.id),
            "content": msg.content,
            "username": username,
            "sender_id": str(msg.sender_id),
            "room_id": str(msg.room_id),
            "timestamp": msg.created_at.isoformat() if msg.created_at else None,
            "type": msg.message_type.value if msg.message_type else "text"
        })
    return messages


async def create_public_servers(db: AsyncSession):
    servers = [
        {"name": "general", "description": "General chat for everyone 🌍", "is_public_server": True},
        {"name": "random", "description": "Random fun conversations 🎲", "is_public_server": True},
        {"name": "tech", "description": "Tech talk, coding, projects 💻", "is_public_server": True},
        {"name": "introductions", "description": "Introduce yourself here 👋", "is_public_server": True},
    ]
    for s in servers:
        existing = await db.execute(select(Room).where(Room.name == s["name"]))
        if not existing.scalar_one_or_none():
            room = Room(
                name=s["name"],
                description=s["description"],
                is_private=False,
                is_public_server=True,
            )
            db.add(room)
    await db.commit()