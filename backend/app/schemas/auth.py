from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    nom: str = Field(min_length=1, max_length=120)
    prenom: str = Field(min_length=1, max_length=120)
    ville: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class SocialLoginRequest(BaseModel):
    provider: str  # google | apple
    id_token: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    ville: Optional[str] = None
    email: Optional[EmailStr] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"