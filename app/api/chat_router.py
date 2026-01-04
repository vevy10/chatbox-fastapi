from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.session import SessionLocal
from app.models.message_model import Message
from app.schemas.message_schema import MessageCreate, MessageOut
from app.core.websocket_manager import manager

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
        content=data.content,
        is_read=False 
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    message_payload = {
        "type": "chat_message",
        "id": new_msg.id,
        "content": new_msg.content,
        "sender_id": new_msg.sender_id,
        "receiver_id": new_msg.receiver_id,
        "is_read": new_msg.is_read,
        "created_at": new_msg.created_at.isoformat()
    }
    
    await manager.send_personal_message(message_payload, new_msg.receiver_id)
    return new_msg


@router.patch("/read/{message_id}")
async def mark_as_read(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if msg:
        msg.is_read = True
        db.commit()
    return {"status": "ok"}


@router.get("/history/{friend_id}", response_model=list[MessageOut])
async def get_history(friend_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        or_(
            Message.receiver_id == friend_id,
            Message.sender_id == friend_id
        )
    ).order_by(Message.created_at.asc()).all()
    return messages