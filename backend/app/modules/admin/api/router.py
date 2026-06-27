"""Router FastAPI du module admin — /api/v1/admin"""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.admin.infrastructure.models import AuditLogModel
from app.modules.auth.api.dependencies import CurrentAdmin
from app.modules.auth.infrastructure.models import UserModel
from app.modules.exams.infrastructure.models import ExamAttemptModel
from app.shared.domain.enums import AttemptStatus, UserRole
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/admin", tags=["Admin"])


# ─── Schémas réponse ──────────────────────────────────────────────────────────

class StatsOverviewResponse(BaseModel):
    total_users: int
    active_users: int
    total_exams_taken: int
    average_success_rate: float | None


class UserStatsResponse(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    admin_count: int
    student_count: int


class ExamStatsResponse(BaseModel):
    total_attempts: int
    completed_attempts: int
    pass_count: int
    fail_count: int
    average_score: float | None
    pass_rate: float | None


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    actor_id: uuid.UUID | None
    action: str
    entity_type: str
    entity_id: uuid.UUID | None
    metadata: dict | None
    created_at: datetime


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/stats/overview", response_model=StatsOverviewResponse)
async def stats_overview(
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StatsOverviewResponse:
    total_users = (await db.execute(select(func.count(UserModel.id)))).scalar_one()
    active_users = (await db.execute(
        select(func.count(UserModel.id)).where(UserModel.is_active == True)  # noqa: E712
    )).scalar_one()

    attempts_row = (await db.execute(
        select(
            func.count(ExamAttemptModel.id).label("total"),
            func.count(ExamAttemptModel.id).filter(
                ExamAttemptModel.status == AttemptStatus.COMPLETED
            ).label("completed"),
            func.avg(ExamAttemptModel.score_percentage).filter(
                ExamAttemptModel.status == AttemptStatus.COMPLETED
            ).label("avg"),
        )
    )).one()

    avg_success = None
    if attempts_row.avg:
        avg_success = float(attempts_row.avg)

    return StatsOverviewResponse(
        total_users=total_users,
        active_users=active_users,
        total_exams_taken=attempts_row.completed or 0,
        average_success_rate=avg_success,
    )


@router.get("/stats/users", response_model=UserStatsResponse)
async def stats_users(
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserStatsResponse:
    total = (await db.execute(select(func.count(UserModel.id)))).scalar_one()
    active = (await db.execute(
        select(func.count(UserModel.id)).where(UserModel.is_active == True)  # noqa: E712
    )).scalar_one()
    verified = (await db.execute(
        select(func.count(UserModel.id)).where(UserModel.is_verified == True)  # noqa: E712
    )).scalar_one()
    admins = (await db.execute(
        select(func.count(UserModel.id)).where(UserModel.role == UserRole.ADMIN)
    )).scalar_one()
    students = (await db.execute(
        select(func.count(UserModel.id)).where(UserModel.role == UserRole.STUDENT)
    )).scalar_one()

    return UserStatsResponse(
        total_users=total, active_users=active, verified_users=verified,
        admin_count=admins, student_count=students,
    )


@router.get("/stats/exams", response_model=ExamStatsResponse)
async def stats_exams(
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExamStatsResponse:
    row = (await db.execute(
        select(
            func.count(ExamAttemptModel.id).label("total"),
            func.count(ExamAttemptModel.id).filter(
                ExamAttemptModel.status == AttemptStatus.COMPLETED
            ).label("completed"),
            func.count(ExamAttemptModel.id).filter(
                ExamAttemptModel.is_passed == True  # noqa: E712
            ).label("passed"),
            func.count(ExamAttemptModel.id).filter(
                ExamAttemptModel.is_passed == False  # noqa: E712
            ).label("failed"),
            func.avg(ExamAttemptModel.score_percentage).filter(
                ExamAttemptModel.status == AttemptStatus.COMPLETED
            ).label("avg"),
        )
    )).one()

    completed = row.completed or 0
    passed = row.passed or 0
    pass_rate = (passed / completed * 100) if completed > 0 else None

    return ExamStatsResponse(
        total_attempts=row.total or 0,
        completed_attempts=completed,
        pass_count=passed,
        fail_count=row.failed or 0,
        average_score=float(row.avg) if row.avg else None,
        pass_rate=pass_rate,
    )


@router.get("/audit-logs", response_model=PaginatedResponse[AuditLogResponse])
async def audit_logs(
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    action: str | None = Query(default=None),
) -> PaginatedResponse[AuditLogResponse]:
    params = PaginationParams(page=page, page_size=page_size)
    q = select(AuditLogModel)
    cq = select(func.count()).select_from(AuditLogModel)
    if action:
        q = q.where(AuditLogModel.action == action)
        cq = cq.where(AuditLogModel.action == action)

    total = (await db.execute(cq)).scalar_one()
    logs = (await db.execute(
        q.order_by(AuditLogModel.created_at.desc())
        .offset(params.offset).limit(params.limit)
    )).scalars().all()

    items = [
        AuditLogResponse(
            id=l.id, actor_id=l.actor_id, action=l.action,
            entity_type=l.entity_type, entity_id=l.entity_id,
            metadata=l.metadata, created_at=l.created_at,
        )
        for l in logs
    ]
    return PaginatedResponse.create(items=items, total=total, params=params)
