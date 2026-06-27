"""Router FastAPI du module users — /api/v1/users"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.api.dependencies import CurrentAdmin, CurrentUser
from app.modules.auth.application.dtos import ChangePasswordDTO
from app.modules.auth.application.use_cases import ChangePasswordUseCase
from app.modules.auth.infrastructure.repositories import UserRepository
from app.modules.users.api.schemas import (
    AdminUpdateUserRequest,
    UpdateMyProfileRequest,
    UserDetailResponse,
    UserListResponse,
)
from app.modules.users.application.dtos import (
    AdminUpdateUserDTO,
    ListUsersDTO,
    UpdateAvatarDTO,
    UpdateProfileDTO,
)
from app.modules.users.application.use_cases import (
    AdminUpdateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateMyProfileUseCase,
    UploadAvatarUseCase,
)
from app.modules.users.infrastructure.repository import UsersRepository
from app.modules.users.infrastructure.storage import SupabaseStorageService
from app.shared.domain.enums import UserRole
from app.shared.pagination import PaginatedResponse, PaginationParams
from app.modules.auth.api.schemas import MessageResponse
from pydantic import BaseModel, Field


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


router = APIRouter(prefix="/users", tags=["Users"])


# ─── Mon profil ───────────────────────────────────────────────────────────────

@router.patch("/me", response_model=UserDetailResponse, summary="Mettre à jour mon profil")
async def update_my_profile(
    body: UpdateMyProfileRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserDetailResponse:
    use_case = UpdateMyProfileUseCase(UsersRepository(db))
    user = await use_case.execute(
        UpdateProfileDTO(
            user_id=current_user.id,
            first_name=body.first_name,
            last_name=body.last_name,
        )
    )
    return UserDetailResponse(
        id=user.id, email=user.email, first_name=user.first_name,
        last_name=user.last_name, role=user.role, is_active=user.is_active,
        is_verified=user.is_verified, avatar_url=user.avatar_url,
        last_login_at=user.last_login_at, created_at=user.created_at,
    )


@router.patch("/me/password", response_model=MessageResponse, summary="Changer mon mot de passe")
async def change_my_password(
    body: ChangePasswordRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    use_case = ChangePasswordUseCase(UserRepository(db))
    await use_case.execute(
        ChangePasswordDTO(
            user_id=current_user.id,
            current_password=body.current_password,
            new_password=body.new_password,
        )
    )
    return MessageResponse(message="Mot de passe mis à jour avec succès.")


@router.post("/me/avatar", response_model=UserDetailResponse, summary="Uploader mon avatar")
async def upload_my_avatar(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
) -> UserDetailResponse:
    content = await file.read()
    use_case = UploadAvatarUseCase(UsersRepository(db), SupabaseStorageService())
    user = await use_case.execute(
        UpdateAvatarDTO(
            user_id=current_user.id,
            file_content=content,
            content_type=file.content_type or "image/jpeg",
            filename=file.filename or "avatar.jpg",
        )
    )
    return UserDetailResponse(
        id=user.id, email=user.email, first_name=user.first_name,
        last_name=user.last_name, role=user.role, is_active=user.is_active,
        is_verified=user.is_verified, avatar_url=user.avatar_url,
        last_login_at=user.last_login_at, created_at=user.created_at,
    )


# ─── Admin — liste & gestion utilisateurs ────────────────────────────────────

@router.get(
    "/",
    response_model=PaginatedResponse[UserListResponse],
    summary="[Admin] Liste des utilisateurs",
)
async def list_users(
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
) -> PaginatedResponse[UserListResponse]:
    params = PaginationParams(page=page, page_size=page_size)
    use_case = ListUsersUseCase(UsersRepository(db))
    users, total = await use_case.execute(
        ListUsersDTO(
            offset=params.offset,
            limit=params.limit,
            role=role,
            is_active=is_active,
            search=search,
        )
    )
    items = [
        UserListResponse(
            id=u.id, email=u.email, first_name=u.first_name, last_name=u.last_name,
            role=u.role, is_active=u.is_active, is_verified=u.is_verified,
            last_login_at=u.last_login_at, created_at=u.created_at,
        )
        for u in users
    ]
    return PaginatedResponse.create(items=items, total=total, params=params)


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="[Admin] Détail d'un utilisateur",
)
async def get_user(
    user_id: uuid.UUID,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserDetailResponse:
    use_case = GetUserUseCase(UsersRepository(db))
    user = await use_case.execute(user_id)
    return UserDetailResponse(
        id=user.id, email=user.email, first_name=user.first_name,
        last_name=user.last_name, role=user.role, is_active=user.is_active,
        is_verified=user.is_verified, avatar_url=user.avatar_url,
        last_login_at=user.last_login_at, created_at=user.created_at,
    )


@router.patch(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="[Admin] Modifier un utilisateur",
)
async def admin_update_user(
    user_id: uuid.UUID,
    body: AdminUpdateUserRequest,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserDetailResponse:
    use_case = AdminUpdateUserUseCase(UsersRepository(db))
    user = await use_case.execute(
        AdminUpdateUserDTO(
            user_id=user_id,
            first_name=body.first_name,
            last_name=body.last_name,
            is_active=body.is_active,
        )
    )
    return UserDetailResponse(
        id=user.id, email=user.email, first_name=user.first_name,
        last_name=user.last_name, role=user.role, is_active=user.is_active,
        is_verified=user.is_verified, avatar_url=user.avatar_url,
        last_login_at=user.last_login_at, created_at=user.created_at,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Supprimer un utilisateur",
)
async def delete_user(
    user_id: uuid.UUID,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    use_case = DeleteUserUseCase(UsersRepository(db))
    await use_case.execute(user_id)
