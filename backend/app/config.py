from __future__ import annotations

from typing import List

from pydantic import AliasChoices, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


PRODUCTION_ORIGIN = "https://heritia.neriacorp.com"
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5174",
    PRODUCTION_ORIGIN,
    "https://heritia-web-production.up.railway.app",
]

JWT_ISSUER = "neriacorp"
JWT_AUDIENCE = "heritia"
JWT_APP = "HERITIA"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HERITIA_",
        env_file=".env",
        populate_by_name=True,
        extra="ignore",
    )

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
    cors_origins: str = Field(
        default=",".join(DEFAULT_CORS_ORIGINS),
        description="Comma-separated allowed CORS origins",
    )

    # N2 / shared NeriaCorp infrastructure (no HERITIA_ prefix)
    n2_master_key: str = Field(
        default="",
        validation_alias=AliasChoices("N2_MASTER_KEY", "NERIA_MASTER_KEY", "X_MASTER_KEY"),
    )
    resend_api_key: str = Field(default="", validation_alias="RESEND_API_KEY")
    resend_from_email: str = Field(
        default="heritia@neriacorp.com",
        validation_alias="RESEND_FROM_EMAIL",
    )
    cloudinary_cloud_name: str = Field(default="", validation_alias="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: str = Field(default="", validation_alias="CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = Field(default="", validation_alias="CLOUDINARY_API_SECRET")
    cloudinary_folder: str = Field(default="heritia", validation_alias="CLOUDINARY_FOLDER")
    firebase_project_id: str = Field(default="", validation_alias="FIREBASE_PROJECT_ID")
    firebase_credentials_json: str = Field(default="", validation_alias="FIREBASE_CREDENTIALS_JSON")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origin_list(self) -> List[str]:
        parts = [part.strip() for part in (self.cors_origins or "").split(",") if part.strip()]
        return parts or list(DEFAULT_CORS_ORIGINS)

    @property
    def master_key(self) -> str:
        """Shared NeriaCorp master key used for N2 server-to-server calls."""
        return self.n2_master_key

    @property
    def master_key_configured(self) -> bool:
        return bool(self.master_key)

    @property
    def jwt_secret(self) -> str:
        """Prefer N2 Master Key; fall back to local secret for development."""
        return self.master_key or self.secret_key

    @property
    def allow_master_key_webhook_bypass(self) -> bool:
        """Allow X-Master-Key instead of stripe-signature in non-production only."""
        return not self.is_production

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    @property
    def public_app_url(self) -> str:
        if self.is_production:
            return self.app_base_url.rstrip("/")
        return self.frontend_url.rstrip("/")

    @property
    def password_reset_url(self) -> str:
        return "{0}/forgot-password".format(self.public_app_url)

    @property
    def stripe_return_url(self) -> str:
        return "{0}/gamification?stripe=return".format(self.public_app_url)

    @property
    def stripe_refresh_url(self) -> str:
        return "{0}/gamification?stripe=refresh".format(self.public_app_url)

    @property
    def resend_configured(self) -> bool:
        return bool(self.resend_api_key and self.resend_from_email)

    @property
    def firebase_configured(self) -> bool:
        return bool(self.firebase_project_id)

    @property
    def cloudinary_configured(self) -> bool:
        return bool(
            self.cloudinary_cloud_name
            and self.cloudinary_api_key
            and self.cloudinary_api_secret
        )


settings = Settings()
