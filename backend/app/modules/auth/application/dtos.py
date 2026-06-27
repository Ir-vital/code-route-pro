"""DTOs internes du module auth (objets de transfert entre couches application ↔ api)."""

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.shared.domain.enums import UserRole


@dataclass
class RegisterDTO:
    email: str
    password: str
    first_name: str
    last_name: str


@dataclass
class LoginDTO:
    email: str
    password: str
    user_agent: str | None = None
    ip_address: str | None = None


@dataclass
class TokenPairDTO:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class AuthUserDTO:
    """Résultat d'une authentification réussie."""
    user_id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    tokens: TokenPairDTO


@dataclass
class RefreshTokenDTO:
    refresh_token: str
    user_agent: str | None = None
    ip_address: str | None = None


@dataclass
class ForgotPasswordDTO:
    email: str


@dataclass
class ResetPasswordDTO:
    token: str
    new_password: str


@dataclass
class ChangePasswordDTO:
    user_id: uuid.UUID
    current_password: str
    new_password: str
