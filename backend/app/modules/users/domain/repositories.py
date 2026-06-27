"""
Interfaces repository du module users.
Le module users réutilise UserEntity du module auth — les deux modules partagent
la même table `users` mais ont des responsabilités différentes :
- auth  : authentification, tokens, sessions
- users : gestion du profil, liste admin, avatar
"""

import uuid
from abc import ABC, abstractmethod

from app.modules.auth.domain.entities import UserEntity
from app.shared.domain.enums import UserRole


class IUsersRepository(ABC):

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None: ...

    @abstractmethod
    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        role: UserRole | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[UserEntity], int]: ...

    @abstractmethod
    async def update_profile(
        self,
        user_id: uuid.UUID,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        avatar_url: str | None = None,
    ) -> UserEntity: ...

    @abstractmethod
    async def set_active(self, user_id: uuid.UUID, is_active: bool) -> UserEntity: ...

    @abstractmethod
    async def delete(self, user_id: uuid.UUID) -> None: ...
