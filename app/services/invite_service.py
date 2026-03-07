from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.invite import RoomInvite
from app.models.room import Room, RoomMember, RoomRole
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import secrets


async def create_invite(room_id: str, user_id: str, never_expires: bool, db: AsyncSession):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    code = secrets.token_urlsafe(8)
    expires_at = None if never_expires else datetime.now(timezone.utc) + timedelta(days=7)

    invite = RoomInvite(
        room_id=room_id,
        created_by=user_id,
        code=code,
        never_expires=never_expires,
        expires_at=expires_at,
    )
    db.add(invite)
    await db.commit()
    await db.refresh(invite)
    return invite


async def use_invite(code: str, user_id: str, db: AsyncSession):
    result = await db.execute(select(RoomInvite).where(RoomInvite.code == code))
    invite = result.scalar_one_or_none()

    if not invite:
        raise HTTPException(status_code=404, detail="Invalid invite link")

    if not invite.never_expires and invite.expires_at:
        if datetime.now(timezone.utc) > invite.expires_at:
            raise HTTPException(status_code=400, detail="Invite link has expired")

    existing = await db.execute(
        select(RoomMember).where(
            RoomMember.room_id == invite.room_id,
            RoomMember.user_id == user_id
        )
    )
    if not existing.scalar_one_or_none():
        db.add(RoomMember(room_id=invite.room_id, user_id=user_id, role=RoomRole.member))
        await db.commit()

    room = await db.execute(select(Room).where(Room.id == invite.room_id))
    return room.scalar_one()