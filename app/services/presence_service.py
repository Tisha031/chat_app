from app.redis.client import redis_client

async def set_online(user_id: str, username: str):
    await redis_client.setex(f"online:{user_id}", 60, username)

async def set_offline(user_id: str):
    await redis_client.delete(f"online:{user_id}")

async def get_online_users() -> list:
    keys = await redis_client.keys("online:*")
    online = []
    for key in keys:
        username = await redis_client.get(key)
        user_id = key.replace("online:", "")
        online.append({"user_id": user_id, "username": username})
    return online

async def is_user_online(user_id: str) -> bool:
    return await redis_client.exists(f"online:{user_id}") == 1

async def refresh_presence(user_id: str):
    # reset TTL — called on heartbeat
    await redis_client.expire(f"online:{user_id}", 60)