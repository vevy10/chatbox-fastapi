from sqlalchemy.orm import Session
from sqlalchemy import or_ 
from app.models.user_model import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_identifier(db: Session, identifier: str):
    """
    Cherche un utilisateur soit par son email, soit par son numéro de téléphone.
    """
    return db.query(User).filter(
        or_(
            User.email == identifier, 
            User.phone == identifier
        )
    ).first()

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user