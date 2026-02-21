from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.core.security import decode_token
from app.models.user import User
from app.models.message import Message
from app.websocket.manager import manager
from app.redis.client import redis_client
import json
from datetime import datetime, timezone

router = APIRouter(tags=["chat"])

async def get_user_from_token(token: str):
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(...)
):
    # authenticate user
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=4001)
        return

    # connect to room
    await manager.connect(websocket, room_id, str(user.id), user.username)

    # set online presence in Redis (expires in 60 seconds)
    await redis_client.setex(f"online:{user.id}", 60, user.username)

    # broadcast join event
    await manager.broadcast_to_room({
        "type": "user_joined",
        "user_id": str(user.id),
        "username": user.username,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, room_id)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "message":
                content = data.get("content", "").strip()
                if not content:
                    continue

                # save to database
                async with AsyncSessionLocal() as db:
                    msg = Message(
                        room_id=room_id,
                        sender_id=user.id,
                        content=content
                    )
                    db.add(msg)
                    await db.commit()
                    await db.refresh(msg)

                # broadcast to room
                await manager.broadcast_to_room({
                    "type": "message",
                    "message_id": str(msg.id),
                    "room_id": room_id,
                    "sender_id": str(user.id),
                    "username": user.username,
                    "content": content,
                    "timestamp": msg.created_at.isoformat()
                }, room_id)

            elif data.get("type") == "typing":
                # broadcast typing indicator
                await manager.broadcast_to_room({
                    "type": "typing",
                    "username": user.username,
                    "is_typing": data.get("is_typing", False)
                }, room_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await redis_client.delete(f"online:{user.id}")

        await manager.broadcast_to_room({
            "type": "user_left",
            "user_id": str(user.id),
            "username": user.username,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, room_id)