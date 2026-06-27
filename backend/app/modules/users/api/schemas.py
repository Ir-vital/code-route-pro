"""Schémas Pydantic du module users."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.shared.domain.enums import UserRole


# ─── Requêtes ─────────────────────────────────────────────────────────────────

class UpdateMyProfileRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)


class AdminUpdateUserRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None


# ─── Réponses ─────────────────────────────────────────────────────────────────

class UserPublicResponse(BaseModel):
    """Profil public minimal (pour les listes, références)."""
    id: uuid.UUID
    first_name: str
    last_name: str
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class UserDetailResponse(BaseModel):
    """Profil complet (propre utilisateur ou admin)."""
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: str | None = None
    last_login_at: datetime | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Élément dans une liste d'utilisateurs (vue admin)."""
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    last_login_at: datetime | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
