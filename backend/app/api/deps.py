from __future__ import annotations

import secrets
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services import auth as auth_service

security = HTTPBearer(auto_error=False)
MASTER_KEY_HEADER = "X-Master-Key"


def verify_master_key(
    x_master_key: Optional[str] = Header(default=None, alias=MASTER_KEY_HEADER),
) -> None:
    """Require a valid NeriaCorp master key on N2 server-to-server routes."""
    if not settings.master_key_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Master key is not configured on the server",
        )
    if not x_master_key or not secrets.compare_digest(x_master_key, settings.master_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Master-Key",
        )


def verify_master_key_optional(
    x_master_key: Optional[str] = Header(default=None, alias=MASTER_KEY_HEADER),
) -> bool:
    """Return True when X-Master-Key matches (non-production webhook testing)."""
    if not settings.master_key_configured or not x_master_key:
        return False
    return secrets.compare_digest(x_master_key, settings.master_key)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = auth_service.decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user