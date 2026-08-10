from __future__ import annotations

from typing import List

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


PRODUCTION_ORIGIN = "https://heritia.neriacorp.com"
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5174",
    PRODUCTION_ORIGIN,
    "https://heritia-web-production.up.railway.app",
]


class Settings(BaseSettings):
    app_name: str = "HERITIA"
    environment: str = "development"  # development | production
    app_base_url: str = PRODUCTION_ORIGIN
    secret_key: str = "heritia-dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "sqlite:///./heritia.db"
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    frontend_url: str = "http://localhost:5174"
    # Comma-separated string (Railway-safe). Avoid List[str] env JSON parsing issues.
    cors_origins: str = Field(
        default=",".join(DEFAULT_CORS_ORIGINS),
        description="Comma-separated allowed CORS origins",
    )

    class Config:
        env_prefix = "HERITIA_"
        env_file = ".env"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origin_list(self) -> List[str]:
        parts = [part.strip() for part in (self.cors_origins or "").split(",") if part.strip()]
        return parts or list(DEFAULT_CORS_ORIGINS)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    @property
    def public_app_url(self) -> str:
        if self.is_production:
            return self.app_base_url.rstrip("/")
        return self.frontend_url.rstrip("/")

    @property
    def stripe_return_url(self) -> str:
        return "{0}/gamification?stripe=return".format(self.public_app_url)

    @property
    def stripe_refresh_url(self) -> str:
        return "{0}/gamification?stripe=refresh".format(self.public_app_url)


settings = Settings()