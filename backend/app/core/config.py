from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "CodeRoute Pro"
    APP_VERSION: str = "1.0.0"
    ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_OPENSSL_RAND_HEX_32"

    # ─── Server ───────────────────────────────────────────────────────────────
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # ─── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[AnyHttpUrl] = ["http://localhost:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | list) -> list:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ─── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://coderoute:coderoute_secret@localhost:5432/coderoute_db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_ECHO: bool = False

    # ─── Redis ────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://:redis_secret@localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # secondes

    # ─── JWT ──────────────────────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ─── Supabase Storage ─────────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_BUCKET_AVATARS: str = "avatars"
    SUPABASE_BUCKET_SIGNS: str = "signs"

    # ─── Email (SMTP) ─────────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_NAME: str = "CodeRoute Pro"
    EMAILS_FROM_ADDRESS: str = "noreply@codeRoutepro.fr"

    # ─── Email (Resend — prioritaire si défini) ───────────────────────────────
    RESEND_API_KEY: str = ""

    # ─── URL Frontend (pour les liens dans les emails) ───────────────────────
    FRONTEND_URL: str = "http://localhost:3000"

    # ─── Rate limiting ────────────────────────────────────────────────────────
    LOGIN_RATE_LIMIT: int = 10  # tentatives par fenêtre
    LOGIN_RATE_LIMIT_WINDOW: int = 300  # secondes

    # ─── Password reset ───────────────────────────────────────────────────────
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 2

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.ENV == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
