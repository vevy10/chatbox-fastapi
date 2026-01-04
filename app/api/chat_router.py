from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.session import SessionLocal
from app.models.message_model import Message
from app.schemas.message_schema import MessageCreate, MessageOut
from app.core.websocket_manager import manager
import json

router = APIRouter(prefix="/chat", tags=["Chat"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/send", response_model=MessageOut)
async def send_message(data: MessageCreate, db: Session = Depends(get_db)):
    new_msg = Message(
        sender_id=data.sender_id,
        receiver_id=data.receiver_id,
        content=data.content
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    message_payload = {
        "id": new_msg.id,
        "content": new_msg.content,
        "sender_id": new_msg.sender_id,
        "receiver_id": new_msg.receiver_id,
        "created_at": str(new_msg.created_at)
    }
    
    await manager.send_personal_message(message_payload, new_msg.receiver_id)
    
    return new_msg

@router.get("/history/{friend_id}", response_model=list[MessageOut])
async def get_history(friend_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        or_(
            Message.receiver_id == friend_id,
            Message.sender_id == friend_id
        )
    ).order_by(Message.created_at.asc()).all()
    return messages