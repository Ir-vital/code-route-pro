"""DTOs internes du module users."""

import uuid
from dataclasses import dataclass

from app.shared.domain.enums import UserRole


@dataclass
class UpdateProfileDTO:
    user_id: uuid.UUID
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None


@dataclass
class UpdateAvatarDTO:
    user_id: uuid.UUID
    file_content: bytes
    content_type: str
    filename: str


@dataclass
class ListUsersDTO:
    offset: int = 0
    limit: int = 20
    role: UserRole | None = None
    is_active: bool | None = None
    search: str | None = None


@dataclass
class AdminUpdateUserDTO:
    user_id: uuid.UUID
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    role: UserRole | None = None
