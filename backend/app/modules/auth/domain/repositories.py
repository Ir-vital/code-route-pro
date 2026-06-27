"""
Interfaces (ports) des repositories du module auth.
La couche application dépend de ces abstractions — jamais des implémentations SQLAlchemy.
"""

import uuid
from abc import ABC, abstractmethod

from app.modules.auth.domain.entities import (
    PasswordResetTokenEntity,
    RefreshTokenEntity,
    UserEntity,
)


class IUserRepository(ABC):

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None: ...

    @abstractmethod
    async def create(self, entity: UserEntity) -> UserEntity: ...

    @abstractmethod
    async def update(self, entity: UserEntity) -> UserEntity: ...

    @abstractmethod
    async def delete(self, user_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool: ...


class IRefreshTokenRepository(ABC):

    @abstractmethod
    async def create(self, entity: RefreshTokenEntity) -> RefreshTokenEntity: ...

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> RefreshTokenEntity | None: ...

    @abstractmethod
    async def revoke(self, token_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def delete_expired(self) -> int: ...


class IPasswordResetTokenRepository(ABC):

    @abstractmethod
    async def create(self, entity: PasswordResetTokenEntity) -> PasswordResetTokenEntity: ...

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> PasswordResetTokenEntity | None: ...

    @abstractmethod
    async def mark_used(self, token_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def delete_expired(self) -> int: ...
