from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.room import RoomCreate, RoomLockVerify, DirectMessageCreate
from app.services import room_service

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("")
async def list_rooms(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await room_service.get_rooms(db)


@router.post("")
async def create_room(data: RoomCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await room_service.create_room(data, str(current_user.id), db)


@router.post("/{room_id}/verify-password")
async def verify_password(room_id: str, data: RoomLockVerify, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await room_service.verify_room_password(room_id, data.password, db)
    await room_service.join_room(room_id, str(current_user.id), db)
    return {"success": True}


@router.post("/{room_id}/join")
async def join_room(room_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await room_service.join_room(room_id, str(current_user.id), db)


@router.post("/{room_id}/leave")
async def leave_room(room_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await room_service.leave_room(room_id, str(current_user.id), db)
    return {"success": True}


@router.get("/{room_id}/messages")
async def get_messages(room_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await room_service.get_room_messages(room_id, db)


@router.post("/dm/start")
async def start_dm(data: DirectMessageCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await room_service.get_or_create_dm(str(current_user.id), data.target_username, db)