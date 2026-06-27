"""
Utilitaires de sécurité : hachage des mots de passe et gestion des JWT.
Le domaine n'importe jamais ce module directement — seule la couche application/infrastructure l'utilise.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ─── Hachage mots de passe ────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ─── JWT ─────────────────────────────────────────────────────────────────────

def create_access_token(subject: str | Any, extra_claims: dict | None = None) -> str:
    """Crée un access token JWT (courte durée de vie)."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    """Crée un refresh token JWT (longue durée de vie)."""
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: dict = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Décode et valide un token JWT.
    Lève JWTError si invalide ou expiré.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def verify_access_token(token: str) -> dict:
    """Vérifie qu'il s'agit bien d'un access token valide."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise JWTError("Token type mismatch: expected access token")
    return payload


def verify_refresh_token(token: str) -> dict:
    """Vérifie qu'il s'agit bien d'un refresh token valide."""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise JWTError("Token type mismatch: expected refresh token")
    return payload
