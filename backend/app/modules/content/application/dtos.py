"""DTOs internes du module content."""

import uuid
from dataclasses import dataclass

from app.shared.domain.enums import Difficulty


@dataclass
class CreateCategoryDTO:
    name: str
    slug: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    display_order: int = 0


@dataclass
class UpdateCategoryDTO:
    category_id: uuid.UUID
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    display_order: int | None = None
    is_active: bool | None = None


@dataclass
class CreateSignDTO:
    category_id: uuid.UUID
    name: str
    image_url: str
    meaning: str
    official_code: str | None = None
    rules: str | None = None
    difficulty: Difficulty = Difficulty.EASY


@dataclass
class UpdateSignDTO:
    sign_id: uuid.UUID
    name: str | None = None
    image_url: str | None = None
    meaning: str | None = None
    official_code: str | None = None
    rules: str | None = None
    difficulty: Difficulty | None = None
    is_active: bool | None = None
    category_id: uuid.UUID | None = None


@dataclass
class ListSignsDTO:
    offset: int = 0
    limit: int = 20
    category_id: uuid.UUID | None = None
    difficulty: Difficulty | None = None
    search: str | None = None
