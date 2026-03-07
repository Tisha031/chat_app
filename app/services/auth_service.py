from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.room import Room, RoomMember, RoomRole
from app.schemas.user import UserRegister
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from fastapi import HTTPException


async def register_user(data: UserRegister, db: AsyncSession):
    result = await db.execute(
        select(User).where((User.email == data.email) | (User.username == data.username))
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email or username already exists")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.flush()

    # Auto join all public servers
    public_rooms = await db.execute(
        select(Room).where(Room.is_public_server == True)
    )
    for room in public_rooms.scalars().all():
        existing = await db.execute(
            select(RoomMember).where(
                RoomMember.room_id == room.id,
                RoomMember.user_id == user.id
            )
        )
        if not existing.scalar_one_or_none():
            db.add(RoomMember(room_id=room.id, user_id=user.id, role=RoomRole.member))

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"id": str(user.id), "username": user.username, "email": user.email}
    }


async def login_user(email: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"id": str(user.id), "username": user.username, "email": user.email}
    }