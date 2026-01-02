from datetime import timedelta
from app.core.security import create_token
from app.core.config import settings

def generate_tokens(user_id: int):
    access = create_token(
        {"sub": str(user_id)},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh = create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return access, refresh
