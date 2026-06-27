"""Implémentations SQLAlchemy des repositories du module content."""

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.domain.entities import CategoryEntity, FavoriteEntity, SignEntity
from app.modules.content.domain.repositories import (
    ICategoryRepository,
    IFavoriteRepository,
    ISignRepository,
)
from app.modules.content.infrastructure.models import CategoryModel, FavoriteModel, SignModel
from app.shared.domain.enums import Difficulty


# ─── Mappers ──────────────────────────────────────────────────────────────────

def _cat_to_entity(m: CategoryModel) -> CategoryEntity:
    return CategoryEntity(
        id=m.id, name=m.name, slug=m.slug, description=m.description,
        icon=m.icon, color=m.color, display_order=m.display_order,
        is_active=m.is_active, created_at=m.created_at, updated_at=m.updated_at,
    )


def _sign_to_entity(m: SignModel) -> SignEntity:
    return SignEntity(
        id=m.id, category_id=m.category_id, name=m.name,
        official_code=m.official_code, image_url=m.image_url,
        meaning=m.meaning, rules=m.rules, difficulty=Difficulty(m.difficulty),
        is_active=m.is_active, created_at=m.created_at, updated_at=m.updated_at,
    )


def _fav_to_entity(m: FavoriteModel) -> FavoriteEntity:
    return FavoriteEntity(
        id=m.id, user_id=m.user_id, sign_id=m.sign_id, created_at=m.created_at
    )


# ─── CategoryRepository ───────────────────────────────────────────────────────

class CategoryRepository(ICategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self, *, include_inactive: bool = False) -> list[CategoryEntity]:
        q = select(CategoryModel).order_by(CategoryModel.display_order)
        if not include_inactive:
            q = q.where(CategoryModel.is_active == True)  # noqa: E712
        result = await self._session.execute(q)
        return [_cat_to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, category_id: uuid.UUID) -> CategoryEntity | None:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        m = result.scalar_one_or_none()
        return _cat_to_entity(m) if m else None

    async def get_by_slug(self, slug: str) -> CategoryEntity | None:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.slug == slug)
        )
        m = result.scalar_one_or_none()
        return _cat_to_entity(m) if m else None

    async def create(self, entity: CategoryEntity) -> CategoryEntity:
        m = CategoryModel()
        m.id = entity.id
        m.name = entity.name
        m.slug = entity.slug
        m.description = entity.description
        m.icon = entity.icon
        m.color = entity.color
        m.display_order = entity.display_order
        m.is_active = entity.is_active
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _cat_to_entity(m)

    async def update(self, entity: CategoryEntity) -> CategoryEntity:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.id == entity.id)
        )
        m = result.scalar_one()
        m.name = entity.name
        m.slug = entity.slug
        m.description = entity.description
        m.icon = entity.icon
        m.color = entity.color
        m.display_order = entity.display_order
        m.is_active = entity.is_active
        await self._session.flush()
        await self._session.refresh(m)
        return _cat_to_entity(m)

    async def delete(self, category_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        m = result.scalar_one_or_none()
        if m:
            await self._session.delete(m)
            await self._session.flush()

    async def slug_exists(self, slug: str, exclude_id: uuid.UUID | None = None) -> bool:
        q = select(CategoryModel.id).where(CategoryModel.slug == slug)
        if exclude_id:
            q = q.where(CategoryModel.id != exclude_id)
        result = await self._session.execute(q)
        return result.scalar_one_or_none() is not None


# ─── SignRepository ───────────────────────────────────────────────────────────

class SignRepository(ISignRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        category_id: uuid.UUID | None = None,
        difficulty: Difficulty | None = None,
        search: str | None = None,
        include_inactive: bool = False,
    ) -> tuple[list[SignEntity], int]:
        q = select(SignModel)
        cq = select(func.count()).select_from(SignModel)

        if not include_inactive:
            q = q.where(SignModel.is_active == True)  # noqa: E712
            cq = cq.where(SignModel.is_active == True)  # noqa: E712
        if category_id:
            q = q.where(SignModel.category_id == category_id)
            cq = cq.where(SignModel.category_id == category_id)
        if difficulty:
            q = q.where(SignModel.difficulty == difficulty)
            cq = cq.where(SignModel.difficulty == difficulty)
        if search:
            pattern = f"%{search}%"
            cond = or_(SignModel.name.ilike(pattern), SignModel.official_code.ilike(pattern))
            q = q.where(cond)
            cq = cq.where(cond)

        total = (await self._session.execute(cq)).scalar_one()
        q = q.offset(offset).limit(limit).order_by(SignModel.name)
        models = (await self._session.execute(q)).scalars().all()
        return [_sign_to_entity(m) for m in models], total

    async def get_by_id(self, sign_id: uuid.UUID) -> SignEntity | None:
        result = await self._session.execute(
            select(SignModel).where(SignModel.id == sign_id)
        )
        m = result.scalar_one_or_none()
        return _sign_to_entity(m) if m else None

    async def create(self, entity: SignEntity) -> SignEntity:
        m = SignModel()
        m.id = entity.id
        m.category_id = entity.category_id
        m.name = entity.name
        m.official_code = entity.official_code
        m.image_url = entity.image_url
        m.meaning = entity.meaning
        m.rules = entity.rules
        m.difficulty = entity.difficulty
        m.is_active = entity.is_active
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _sign_to_entity(m)

    async def update(self, entity: SignEntity) -> SignEntity:
        result = await self._session.execute(
            select(SignModel).where(SignModel.id == entity.id)
        )
        m = result.scalar_one()
        m.category_id = entity.category_id
        m.name = entity.name
        m.official_code = entity.official_code
        m.image_url = entity.image_url
        m.meaning = entity.meaning
        m.rules = entity.rules
        m.difficulty = entity.difficulty
        m.is_active = entity.is_active
        await self._session.flush()
        await self._session.refresh(m)
        return _sign_to_entity(m)

    async def delete(self, sign_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(SignModel).where(SignModel.id == sign_id)
        )
        m = result.scalar_one_or_none()
        if m:
            await self._session.delete(m)
            await self._session.flush()


# ─── FavoriteRepository ───────────────────────────────────────────────────────

class FavoriteRepository(IFavoriteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[FavoriteEntity], int]:
        cq = select(func.count()).select_from(FavoriteModel).where(FavoriteModel.user_id == user_id)
        total = (await self._session.execute(cq)).scalar_one()
        q = (
            select(FavoriteModel)
            .where(FavoriteModel.user_id == user_id)
            .offset(offset)
            .limit(limit)
            .order_by(FavoriteModel.created_at.desc())
        )
        models = (await self._session.execute(q)).scalars().all()
        return [_fav_to_entity(m) for m in models], total

    async def exists(self, user_id: uuid.UUID, sign_id: uuid.UUID) -> bool:
        result = await self._session.execute(
            select(FavoriteModel.id).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.sign_id == sign_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def add(self, entity: FavoriteEntity) -> FavoriteEntity:
        m = FavoriteModel()
        m.id = entity.id
        m.user_id = entity.user_id
        m.sign_id = entity.sign_id
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _fav_to_entity(m)

    async def remove(self, user_id: uuid.UUID, sign_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.sign_id == sign_id,
            )
        )
        m = result.scalar_one_or_none()
        if m:
            await self._session.delete(m)
            await self._session.flush()
