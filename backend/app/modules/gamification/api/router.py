"""Router FastAPI du module gamification — /api/v1/badges"""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.api.dependencies import CurrentUser
from app.modules.gamification.infrastructure.models import BadgeModel, UserBadgeModel
from app.shared.domain.enums import BadgeCriteriaType

router = APIRouter(prefix="/badges", tags=["Gamification — Badges"])


class BadgeResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    icon: str | None = None
    criteria_type: BadgeCriteriaType
    criteria_value: int


class UserBadgeResponse(BaseModel):
    badge: BadgeResponse
    earned_at: datetime


@router.get("/", response_model=list[BadgeResponse], summary="Catalogue des badges")
async def list_badges(
    _user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[BadgeResponse]:
    result = await db.execute(select(BadgeModel).order_by(BadgeModel.name))
    return [
        BadgeResponse(
            id=b.id, name=b.name, description=b.description,
            icon=b.icon, criteria_type=b.criteria_type, criteria_value=b.criteria_value,
        )
        for b in result.scalars().all()
    ]


@router.get("/me", response_model=list[UserBadgeResponse], summary="Mes badges obtenus")
async def my_badges(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[UserBadgeResponse]:
    result = await db.execute(
        select(UserBadgeModel, BadgeModel)
        .join(BadgeModel, UserBadgeModel.badge_id == BadgeModel.id)
        .where(UserBadgeModel.user_id == current_user.id)
        .order_by(UserBadgeModel.earned_at.desc())
    )
    return [
        UserBadgeResponse(
            badge=BadgeResponse(
                id=badge.id, name=badge.name, description=badge.description,
                icon=badge.icon, criteria_type=badge.criteria_type,
                criteria_value=badge.criteria_value,
            ),
            earned_at=ub.earned_at,
        )
        for ub, badge in result.all()
    ]
