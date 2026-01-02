from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    sexe: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    identifier: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    

class ForgotPasswordRequest(BaseModel):
    identifier: str

class ResetPassword(BaseModel):
    token: str
    new_password: str
    
    
class ResetPasswordSchema(BaseModel):
    identifier: str
    code: str
    new_password: str