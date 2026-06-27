"""
Entités du domaine auth.
Objets Python purs — aucune dépendance SQLAlchemy ou FastAPI.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.shared.domain.enums import UserRole


@dataclass
class UserEntity:
    """Représentation métier d'un utilisateur."""

    email: str
    hashed_password: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.STUDENT
    is_active: bool = True
    is_verified: bool = False
    avatar_url: str | None = None
    last_login_at: datetime | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def can_login(self) -> bool:
        return self.is_active


@dataclass
class RefreshTokenEntity:
    """Token de rafraîchissement JWT persisté."""

    user_id: uuid.UUID
    token_hash: str
    expires_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    revoked_at: datetime | None = None
    user_agent: str | None = None
    ip_address: str | None = None
    created_at: datetime | None = None

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def is_expired(self) -> bool:
        from datetime import UTC
        return datetime.now(UTC) > self.expires_at.replace(tzinfo=UTC if self.expires_at.tzinfo is None else None) if self.expires_at.tzinfo is None else datetime.now(UTC) > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_revoked and not self.is_expired


@dataclass
class PasswordResetTokenEntity:
    """Token de réinitialisation de mot de passe."""

    user_id: uuid.UUID
    token_hash: str
    expires_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    used_at: datetime | None = None
    created_at: datetime | None = None

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        from datetime import UTC
        now = datetime.now(UTC)
        exp = self.expires_at if self.expires_at.tzinfo else self.expires_at.replace(tzinfo=UTC)
        return now > exp

    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired
