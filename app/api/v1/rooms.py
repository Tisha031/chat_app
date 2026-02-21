from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.room import RoomCreate, RoomResponse, RoomMemberResponse
from app.schemas.message import MessageResponse
from app.services import room_service
from typing import List

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("", response_model=RoomResponse, status_code=201)
async def create_room(
    data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await room_service.create_room(data, current_user.id, db)

@router.get("", response_model=List[RoomResponse])
async def list_rooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await room_service.get_rooms(db)

@router.post("/{room_id}/join", response_model=RoomMemberResponse)
async def join_room(
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await room_service.join_room(room_id, current_user.id, db)

@router.post("/{room_id}/leave", status_code=204)
async def leave_room(
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await room_service.leave_room(room_id, current_user.id, db)

@router.get("/{room_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await room_service.get_room_messages(room_id, db)

@router.get("/{room_id}/messages/search", response_model=List[MessageResponse])
async def search_messages(
    room_id: UUID,
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await room_service.search_messages(room_id, q, db)