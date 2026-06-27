"""
Dépendances FastAPI du module auth.
- get_current_user  : extrait et valide le JWT, retourne l'utilisateur courant
- require_role      : vérifie le rôle de l'utilisateur
- get_current_admin : raccourci pour require_role(ADMIN)
"""

import uuid
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, InvalidTokenException, UnauthorizedException
from app.core.security import verify_access_token
from app.modules.auth.domain.entities import UserEntity
from app.modules.auth.infrastructure.repositories import UserRepository
from app.shared.domain.enums import UserRole

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserEntity:
    """
    Extrait le JWT du header Authorization, le valide, vérifie la blacklist Redis,
    et retourne l'utilisateur.
    """
    if not credentials:
        raise UnauthorizedException()

    token = credentials.credentials

    try:
        payload = verify_access_token(token)
    except JWTError:
        raise InvalidTokenException()

    # Vérifier la blacklist Redis (token révoqué lors du logout)
    try:
        from app.core.redis import get_redis_pool
        import hashlib
        redis = await get_redis_pool()
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if await redis.exists(f"blacklist:access:{token_hash}"):
            raise InvalidTokenException()
    except InvalidTokenException:
        raise
    except Exception:
        pass  # Redis indisponible → on laisse passer (fail-open)

    user_id = uuid.UUID(payload["sub"])
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException()
    if not user.is_active:
        raise ForbiddenException("Ce compte est désactivé")

    return user


def require_role(*roles: UserRole):
    """Factory de dépendance pour vérifier le rôle de l'utilisateur."""

    async def _check(
        current_user: Annotated[UserEntity, Depends(get_current_user)],
    ) -> UserEntity:
        if current_user.role not in roles:
            raise ForbiddenException()
        return current_user

    return _check


# Raccourcis
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]
CurrentAdmin = Annotated[UserEntity, Depends(require_role(UserRole.ADMIN))]
