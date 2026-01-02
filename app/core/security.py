from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_token(data: dict, expires: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expires
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
