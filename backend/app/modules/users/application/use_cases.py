"""Use cases du module users."""

import uuid
from abc import ABC, abstractmethod

from app.modules.auth.domain.entities import UserEntity
from app.modules.auth.domain.exceptions import UserNotFoundException
from app.modules.users.application.dtos import (
    AdminUpdateUserDTO,
    ListUsersDTO,
    UpdateAvatarDTO,
    UpdateProfileDTO,
)
from app.modules.users.domain.repositories import IUsersRepository
from app.shared.pagination import PaginatedResponse, PaginationParams


class GetUserUseCase:
    def __init__(self, repo: IUsersRepository) -> None:
        self._repo = repo

    async def execute(self, user_id: uuid.UUID) -> UserEntity:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        return user


class ListUsersUseCase:
    def __init__(self, repo: IUsersRepository) -> None:
        self._repo = repo

    async def execute(self, dto: ListUsersDTO) -> tuple[list[UserEntity], int]:
        return await self._repo.get_all(
            offset=dto.offset,
            limit=dto.limit,
            role=dto.role,
            is_active=dto.is_active,
            search=dto.search,
        )


class UpdateMyProfileUseCase:
    def __init__(self, repo: IUsersRepository) -> None:
        self._repo = repo

    async def execute(self, dto: UpdateProfileDTO) -> UserEntity:
        user = await self._repo.get_by_id(dto.user_id)
        if not user:
            raise UserNotFoundException(str(dto.user_id))

        return await self._repo.update_profile(
            dto.user_id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            avatar_url=dto.avatar_url,
        )


class UploadAvatarUseCase:
    """
    Upload d'avatar vers Supabase Storage.
    L'URL publique est ensuite stockée sur le profil utilisateur.
    """

    def __init__(self, repo: IUsersRepository, storage_service: "IStorageService") -> None:
        self._repo = repo
        self._storage = storage_service

    async def execute(self, dto: UpdateAvatarDTO) -> UserEntity:
        user = await self._repo.get_by_id(dto.user_id)
        if not user:
            raise UserNotFoundException(str(dto.user_id))

        avatar_url = await self._storage.upload(
            bucket="avatars",
            path=f"users/{dto.user_id}/{dto.filename}",
            content=dto.file_content,
            content_type=dto.content_type,
        )
        return await self._repo.update_profile(dto.user_id, avatar_url=avatar_url)


class AdminUpdateUserUseCase:
    def __init__(self, repo: IUsersRepository) -> None:
        self._repo = repo

    async def execute(self, dto: AdminUpdateUserDTO) -> UserEntity:
        user = await self._repo.get_by_id(dto.user_id)
        if not user:
            raise UserNotFoundException(str(dto.user_id))

        update_kwargs: dict = {}
        if dto.first_name is not None:
            update_kwargs["first_name"] = dto.first_name
        if dto.last_name is not None:
            update_kwargs["last_name"] = dto.last_name

        if update_kwargs:
            user = await self._repo.update_profile(dto.user_id, **update_kwargs)

        if dto.is_active is not None:
            user = await self._repo.set_active(dto.user_id, dto.is_active)

        return user


class DeleteUserUseCase:
    def __init__(self, repo: IUsersRepository) -> None:
        self._repo = repo

    async def execute(self, user_id: uuid.UUID) -> None:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        await self._repo.delete(user_id)


class IStorageService(ABC):
    """Port vers le service de stockage (Supabase Storage, S3, etc.)."""

    @abstractmethod
    async def upload(
        self,
        bucket: str,
        path: str,
        content: bytes,
        content_type: str,
    ) -> str:
        """Retourne l'URL publique du fichier uploadé."""
        ...
