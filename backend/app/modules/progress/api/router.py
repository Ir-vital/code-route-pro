"""Router FastAPI du module progress — /api/v1/dashboard"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.api.dependencies import CurrentUser
from app.modules.exams.infrastructure.models import ExamAttemptModel
from app.modules.progress.infrastructure.models import CategoryMasteryModel, UserProgressModel
from app.shared.domain.enums import AttemptStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard / Progress"])


class DashboardSummaryResponse(BaseModel):
    total_attempts: int
    completed_attempts: int
    average_score: float | None
    best_score: float | None
    last_score: float | None
    current_streak_days: int
    xp_points: int
    level: int


class ProgressChartPoint(BaseModel):
    date: str
    score: float


class CategoryMasteryResponse(BaseModel):
    category_id: uuid.UUID
    mastery_percentage: float


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DashboardSummaryResponse:
    # Stats tentatives
    attempts_q = await db.execute(
        select(
            func.count(ExamAttemptModel.id).label("total"),
            func.count(ExamAttemptModel.id).filter(
                ExamAttemptModel.status == AttemptStatus.COMPLETED
            ).label("completed"),
            func.avg(ExamAttemptModel.score_percentage).filter(
                ExamAttemptModel.status == AttemptStatus.COMPLETED
            ).label("avg_score"),
            func.max(ExamAttemptModel.score_percentage).label("best_score"),
        ).where(ExamAttemptModel.user_id == current_user.id)
    )
    row = attempts_q.one()

    # Dernière note
    last_q = await db.execute(
        select(ExamAttemptModel.score_percentage)
        .where(
            ExamAttemptModel.user_id == current_user.id,
            ExamAttemptModel.status == AttemptStatus.COMPLETED,
        )
        .order_by(ExamAttemptModel.finished_at.desc())
        .limit(1)
    )
    last_score = last_q.scalar_one_or_none()

    # Progression utilisateur
    progress_q = await db.execute(
        select(UserProgressModel).where(UserProgressModel.user_id == current_user.id)
    )
    progress = progress_q.scalar_one_or_none()

    return DashboardSummaryResponse(
        total_attempts=row.total or 0,
        completed_attempts=row.completed or 0,
        average_score=float(row.avg_score) if row.avg_score else None,
        best_score=float(row.best_score) if row.best_score else None,
        last_score=float(last_score) if last_score else None,
        current_streak_days=progress.current_streak_days if progress else 0,
        xp_points=progress.xp_points if progress else 0,
        level=progress.level if progress else 1,
    )


@router.get("/progress-chart", response_model=list[ProgressChartPoint])
async def get_progress_chart(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProgressChartPoint]:
    result = await db.execute(
        select(
            func.date(ExamAttemptModel.finished_at).label("date"),
            func.avg(ExamAttemptModel.score_percentage).label("score"),
        )
        .where(
            ExamAttemptModel.user_id == current_user.id,
            ExamAttemptModel.status == AttemptStatus.COMPLETED,
            ExamAttemptModel.finished_at.isnot(None),
        )
        .group_by(func.date(ExamAttemptModel.finished_at))
        .order_by(func.date(ExamAttemptModel.finished_at))
        .limit(90)
    )
    return [
        ProgressChartPoint(date=str(row.date), score=float(row.score))
        for row in result.all()
    ]


@router.get("/category-mastery", response_model=list[CategoryMasteryResponse])
async def get_category_mastery(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CategoryMasteryResponse]:
    result = await db.execute(
        select(CategoryMasteryModel).where(CategoryMasteryModel.user_id == current_user.id)
    )
    return [
        CategoryMasteryResponse(
            category_id=m.category_id,
            mastery_percentage=float(m.mastery_percentage),
        )
        for m in result.scalars().all()
    ]
