"""Entités métier du module content."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.shared.domain.enums import Difficulty


@dataclass
class CategoryEntity:
    name: str
    slug: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    display_order: int = 0
    is_active: bool = True
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class SignEntity:
    category_id: uuid.UUID
    name: str
    image_url: str
    meaning: str
    official_code: str | None = None
    rules: str | None = None
    difficulty: Difficulty = Difficulty.EASY
    is_active: bool = True
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class FavoriteEntity:
    user_id: uuid.UUID
    sign_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
