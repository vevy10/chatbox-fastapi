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
    
class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    profile_photo: Optional[str]
    last_message: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut
    

class ForgotPasswordRequest(BaseModel):
    identifier: str

class ResetPassword(BaseModel):
    token: str
    new_password: str
    
    
class ResetPasswordSchema(BaseModel):
    identifier: str
    code: str
    new_password: str
    
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    profile_photo: Optional[str] = None

    class Config:
        from_attributes = True