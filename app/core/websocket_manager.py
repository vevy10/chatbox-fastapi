from fastapi import WebSocket
from typing import Dict, List
import json
from starlette.websockets import WebSocketState

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        await self.broadcast_presence()

    async def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            await self.broadcast_presence()

    async def broadcast_presence(self):
        online_ids = list(self.active_connections.keys())
        message = {"type": "presence", "online_ids": online_ids}
        for connection in self.active_connections.values():
            try:
                await connection.send_json(message)
            except: pass


    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"Erreur lors de l'envoi à {user_id}: {e}")
                    del self.active_connections[user_id]
            else:
                del self.active_connections[user_id]
                
                
manager = ConnectionManager()