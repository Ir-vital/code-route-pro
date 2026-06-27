"""
Implémentations SQLAlchemy des repositories du module auth.
Ces classes implémentent les interfaces définies dans domain/repositories.py.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.domain.entities import (
    PasswordResetTokenEntity,
    RefreshTokenEntity,
    UserEntity,
)
from app.modules.auth.domain.repositories import (
    IPasswordResetTokenRepository,
    IRefreshTokenRepository,
    IUserRepository,
)
from app.modules.auth.infrastructure.models import (
    PasswordResetTokenModel,
    RefreshTokenModel,
    UserModel,
)
from app.shared.domain.enums import UserRole


# ─── Mappers (Model ↔ Entity) ─────────────────────────────────────────────────

def _user_to_entity(m: UserModel) -> UserEntity:
    return UserEntity(
        id=m.id,
        email=m.email,
        hashed_password=m.hashed_password,
        first_name=m.first_name,
        last_name=m.last_name,
        avatar_url=m.avatar_url,
        role=UserRole(m.role),
        is_active=m.is_active,
        is_verified=m.is_verified,
        last_login_at=m.last_login_at,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _entity_to_user_model(e: UserEntity) -> UserModel:
    m = UserModel()
    m.id = e.id
    m.email = e.email
    m.hashed_password = e.hashed_password
    m.first_name = e.first_name
    m.last_name = e.last_name
    m.avatar_url = e.avatar_url
    m.role = e.role
    m.is_active = e.is_active
    m.is_verified = e.is_verified
    m.last_login_at = e.last_login_at
    return m


def _refresh_to_entity(m: RefreshTokenModel) -> RefreshTokenEntity:
    return RefreshTokenEntity(
        id=m.id,
        user_id=m.user_id,
        token_hash=m.token_hash,
        expires_at=m.expires_at,
        revoked_at=m.revoked_at,
        user_agent=m.user_agent,
        ip_address=m.ip_address,
        created_at=m.created_at,
    )


def _reset_to_entity(m: PasswordResetTokenModel) -> PasswordResetTokenEntity:
    return PasswordResetTokenEntity(
        id=m.id,
        user_id=m.user_id,
        token_hash=m.token_hash,
        expires_at=m.expires_at,
        used_at=m.used_at,
        created_at=m.created_at,
    )


# ─── Repositories ─────────────────────────────────────────────────────────────

class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        m = result.scalar_one_or_none()
        return _user_to_entity(m) if m else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        m = result.scalar_one_or_none()
        return _user_to_entity(m) if m else None

    async def create(self, entity: UserEntity) -> UserEntity:
        m = _entity_to_user_model(entity)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _user_to_entity(m)

    async def update(self, entity: UserEntity) -> UserEntity:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == entity.id)
        )
        m = result.scalar_one_or_none()
        if not m:
            return entity
        m.email = entity.email
        m.hashed_password = entity.hashed_password
        m.first_name = entity.first_name
        m.last_name = entity.last_name
        m.avatar_url = entity.avatar_url
        m.role = entity.role
        m.is_active = entity.is_active
        m.is_verified = entity.is_verified
        m.last_login_at = entity.last_login_at
        await self._session.flush()
        await self._session.refresh(m)
        return _user_to_entity(m)

    async def delete(self, user_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        m = result.scalar_one_or_none()
        if m:
            await self._session.delete(m)
            await self._session.flush()

    async def email_exists(self, email: str) -> bool:
        result = await self._session.execute(
            select(UserModel.id).where(UserModel.email == email.lower())
        )
        return result.scalar_one_or_none() is not None


class RefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, entity: RefreshTokenEntity) -> RefreshTokenEntity:
        m = RefreshTokenModel()
        m.id = entity.id
        m.user_id = entity.user_id
        m.token_hash = entity.token_hash
        m.expires_at = entity.expires_at
        m.user_agent = entity.user_agent
        m.ip_address = entity.ip_address
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _refresh_to_entity(m)

    async def get_by_token_hash(self, token_hash: str) -> RefreshTokenEntity | None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        m = result.scalar_one_or_none()
        return _refresh_to_entity(m) if m else None

    async def revoke(self, token_id: uuid.UUID) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id)
            .values(revoked_at=datetime.now(UTC))
        )

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )

    async def delete_expired(self) -> int:
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.expires_at < datetime.now(UTC)
            )
        )
        expired = result.scalars().all()
        for m in expired:
            await self._session.delete(m)
        return len(expired)


class PasswordResetTokenRepository(IPasswordResetTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, entity: PasswordResetTokenEntity) -> PasswordResetTokenEntity:
        m = PasswordResetTokenModel()
        m.id = entity.id
        m.user_id = entity.user_id
        m.token_hash = entity.token_hash
        m.expires_at = entity.expires_at
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _reset_to_entity(m)

    async def get_by_token_hash(self, token_hash: str) -> PasswordResetTokenEntity | None:
        result = await self._session.execute(
            select(PasswordResetTokenModel).where(
                PasswordResetTokenModel.token_hash == token_hash
            )
        )
        m = result.scalar_one_or_none()
        return _reset_to_entity(m) if m else None

    async def mark_used(self, token_id: uuid.UUID) -> None:
        await self._session.execute(
            update(PasswordResetTokenModel)
            .where(PasswordResetTokenModel.id == token_id)
            .values(used_at=datetime.now(UTC))
        )

    async def delete_expired(self) -> int:
        result = await self._session.execute(
            select(PasswordResetTokenModel).where(
                PasswordResetTokenModel.expires_at < datetime.now(UTC)
            )
        )
        expired = result.scalars().all()
        for m in expired:
            await self._session.delete(m)
        return len(expired)
