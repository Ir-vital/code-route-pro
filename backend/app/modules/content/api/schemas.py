"""Schémas Pydantic du module content."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.shared.domain.enums import Difficulty


# ─── Catégories ───────────────────────────────────────────────────────────────

class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    display_order: int
    is_active: bool

    model_config = {"from_attributes": True}


class CreateCategoryRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    slug: str = Field(min_length=1, max_length=160, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    icon: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=20)
    display_order: int = 0


class UpdateCategoryRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    slug: str | None = Field(default=None, min_length=1, max_length=160, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    display_order: int | None = None
    is_active: bool | None = None


# ─── Panneaux ─────────────────────────────────────────────────────────────────

class SignResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    official_code: str | None = None
    image_url: str
    meaning: str
    rules: str | None = None
    difficulty: Difficulty
    is_active: bool

    model_config = {"from_attributes": True}


class CreateSignRequest(BaseModel):
    category_id: uuid.UUID
    name: str = Field(min_length=1, max_length=200)
    image_url: str = Field(max_length=500)
    meaning: str
    official_code: str | None = Field(default=None, max_length=50)
    rules: str | None = None
    difficulty: Difficulty = Difficulty.EASY


class UpdateSignRequest(BaseModel):
    category_id: uuid.UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    image_url: str | None = Field(default=None, max_length=500)
    meaning: str | None = None
    official_code: str | None = None
    rules: str | None = None
    difficulty: Difficulty | None = None
    is_active: bool | None = None


# ─── Favoris ──────────────────────────────────────────────────────────────────

class FavoriteResponse(BaseModel):
    id: uuid.UUID
    sign_id: uuid.UUID
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
