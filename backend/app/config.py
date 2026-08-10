from __future__ import annotations

import json
from typing import Any, List, Union

from pydantic import Field, field_validator
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
    # Dev frontend; production uses app_base_url for Stripe return links
    frontend_url: str = "http://localhost:5174"
    cors_origins: List[str] = Field(default_factory=lambda: list(DEFAULT_CORS_ORIGINS))

    class Config:
        env_prefix = "HERITIA_"
        env_file = ".env"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Union[List[str], Any]:
        if value is None or value == "":
            return list(DEFAULT_CORS_ORIGINS)
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("["):
                return json.loads(text)
            return [part.strip() for part in text.split(",") if part.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    @property
    def public_app_url(self) -> str:
        """Canonical public URL used for Stripe OAuth return/refresh links."""
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