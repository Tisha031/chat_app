from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services import invite_service
from pydantic import BaseModel

router = APIRouter(prefix="/invites", tags=["Invites"])

class CreateInviteRequest(BaseModel):
    room_id: str
    never_expires: bool = False

class UseInviteRequest(BaseModel):
    code: str

@router.post("")
async def create_invite(
    data: CreateInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invite = await invite_service.create_invite(
        data.room_id, str(current_user.id), data.never_expires, db
    )
    return {
        "code": invite.code,
        "invite_url": f"http://localhost:5173/invite/{invite.code}",
        "never_expires": invite.never_expires,
        "expires_at": invite.expires_at,
    }

@router.post("/use")
async def use_invite(
    data: UseInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = await invite_service.use_invite(data.code, str(current_user.id), db)
    return {"room_id": str(room.id), "room_name": room.name}