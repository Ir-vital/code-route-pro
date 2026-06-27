"""Implémentation SQLAlchemy du repository users."""

import uuid

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.domain.entities import UserEntity
from app.modules.auth.infrastructure.models import UserModel
from app.modules.auth.infrastructure.repositories import _user_to_entity
from app.modules.users.domain.repositories import IUsersRepository
from app.shared.domain.enums import UserRole


class UsersRepository(IUsersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        m = result.scalar_one_or_none()
        return _user_to_entity(m) if m else None

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        role: UserRole | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[UserEntity], int]:
        query = select(UserModel)
        count_query = select(func.count()).select_from(UserModel)

        if role is not None:
            query = query.where(UserModel.role == role)
            count_query = count_query.where(UserModel.role == role)
        if is_active is not None:
            query = query.where(UserModel.is_active == is_active)
            count_query = count_query.where(UserModel.is_active == is_active)
        if search:
            pattern = f"%{search}%"
            condition = or_(
                UserModel.email.ilike(pattern),
                UserModel.first_name.ilike(pattern),
                UserModel.last_name.ilike(pattern),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(offset).limit(limit).order_by(UserModel.created_at.desc())
        result = await self._session.execute(query)
        models = result.scalars().all()

        return [_user_to_entity(m) for m in models], total

    async def update_profile(
        self,
        user_id: uuid.UUID,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        avatar_url: str | None = None,
    ) -> UserEntity:
        values: dict = {}
        if first_name is not None:
            values["first_name"] = first_name
        if last_name is not None:
            values["last_name"] = last_name
        if avatar_url is not None:
            values["avatar_url"] = avatar_url

        if values:
            await self._session.execute(
                update(UserModel).where(UserModel.id == user_id).values(**values)
            )
            await self._session.flush()

        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        m = result.scalar_one()
        return _user_to_entity(m)

    async def set_active(self, user_id: uuid.UUID, is_active: bool) -> UserEntity:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=is_active)
        )
        await self._session.flush()
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        m = result.scalar_one()
        return _user_to_entity(m)

    async def delete(self, user_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        m = result.scalar_one_or_none()
        if m:
            await self._session.delete(m)
            await self._session.flush()
