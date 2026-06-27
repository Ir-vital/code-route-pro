"""Modèles SQLAlchemy du module exams."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Integer, Numeric,
    PrimaryKeyConstraint, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.domain.enums import (
    AttemptStatus, Difficulty, ExamType, QuestionType,
)
from app.shared.mixins import TimestampMixin, UUIDMixin


class QuestionModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "questions"

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    sign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("signs.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, name="question_type_enum"), nullable=False, default=QuestionType.SINGLE_CHOICE
    )
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, name="question_difficulty_enum"), nullable=False, default=Difficulty.EASY
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    options: Mapped[list["QuestionOptionModel"]] = relationship(
        back_populates="question", cascade="all, delete-orphan", order_by="QuestionOptionModel.display_order"
    )


class QuestionOptionModel(Base, UUIDMixin):
    __tablename__ = "question_options"

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    question: Mapped["QuestionModel"] = relationship(back_populates="options")


class ExamModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exams"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    exam_type: Mapped[ExamType] = mapped_column(
        Enum(ExamType, name="exam_type_enum"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    question_count: Mapped[int] = mapped_column(Integer, nullable=False)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    passing_score_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=80.0, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, name="exam_difficulty_enum"), nullable=False, default=Difficulty.MIXED
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ExamAttemptModel(Base, UUIDMixin):
    __tablename__ = "exam_attempts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exams.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[AttemptStatus] = mapped_column(
        Enum(AttemptStatus, name="attempt_status_enum"), nullable=False, default=AttemptStatus.IN_PROGRESS
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow()
    )

    questions: Mapped[list["AttemptQuestionModel"]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan",
        order_by="AttemptQuestionModel.display_order"
    )
    answers: Mapped[list["AttemptAnswerModel"]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan"
    )


class AttemptQuestionModel(Base, UUIDMixin):
    __tablename__ = "attempt_questions"

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exam_attempts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)

    attempt: Mapped["ExamAttemptModel"] = relationship(back_populates="questions")


class AttemptAnswerModel(Base, UUIDMixin):
    __tablename__ = "attempt_answers"

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exam_attempts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False
    )
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    attempt: Mapped["ExamAttemptModel"] = relationship(back_populates="answers")
    selected_options: Mapped[list["AttemptAnswerOptionModel"]] = relationship(
        back_populates="answer", cascade="all, delete-orphan"
    )


class AttemptAnswerOptionModel(Base):
    __tablename__ = "attempt_answer_options"
    __table_args__ = (
        PrimaryKeyConstraint("attempt_answer_id", "question_option_id"),
    )

    attempt_answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("attempt_answers.id", ondelete="CASCADE"), nullable=False
    )
    question_option_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("question_options.id", ondelete="RESTRICT"), nullable=False
    )

    answer: Mapped["AttemptAnswerModel"] = relationship(back_populates="selected_options")
