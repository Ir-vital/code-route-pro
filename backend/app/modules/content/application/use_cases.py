"""Use cases du module content."""

import uuid

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.content.application.dtos import (
    CreateCategoryDTO,
    CreateSignDTO,
    ListSignsDTO,
    UpdateCategoryDTO,
    UpdateSignDTO,
)
from app.modules.content.domain.entities import CategoryEntity, FavoriteEntity, SignEntity
from app.modules.content.domain.repositories import (
    ICategoryRepository,
    IFavoriteRepository,
    ISignRepository,
)


# ─── Catégories ───────────────────────────────────────────────────────────────

class ListCategoriesUseCase:
    def __init__(self, repo: ICategoryRepository) -> None:
        self._repo = repo

    async def execute(self, include_inactive: bool = False) -> list[CategoryEntity]:
        return await self._repo.get_all(include_inactive=include_inactive)


class GetCategoryUseCase:
    def __init__(self, repo: ICategoryRepository) -> None:
        self._repo = repo

    async def execute(self, category_id: uuid.UUID) -> CategoryEntity:
        cat = await self._repo.get_by_id(category_id)
        if not cat:
            raise NotFoundException("Catégorie", str(category_id))
        return cat


class CreateCategoryUseCase:
    def __init__(self, repo: ICategoryRepository) -> None:
        self._repo = repo

    async def execute(self, dto: CreateCategoryDTO) -> CategoryEntity:
        if await self._repo.slug_exists(dto.slug):
            raise ConflictException(f"Le slug '{dto.slug}' est déjà utilisé")
        entity = CategoryEntity(
            name=dto.name,
            slug=dto.slug,
            description=dto.description,
            icon=dto.icon,
            color=dto.color,
            display_order=dto.display_order,
        )
        return await self._repo.create(entity)


class UpdateCategoryUseCase:
    def __init__(self, repo: ICategoryRepository) -> None:
        self._repo = repo

    async def execute(self, dto: UpdateCategoryDTO) -> CategoryEntity:
        cat = await self._repo.get_by_id(dto.category_id)
        if not cat:
            raise NotFoundException("Catégorie", str(dto.category_id))

        if dto.slug and dto.slug != cat.slug:
            if await self._repo.slug_exists(dto.slug, exclude_id=dto.category_id):
                raise ConflictException(f"Le slug '{dto.slug}' est déjà utilisé")
            cat.slug = dto.slug

        if dto.name is not None:
            cat.name = dto.name
        if dto.description is not None:
            cat.description = dto.description
        if dto.icon is not None:
            cat.icon = dto.icon
        if dto.color is not None:
            cat.color = dto.color
        if dto.display_order is not None:
            cat.display_order = dto.display_order
        if dto.is_active is not None:
            cat.is_active = dto.is_active

        return await self._repo.update(cat)


class DeleteCategoryUseCase:
    def __init__(self, repo: ICategoryRepository) -> None:
        self._repo = repo

    async def execute(self, category_id: uuid.UUID) -> None:
        if not await self._repo.get_by_id(category_id):
            raise NotFoundException("Catégorie", str(category_id))
        await self._repo.delete(category_id)


# ─── Panneaux ─────────────────────────────────────────────────────────────────

class ListSignsUseCase:
    def __init__(self, repo: ISignRepository) -> None:
        self._repo = repo

    async def execute(self, dto: ListSignsDTO) -> tuple[list[SignEntity], int]:
        return await self._repo.get_all(
            offset=dto.offset,
            limit=dto.limit,
            category_id=dto.category_id,
            difficulty=dto.difficulty,
            search=dto.search,
        )


class GetSignUseCase:
    def __init__(self, repo: ISignRepository) -> None:
        self._repo = repo

    async def execute(self, sign_id: uuid.UUID) -> SignEntity:
        sign = await self._repo.get_by_id(sign_id)
        if not sign:
            raise NotFoundException("Panneau", str(sign_id))
        return sign


class CreateSignUseCase:
    def __init__(self, sign_repo: ISignRepository, category_repo: ICategoryRepository) -> None:
        self._sign_repo = sign_repo
        self._category_repo = category_repo

    async def execute(self, dto: CreateSignDTO) -> SignEntity:
        if not await self._category_repo.get_by_id(dto.category_id):
            raise NotFoundException("Catégorie", str(dto.category_id))
        entity = SignEntity(
            category_id=dto.category_id,
            name=dto.name,
            image_url=dto.image_url,
            meaning=dto.meaning,
            official_code=dto.official_code,
            rules=dto.rules,
            difficulty=dto.difficulty,
        )
        return await self._sign_repo.create(entity)


class UpdateSignUseCase:
    def __init__(self, repo: ISignRepository) -> None:
        self._repo = repo

    async def execute(self, dto: UpdateSignDTO) -> SignEntity:
        sign = await self._repo.get_by_id(dto.sign_id)
        if not sign:
            raise NotFoundException("Panneau", str(dto.sign_id))

        if dto.name is not None:
            sign.name = dto.name
        if dto.image_url is not None:
            sign.image_url = dto.image_url
        if dto.meaning is not None:
            sign.meaning = dto.meaning
        if dto.official_code is not None:
            sign.official_code = dto.official_code
        if dto.rules is not None:
            sign.rules = dto.rules
        if dto.difficulty is not None:
            sign.difficulty = dto.difficulty
        if dto.is_active is not None:
            sign.is_active = dto.is_active
        if dto.category_id is not None:
            sign.category_id = dto.category_id

        return await self._repo.update(sign)


class DeleteSignUseCase:
    def __init__(self, repo: ISignRepository) -> None:
        self._repo = repo

    async def execute(self, sign_id: uuid.UUID) -> None:
        if not await self._repo.get_by_id(sign_id):
            raise NotFoundException("Panneau", str(sign_id))
        await self._repo.delete(sign_id)


# ─── Favoris ──────────────────────────────────────────────────────────────────

class GetMyFavoritesUseCase:
    def __init__(self, repo: IFavoriteRepository) -> None:
        self._repo = repo

    async def execute(
        self, user_id: uuid.UUID, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[FavoriteEntity], int]:
        return await self._repo.get_by_user(user_id, offset=offset, limit=limit)


class AddFavoriteUseCase:
    def __init__(
        self, fav_repo: IFavoriteRepository, sign_repo: ISignRepository
    ) -> None:
        self._fav_repo = fav_repo
        self._sign_repo = sign_repo

    async def execute(self, user_id: uuid.UUID, sign_id: uuid.UUID) -> FavoriteEntity:
        if not await self._sign_repo.get_by_id(sign_id):
            raise NotFoundException("Panneau", str(sign_id))
        if await self._fav_repo.exists(user_id, sign_id):
            raise ConflictException("Ce panneau est déjà dans vos favoris")
        entity = FavoriteEntity(user_id=user_id, sign_id=sign_id)
        return await self._fav_repo.add(entity)


class RemoveFavoriteUseCase:
    def __init__(self, repo: IFavoriteRepository) -> None:
        self._repo = repo

    async def execute(self, user_id: uuid.UUID, sign_id: uuid.UUID) -> None:
        if not await self._repo.exists(user_id, sign_id):
            raise NotFoundException("Favori")
        await self._repo.remove(user_id, sign_id)
