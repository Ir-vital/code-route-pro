"""Implémentations SQLAlchemy des repositories du module exams."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.exams.domain.entities import (
    AttemptAnswerEntity,
    AttemptQuestionEntity,
    ExamAttemptEntity,
    ExamEntity,
    QuestionEntity,
    QuestionOptionEntity,
)
from app.modules.exams.domain.repositories import (
    IExamAttemptRepository,
    IExamRepository,
    IQuestionRepository,
)
from app.modules.exams.infrastructure.models import (
    AttemptAnswerModel,
    AttemptAnswerOptionModel,
    AttemptQuestionModel,
    ExamAttemptModel,
    ExamModel,
    QuestionModel,
    QuestionOptionModel,
)
from app.shared.domain.enums import AttemptStatus, Difficulty, ExamType, QuestionType


# ─── Mappers ──────────────────────────────────────────────────────────────────

def _opt_to_entity(m: QuestionOptionModel) -> QuestionOptionEntity:
    return QuestionOptionEntity(
        id=m.id, question_id=m.question_id, content=m.content,
        is_correct=m.is_correct, display_order=m.display_order,
    )


def _question_to_entity(m: QuestionModel) -> QuestionEntity:
    return QuestionEntity(
        id=m.id, category_id=m.category_id, sign_id=m.sign_id,
        content=m.content, image_url=m.image_url, explanation=m.explanation,
        question_type=QuestionType(m.question_type),
        difficulty=Difficulty(m.difficulty),
        is_active=m.is_active,
        options=[_opt_to_entity(o) for o in (m.options or [])],
        created_at=m.created_at, updated_at=m.updated_at,
    )


def _exam_to_entity(m: ExamModel) -> ExamEntity:
    return ExamEntity(
        id=m.id, title=m.title, description=m.description,
        exam_type=ExamType(m.exam_type), category_id=m.category_id,
        question_count=m.question_count, time_limit_seconds=m.time_limit_seconds,
        passing_score_percentage=float(m.passing_score_percentage),
        difficulty=Difficulty(m.difficulty), is_active=m.is_active,
        created_at=m.created_at, updated_at=m.updated_at,
    )


def _attempt_q_to_entity(m: AttemptQuestionModel) -> AttemptQuestionEntity:
    return AttemptQuestionEntity(
        id=m.id, attempt_id=m.attempt_id,
        question_id=m.question_id, display_order=m.display_order,
    )


def _attempt_answer_to_entity(m: AttemptAnswerModel) -> AttemptAnswerEntity:
    return AttemptAnswerEntity(
        id=m.id, attempt_id=m.attempt_id, question_id=m.question_id,
        is_correct=m.is_correct, answered_at=m.answered_at,
        selected_option_ids=[o.question_option_id for o in (m.selected_options or [])],
    )


def _attempt_to_entity(m: ExamAttemptModel) -> ExamAttemptEntity:
    return ExamAttemptEntity(
        id=m.id, user_id=m.user_id, exam_id=m.exam_id,
        status=AttemptStatus(m.status),
        started_at=m.started_at, finished_at=m.finished_at,
        duration_seconds=m.duration_seconds,
        score_percentage=float(m.score_percentage) if m.score_percentage is not None else None,
        is_passed=m.is_passed,
        questions=[_attempt_q_to_entity(q) for q in (m.questions or [])],
        answers=[_attempt_answer_to_entity(a) for a in (m.answers or [])],
        created_at=m.created_at,
    )


# ─── QuestionRepository ───────────────────────────────────────────────────────

class QuestionRepository(IQuestionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, question_id: uuid.UUID) -> QuestionEntity | None:
        result = await self._session.execute(
            select(QuestionModel)
            .options(selectinload(QuestionModel.options))
            .where(QuestionModel.id == question_id)
        )
        m = result.scalar_one_or_none()
        return _question_to_entity(m) if m else None

    async def get_all(
        self, *, offset=0, limit=20,
        category_id=None, difficulty=None, is_active=None,
    ) -> tuple[list[QuestionEntity], int]:
        q = select(QuestionModel).options(selectinload(QuestionModel.options))
        cq = select(func.count()).select_from(QuestionModel)
        if category_id:
            q = q.where(QuestionModel.category_id == category_id)
            cq = cq.where(QuestionModel.category_id == category_id)
        if difficulty:
            q = q.where(QuestionModel.difficulty == difficulty)
            cq = cq.where(QuestionModel.difficulty == difficulty)
        if is_active is not None:
            q = q.where(QuestionModel.is_active == is_active)
            cq = cq.where(QuestionModel.is_active == is_active)
        total = (await self._session.execute(cq)).scalar_one()
        q = q.offset(offset).limit(limit)
        models = (await self._session.execute(q)).scalars().all()
        return [_question_to_entity(m) for m in models], total

    async def get_random_for_exam(
        self, count: int, *, category_id=None, difficulty=None
    ) -> list[QuestionEntity]:
        q = (
            select(QuestionModel)
            .options(selectinload(QuestionModel.options))
            .where(QuestionModel.is_active == True)  # noqa: E712
            .order_by(func.random())
            .limit(count)
        )
        if category_id:
            q = q.where(QuestionModel.category_id == category_id)
        if difficulty:
            q = q.where(QuestionModel.difficulty == difficulty)
        models = (await self._session.execute(q)).scalars().all()
        return [_question_to_entity(m) for m in models]

    async def create(self, entity: QuestionEntity) -> QuestionEntity:
        m = QuestionModel()
        m.id = entity.id
        m.category_id = entity.category_id
        m.sign_id = entity.sign_id
        m.content = entity.content
        m.image_url = entity.image_url
        m.explanation = entity.explanation
        m.question_type = entity.question_type
        m.difficulty = entity.difficulty
        m.is_active = entity.is_active
        self._session.add(m)
        await self._session.flush()
        for opt in entity.options:
            om = QuestionOptionModel()
            om.id = opt.id
            om.question_id = m.id
            om.content = opt.content
            om.is_correct = opt.is_correct
            om.display_order = opt.display_order
            self._session.add(om)
        await self._session.flush()
        await self._session.refresh(m)
        return _question_to_entity(m)

    async def update(self, entity: QuestionEntity) -> QuestionEntity:
        result = await self._session.execute(
            select(QuestionModel).options(selectinload(QuestionModel.options))
            .where(QuestionModel.id == entity.id)
        )
        m = result.scalar_one()
        m.content = entity.content
        m.explanation = entity.explanation
        m.difficulty = entity.difficulty
        m.is_active = entity.is_active
        await self._session.flush()
        await self._session.refresh(m)
        return _question_to_entity(m)

    async def delete(self, question_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(QuestionModel).where(QuestionModel.id == question_id)
        )
        m = result.scalar_one_or_none()
        if m:
            await self._session.delete(m)
            await self._session.flush()


# ─── ExamRepository ───────────────────────────────────────────────────────────

class ExamRepository(IExamRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, exam_id: uuid.UUID) -> ExamEntity | None:
        result = await self._session.execute(select(ExamModel).where(ExamModel.id == exam_id))
        m = result.scalar_one_or_none()
        return _exam_to_entity(m) if m else None

    async def get_all(self, *, offset=0, limit=20, is_active=True) -> tuple[list[ExamEntity], int]:
        q = select(ExamModel)
        cq = select(func.count()).select_from(ExamModel)
        if is_active is not None:
            q = q.where(ExamModel.is_active == is_active)
            cq = cq.where(ExamModel.is_active == is_active)
        total = (await self._session.execute(cq)).scalar_one()
        q = q.offset(offset).limit(limit).order_by(ExamModel.created_at.desc())
        models = (await self._session.execute(q)).scalars().all()
        return [_exam_to_entity(m) for m in models], total

    async def create(self, entity: ExamEntity) -> ExamEntity:
        m = ExamModel()
        m.id = entity.id
        m.title = entity.title
        m.description = entity.description
        m.exam_type = entity.exam_type
        m.category_id = entity.category_id
        m.question_count = entity.question_count
        m.time_limit_seconds = entity.time_limit_seconds
        m.passing_score_percentage = entity.passing_score_percentage
        m.difficulty = entity.difficulty
        m.is_active = entity.is_active
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _exam_to_entity(m)

    async def update(self, entity: ExamEntity) -> ExamEntity:
        result = await self._session.execute(select(ExamModel).where(ExamModel.id == entity.id))
        m = result.scalar_one()
        m.title = entity.title
        m.description = entity.description
        m.question_count = entity.question_count
        m.time_limit_seconds = entity.time_limit_seconds
        m.passing_score_percentage = entity.passing_score_percentage
        m.is_active = entity.is_active
        await self._session.flush()
        await self._session.refresh(m)
        return _exam_to_entity(m)

    async def delete(self, exam_id: uuid.UUID) -> None:
        result = await self._session.execute(select(ExamModel).where(ExamModel.id == exam_id))
        m = result.scalar_one_or_none()
        if m:
            await self._session.delete(m)
            await self._session.flush()


# ─── ExamAttemptRepository ────────────────────────────────────────────────────

class ExamAttemptRepository(IExamAttemptRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, attempt_id: uuid.UUID) -> ExamAttemptEntity | None:
        result = await self._session.execute(
            select(ExamAttemptModel)
            .options(
                selectinload(ExamAttemptModel.questions),
                selectinload(ExamAttemptModel.answers).selectinload(AttemptAnswerModel.selected_options),
            )
            .where(ExamAttemptModel.id == attempt_id)
        )
        m = result.scalar_one_or_none()
        return _attempt_to_entity(m) if m else None

    async def get_by_user(
        self, user_id: uuid.UUID, *, offset=0, limit=20
    ) -> tuple[list[ExamAttemptEntity], int]:
        cq = select(func.count()).select_from(ExamAttemptModel).where(ExamAttemptModel.user_id == user_id)
        total = (await self._session.execute(cq)).scalar_one()
        q = (
            select(ExamAttemptModel)
            .options(selectinload(ExamAttemptModel.questions))
            .where(ExamAttemptModel.user_id == user_id)
            .order_by(ExamAttemptModel.started_at.desc())
            .offset(offset).limit(limit)
        )
        models = (await self._session.execute(q)).scalars().all()
        return [_attempt_to_entity(m) for m in models], total

    async def get_in_progress(self, user_id: uuid.UUID, exam_id: uuid.UUID) -> ExamAttemptEntity | None:
        result = await self._session.execute(
            select(ExamAttemptModel).where(
                ExamAttemptModel.user_id == user_id,
                ExamAttemptModel.exam_id == exam_id,
                ExamAttemptModel.status == AttemptStatus.IN_PROGRESS,
            )
        )
        m = result.scalar_one_or_none()
        return _attempt_to_entity(m) if m else None

    async def create(self, entity: ExamAttemptEntity) -> ExamAttemptEntity:
        m = ExamAttemptModel()
        m.id = entity.id
        m.user_id = entity.user_id
        m.exam_id = entity.exam_id
        m.status = entity.status
        m.started_at = entity.started_at or datetime.now(UTC)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _attempt_to_entity(m)

    async def update(self, entity: ExamAttemptEntity) -> ExamAttemptEntity:
        result = await self._session.execute(
            select(ExamAttemptModel)
            .options(
                selectinload(ExamAttemptModel.questions),
                selectinload(ExamAttemptModel.answers).selectinload(AttemptAnswerModel.selected_options),
            )
            .where(ExamAttemptModel.id == entity.id)
        )
        m = result.scalar_one()
        m.status = entity.status
        m.finished_at = entity.finished_at
        m.duration_seconds = entity.duration_seconds
        m.score_percentage = entity.score_percentage
        m.is_passed = entity.is_passed

        # Sync questions snapshot
        existing_q_ids = {q.question_id for q in m.questions}
        for aq in entity.questions:
            if aq.question_id not in existing_q_ids:
                qm = AttemptQuestionModel()
                qm.id = aq.id
                qm.attempt_id = entity.id
                qm.question_id = aq.question_id
                qm.display_order = aq.display_order
                self._session.add(qm)

        await self._session.flush()
        await self._session.refresh(m)
        return _attempt_to_entity(m)

    async def save_answer(self, answer: AttemptAnswerEntity) -> AttemptAnswerEntity:
        # Upsert de la réponse
        result = await self._session.execute(
            select(AttemptAnswerModel).where(
                AttemptAnswerModel.attempt_id == answer.attempt_id,
                AttemptAnswerModel.question_id == answer.question_id,
            )
        )
        m = result.scalar_one_or_none()
        if not m:
            m = AttemptAnswerModel()
            m.id = answer.id
            m.attempt_id = answer.attempt_id
            m.question_id = answer.question_id
            self._session.add(m)

        m.is_correct = answer.is_correct
        m.answered_at = answer.answered_at
        await self._session.flush()

        # Remplacer les options sélectionnées
        existing = await self._session.execute(
            select(AttemptAnswerOptionModel).where(
                AttemptAnswerOptionModel.attempt_answer_id == m.id
            )
        )
        for old in existing.scalars().all():
            await self._session.delete(old)

        for opt_id in answer.selected_option_ids:
            opt_model = AttemptAnswerOptionModel()
            opt_model.attempt_answer_id = m.id
            opt_model.question_option_id = opt_id
            self._session.add(opt_model)

        await self._session.flush()
        await self._session.refresh(m)
        return _attempt_answer_to_entity(m)

    async def get_answer(
        self, attempt_id: uuid.UUID, question_id: uuid.UUID
    ) -> AttemptAnswerEntity | None:
        result = await self._session.execute(
            select(AttemptAnswerModel)
            .options(selectinload(AttemptAnswerModel.selected_options))
            .where(
                AttemptAnswerModel.attempt_id == attempt_id,
                AttemptAnswerModel.question_id == question_id,
            )
        )
        m = result.scalar_one_or_none()
        return _attempt_answer_to_entity(m) if m else None
