from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.schemas.user_schema import UserCreate, UserLogin, Token, ForgotPasswordRequest, ResetPasswordSchema, UserResponse
from app.repositories.user_repo import create_user, get_user_by_identifier
from app.models.user_model import User
from app.core.security import hash_password, verify_password
from app.services.auth_service import generate_tokens
from app.services.email_service import send_auth_email
import re
from app.services.sms_service import send_sms_code
import shutil
import os
import secrets

router = APIRouter(prefix="/auth")

UPLOAD_DIR = "static/profile_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
async def register(data: UserCreate, db: Session = Depends(get_db)):
    if data.email and get_user_by_identifier(db, data.email):
        raise HTTPException(400, "Cet email est déjà utilisé")
    
    new_user_obj = User(
        first_name=data.first_name,
        last_name=data.last_name,
        sexe=data.sexe,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password)
    )
    
    user_created = create_user(db, new_user_obj)
    
    if data.email:
        await send_auth_email(
            email_to=data.email,
            subject="Bienvenue sur CHATBOX",
            body=f"<h1>Bonjour {data.last_name} {data.first_name}</h1><p>Votre compte a été créé avec succès.</p>"
        )
    
    return {"message": "Utilisateur créé et email envoyé", "user_id": user_created.id}

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_identifier(db, data.identifier)

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Identifiants invalides")

    access, refresh = generate_tokens(user.id)
    return {
        "access_token": access, 
        "refresh_token": refresh,
        "user": user
    }

@router.post("/upload-photo/{user_id}")
def upload_profile_photo(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    extension = file.filename.split(".")[-1]
    if extension.lower() not in ["jpg", "png", "jpeg"]:
        raise HTTPException(400, "Format d'image non supporté")

    file_name = f"user_{user_id}_{secrets.token_hex(4)}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(404, "Utilisateur non trouvé")
        
    db_user.profile_photo = file_path
    db.commit()

    return {"info": "Photo de profil mise à jour", "path": file_path}


@router.delete("/delete-photo/{user_id}")
def delete_profile_photo(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(404, "Utilisateur non trouvé")
    
    if db_user.profile_photo and os.path.exists(db_user.profile_photo):
        try:
            os.remove(db_user.profile_photo)
        except Exception:
            pass

    db_user.profile_photo = None
    db.commit()

    return {"message": "Photo de profil supprimée"}


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    db_user = get_user_by_identifier(db, data.identifier)
    
    if not db_user:
        return {"message": "Si le compte existe, un code a été envoyé"}

    reset_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    
    db_user.reset_code = reset_code
    db.commit()

    is_email = re.match(r"[^@]+@[^@]+\.[^@]+", data.identifier)

    if is_email and db_user.email:
        await send_auth_email(
            email_to=db_user.email,
            subject="Réinitialisation de mot de passe",
            body=f"Votre code secret CHATBOX est : <b>{reset_code}</b>"
        )
        return {"message": "Code envoyé par email"}
    
    elif db_user.phone:

        send_sms_code(db_user.phone, reset_code)
        return {"message": "Code envoyé par SMS"}

    return {"message": "Aucun moyen de contact trouvé"}

@router.post("/reset-password")
def reset_password(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    user = get_user_by_identifier(db, data.identifier)
    
    if not user or user.reset_code != data.code:
        raise HTTPException(status_code=400, detail="Code de vérification invalide")
    
    user.password_hash = hash_password(data.new_password)
    user.reset_code = None 
    db.commit()
    
    return {"message": "Mot de passe mis à jour avec succès"}

@router.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):

    return db.query(User).all()