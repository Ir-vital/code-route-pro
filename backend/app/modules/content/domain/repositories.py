"""Interfaces repository du module content."""

import uuid
from abc import ABC, abstractmethod

from app.modules.content.domain.entities import CategoryEntity, FavoriteEntity, SignEntity
from app.shared.domain.enums import Difficulty


class ICategoryRepository(ABC):

    @abstractmethod
    async def get_all(self, *, include_inactive: bool = False) -> list[CategoryEntity]: ...

    @abstractmethod
    async def get_by_id(self, category_id: uuid.UUID) -> CategoryEntity | None: ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> CategoryEntity | None: ...

    @abstractmethod
    async def create(self, entity: CategoryEntity) -> CategoryEntity: ...

    @abstractmethod
    async def update(self, entity: CategoryEntity) -> CategoryEntity: ...

    @abstractmethod
    async def delete(self, category_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def slug_exists(self, slug: str, exclude_id: uuid.UUID | None = None) -> bool: ...


class ISignRepository(ABC):

    @abstractmethod
    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        category_id: uuid.UUID | None = None,
        difficulty: Difficulty | None = None,
        search: str | None = None,
        include_inactive: bool = False,
    ) -> tuple[list[SignEntity], int]: ...

    @abstractmethod
    async def get_by_id(self, sign_id: uuid.UUID) -> SignEntity | None: ...

    @abstractmethod
    async def create(self, entity: SignEntity) -> SignEntity: ...

    @abstractmethod
    async def update(self, entity: SignEntity) -> SignEntity: ...

    @abstractmethod
    async def delete(self, sign_id: uuid.UUID) -> None: ...


class IFavoriteRepository(ABC):

    @abstractmethod
    async def get_by_user(
        self,
        user_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[FavoriteEntity], int]: ...

    @abstractmethod
    async def exists(self, user_id: uuid.UUID, sign_id: uuid.UUID) -> bool: ...

    @abstractmethod
    async def add(self, entity: FavoriteEntity) -> FavoriteEntity: ...

    @abstractmethod
    async def remove(self, user_id: uuid.UUID, sign_id: uuid.UUID) -> None: ...
