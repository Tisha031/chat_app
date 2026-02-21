from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.presence_service import get_online_users, is_user_online
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/online")
async def online_users(current_user: User = Depends(get_current_user)):
    return await get_online_users()

@router.get("/online/{user_id}")
async def check_user_online(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    online = await is_user_online(user_id)
    return {"user_id": user_id, "is_online": online}