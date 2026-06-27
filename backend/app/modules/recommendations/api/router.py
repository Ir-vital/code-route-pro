"""Router FastAPI du module recommendations — /api/v1/dashboard/recommendations"""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.api.dependencies import CurrentUser
from app.modules.recommendations.infrastructure.models import RecommendationModel

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


class RecommendationResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    reason: str | None = None
    priority: int
    generated_at: datetime


@router.get("/", response_model=list[RecommendationResponse], summary="Mes recommandations")
async def get_my_recommendations(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[RecommendationResponse]:
    result = await db.execute(
        select(RecommendationModel)
        .where(
            RecommendationModel.user_id == current_user.id,
            RecommendationModel.is_dismissed == False,  # noqa: E712
        )
        .order_by(RecommendationModel.priority.desc())
        .limit(10)
    )
    return [
        RecommendationResponse(
            id=r.id, category_id=r.category_id,
            reason=r.reason, priority=r.priority, generated_at=r.generated_at,
        )
        for r in result.scalars().all()
    ]


@router.post("/{recommendation_id}/dismiss", response_model=dict)
async def dismiss_recommendation(
    recommendation_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    await db.execute(
        update(RecommendationModel)
        .where(
            RecommendationModel.id == recommendation_id,
            RecommendationModel.user_id == current_user.id,
        )
        .values(is_dismissed=True)
    )
    return {"message": "Recommandation ignorée"}
