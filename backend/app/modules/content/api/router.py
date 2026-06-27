"""Routers FastAPI du module content — /api/v1/categories, /api/v1/signs"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.api.dependencies import CurrentAdmin, CurrentUser
from app.modules.content.api.schemas import (
    CategoryResponse,
    CreateCategoryRequest,
    CreateSignRequest,
    FavoriteResponse,
    SignResponse,
    UpdateCategoryRequest,
    UpdateSignRequest,
)
from app.modules.content.application.dtos import (
    CreateCategoryDTO,
    CreateSignDTO,
    ListSignsDTO,
    UpdateCategoryDTO,
    UpdateSignDTO,
)
from app.modules.content.application.use_cases import (
    AddFavoriteUseCase,
    CreateCategoryUseCase,
    CreateSignUseCase,
    DeleteCategoryUseCase,
    DeleteSignUseCase,
    GetMyFavoritesUseCase,
    GetSignUseCase,
    ListCategoriesUseCase,
    ListSignsUseCase,
    RemoveFavoriteUseCase,
    UpdateCategoryUseCase,
    UpdateSignUseCase,
)
from app.modules.content.infrastructure.repositories import (
    CategoryRepository,
    FavoriteRepository,
    SignRepository,
)
from app.shared.domain.enums import Difficulty
from app.shared.pagination import PaginatedResponse, PaginationParams

# ─── Catégories ───────────────────────────────────────────────────────────────
categories_router = APIRouter(prefix="/categories", tags=["Content — Catégories"])


@categories_router.get("/", response_model=list[CategoryResponse])
async def list_categories(
    _user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_inactive: bool = Query(default=False),
) -> list[CategoryResponse]:
    uc = ListCategoriesUseCase(CategoryRepository(db))
    cats = await uc.execute(include_inactive=include_inactive)
    return [CategoryResponse(id=c.id, name=c.name, slug=c.slug, description=c.description,
                              icon=c.icon, color=c.color, display_order=c.display_order,
                              is_active=c.is_active) for c in cats]


@categories_router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    body: CreateCategoryRequest,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryResponse:
    uc = CreateCategoryUseCase(CategoryRepository(db))
    c = await uc.execute(CreateCategoryDTO(**body.model_dump()))
    return CategoryResponse(id=c.id, name=c.name, slug=c.slug, description=c.description,
                             icon=c.icon, color=c.color, display_order=c.display_order,
                             is_active=c.is_active)


@categories_router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    body: UpdateCategoryRequest,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryResponse:
    uc = UpdateCategoryUseCase(CategoryRepository(db))
    c = await uc.execute(UpdateCategoryDTO(category_id=category_id, **body.model_dump()))
    return CategoryResponse(id=c.id, name=c.name, slug=c.slug, description=c.description,
                             icon=c.icon, color=c.color, display_order=c.display_order,
                             is_active=c.is_active)


@categories_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await DeleteCategoryUseCase(CategoryRepository(db)).execute(category_id)


# ─── Panneaux ─────────────────────────────────────────────────────────────────
signs_router = APIRouter(prefix="/signs", tags=["Content — Panneaux"])


@signs_router.get("/", response_model=PaginatedResponse[SignResponse])
async def list_signs(
    _user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category_id: uuid.UUID | None = Query(default=None),
    difficulty: Difficulty | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
) -> PaginatedResponse[SignResponse]:
    params = PaginationParams(page=page, page_size=page_size)
    uc = ListSignsUseCase(SignRepository(db))
    signs, total = await uc.execute(
        ListSignsDTO(
            offset=params.offset, limit=params.limit,
            category_id=category_id, difficulty=difficulty, search=search,
        )
    )
    items = [SignResponse(id=s.id, category_id=s.category_id, name=s.name,
                          official_code=s.official_code, image_url=s.image_url,
                          meaning=s.meaning, rules=s.rules, difficulty=s.difficulty,
                          is_active=s.is_active) for s in signs]
    return PaginatedResponse.create(items=items, total=total, params=params)


@signs_router.get("/{sign_id}", response_model=SignResponse)
async def get_sign(
    sign_id: uuid.UUID,
    _user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SignResponse:
    s = await GetSignUseCase(SignRepository(db)).execute(sign_id)
    return SignResponse(id=s.id, category_id=s.category_id, name=s.name,
                        official_code=s.official_code, image_url=s.image_url,
                        meaning=s.meaning, rules=s.rules, difficulty=s.difficulty,
                        is_active=s.is_active)


@signs_router.post("/", response_model=SignResponse, status_code=status.HTTP_201_CREATED)
async def create_sign(
    body: CreateSignRequest,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SignResponse:
    uc = CreateSignUseCase(SignRepository(db), CategoryRepository(db))
    s = await uc.execute(CreateSignDTO(**body.model_dump()))
    return SignResponse(id=s.id, category_id=s.category_id, name=s.name,
                        official_code=s.official_code, image_url=s.image_url,
                        meaning=s.meaning, rules=s.rules, difficulty=s.difficulty,
                        is_active=s.is_active)


@signs_router.patch("/{sign_id}", response_model=SignResponse)
async def update_sign(
    sign_id: uuid.UUID,
    body: UpdateSignRequest,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SignResponse:
    uc = UpdateSignUseCase(SignRepository(db))
    s = await uc.execute(UpdateSignDTO(sign_id=sign_id, **body.model_dump()))
    return SignResponse(id=s.id, category_id=s.category_id, name=s.name,
                        official_code=s.official_code, image_url=s.image_url,
                        meaning=s.meaning, rules=s.rules, difficulty=s.difficulty,
                        is_active=s.is_active)


@signs_router.delete("/{sign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sign(
    sign_id: uuid.UUID,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await DeleteSignUseCase(SignRepository(db)).execute(sign_id)


@signs_router.post("/{sign_id}/favorite", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    sign_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FavoriteResponse:
    uc = AddFavoriteUseCase(FavoriteRepository(db), SignRepository(db))
    fav = await uc.execute(current_user.id, sign_id)
    return FavoriteResponse(id=fav.id, sign_id=fav.sign_id, created_at=fav.created_at)


@signs_router.delete("/{sign_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    sign_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await RemoveFavoriteUseCase(FavoriteRepository(db)).execute(current_user.id, sign_id)


# ─── Favoris de l'utilisateur courant ────────────────────────────────────────
favorites_router = APIRouter(prefix="/users/me/favorites", tags=["Content — Favoris"])


@favorites_router.get("/", response_model=PaginatedResponse[FavoriteResponse])
async def my_favorites(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[FavoriteResponse]:
    params = PaginationParams(page=page, page_size=page_size)
    uc = GetMyFavoritesUseCase(FavoriteRepository(db))
    favs, total = await uc.execute(current_user.id, offset=params.offset, limit=params.limit)
    items = [FavoriteResponse(id=f.id, sign_id=f.sign_id, created_at=f.created_at) for f in favs]
    return PaginatedResponse.create(items=items, total=total, params=params)
