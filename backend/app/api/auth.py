from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SocialLoginRequest,
    TokenResponse,
)
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = auth_service.register_user(
        db,
        nom=payload.nom,
        prenom=payload.prenom,
        ville=payload.ville,
        email=payload.email,
        password=payload.password,
    )
    return TokenResponse(access_token=auth_service.create_access_token(str(user.id)))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=auth_service.create_access_token(str(user.id)))


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    # Always return ok to avoid email enumeration
    if not user:
        return {"ok": True, "message": "If the email exists, a reset link was sent."}
    token = auth_service.create_reset_token(db, user)
    # Dev stub: return token (replace with email delivery in production)
    return {
        "ok": True,
        "message": "If the email exists, a reset link was sent.",
        "dev_reset_token": token,
    }


@router.post("/reset-password", response_model=TokenResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = auth_service.reset_password(db, payload.token, payload.new_password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    return TokenResponse(access_token=auth_service.create_access_token(str(user.id)))


@router.post("/social", response_model=TokenResponse)
def social_login(payload: SocialLoginRequest, db: Session = Depends(get_db)):
    """Google / Apple social login stub — wire real token verification later."""
    if payload.provider not in ("google", "apple"):
        raise HTTPException(status_code=400, detail="provider must be google or apple")
    if not payload.id_token:
        raise HTTPException(status_code=400, detail="id_token required")
    if not payload.email:
        raise HTTPException(status_code=400, detail="email required for social bootstrap")
    try:
        user = auth_service.social_login_or_register(
            db,
            provider=payload.provider,
            email=payload.email,
            nom=payload.nom or "Utilisateur",
            prenom=payload.prenom or "HERITIA",
            ville=payload.ville or "À définir",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return TokenResponse(access_token=auth_service.create_access_token(str(user.id)))