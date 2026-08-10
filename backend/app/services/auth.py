from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: Optional[str]) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": subject, "exp": expire},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        sub = payload.get("sub")
        return str(sub) if sub else None
    except JWTError:
        return None


def register_user(
    db: Session,
    *,
    nom: str,
    prenom: str,
    ville: str,
    email: str,
    password: str,
) -> User:
    user = User(
        nom=nom.strip(),
        prenom=prenom.strip(),
        ville=ville.strip(),
        email=email.lower().strip(),
        hashed_password=hash_password(password),
        auth_provider="email",
        plan_type="standard_monthly",
        health_options=[],
        referral_credits=0,
        referrals_this_year=0,
        referral_free_years_claimed=0,
        gold_badges_count=0,
        ebook_unlocked=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_reset_token(db: Session, user: User) -> str:
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    return token


def reset_password(db: Session, token: str, new_password: str) -> Optional[User]:
    user = db.query(User).filter(User.reset_token == token).first()
    if not user or not user.reset_token_expires:
        return None
    if user.reset_token_expires < datetime.utcnow():
        return None
    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    db.refresh(user)
    return user


def social_login_or_register(
    db: Session,
    *,
    provider: str,
    email: str,
    nom: str = "Utilisateur",
    prenom: str = "HERITIA",
    ville: str = "À définir",
) -> User:
    """Stub social auth: trusts provider token verification upstream."""
    if provider not in ("google", "apple"):
        raise ValueError("Unsupported social provider")
    existing = db.query(User).filter(User.email == email.lower().strip()).first()
    if existing:
        return existing
    user = User(
        nom=nom,
        prenom=prenom,
        ville=ville,
        email=email.lower().strip(),
        hashed_password=None,
        auth_provider=provider,
        plan_type="standard_monthly",
        health_options=[],
        referral_credits=0,
        referrals_this_year=0,
        referral_free_years_claimed=0,
        gold_badges_count=0,
        ebook_unlocked=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user