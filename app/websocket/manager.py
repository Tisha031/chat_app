from collections import defaultdict
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # room_id → list of (websocket, user_id, username)
        self.active_connections: dict[str, list[tuple]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str, username: str):
        await websocket.accept()
        self.active_connections[room_id].append((websocket, user_id, username))

    def disconnect(self, websocket: WebSocket, room_id: str):
        self.active_connections[room_id] = [
            conn for conn in self.active_connections[room_id]
            if conn[0] != websocket
        ]

    async def broadcast_to_room(self, message: dict, room_id: str):
        dead_connections = []
        for conn in self.active_connections[room_id]:
            try:
                await conn[0].send_json(message)
            except Exception:
                dead_connections.append(conn)

        # clean up dead connections
        for conn in dead_connections:
            self.active_connections[room_id].remove(conn)

    def get_online_users(self, room_id: str) -> list:
        return [
            {"user_id": conn[1], "username": conn[2]}
            for conn in self.active_connections[room_id]
        ]

manager = ConnectionManager()