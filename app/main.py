from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine
from app.api.auth_router import router as auth_router
from app.api.chat_router import router as chat_router
from app.core.websocket_manager import manager
from fastapi.staticfiles import StaticFiles
from typing import Dict

app = FastAPI(title=settings.APP_NAME)

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(chat_router)


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "typing":
                payload = {
                    "type": "typing",
                    "sender_id": user_id,
                    "is_typing": data.get("is_typing")
                }
                await manager.send_personal_message(payload, data.get("receiver_id"))
                
            elif data.get("type") == "read_receipt":
                payload = {
                    "type": "read_receipt",
                    "message_id": data.get("message_id"),
                    "reader_id": user_id
                }
                await manager.send_personal_message(payload, data.get("sender_id"))

    except WebSocketDisconnect:
        await manager.disconnect(user_id)
    except Exception as e:
        print(f"Erreur socket: {e}")
        await manager.disconnect(user_id)