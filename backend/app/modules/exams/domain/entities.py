"""Entités métier du module exams."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.shared.domain.enums import AttemptStatus, Difficulty, ExamType, QuestionType


@dataclass
class QuestionOptionEntity:
    question_id: uuid.UUID
    content: str
    is_correct: bool = False
    display_order: int = 0
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class QuestionEntity:
    category_id: uuid.UUID
    content: str
    question_type: QuestionType = QuestionType.SINGLE_CHOICE
    difficulty: Difficulty = Difficulty.EASY
    sign_id: uuid.UUID | None = None
    image_url: str | None = None
    explanation: str | None = None
    is_active: bool = True
    options: list[QuestionOptionEntity] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def correct_option_ids(self) -> list[uuid.UUID]:
        return [opt.id for opt in self.options if opt.is_correct]


@dataclass
class ExamEntity:
    title: str
    exam_type: ExamType
    question_count: int
    time_limit_seconds: int
    description: str | None = None
    category_id: uuid.UUID | None = None
    passing_score_percentage: float = 80.0
    difficulty: Difficulty = Difficulty.MIXED
    is_active: bool = True
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class AttemptQuestionEntity:
    """Snapshot d'une question tirée pour une tentative."""
    attempt_id: uuid.UUID
    question_id: uuid.UUID
    display_order: int
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class AttemptAnswerOptionEntity:
    attempt_answer_id: uuid.UUID
    question_option_id: uuid.UUID


@dataclass
class AttemptAnswerEntity:
    attempt_id: uuid.UUID
    question_id: uuid.UUID
    is_correct: bool | None = None
    answered_at: datetime | None = None
    selected_option_ids: list[uuid.UUID] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class ExamAttemptEntity:
    user_id: uuid.UUID
    exam_id: uuid.UUID
    status: AttemptStatus = AttemptStatus.IN_PROGRESS
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_seconds: int | None = None
    score_percentage: float | None = None
    is_passed: bool | None = None
    questions: list[AttemptQuestionEntity] = field(default_factory=list)
    answers: list[AttemptAnswerEntity] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None

    @property
    def is_complete(self) -> bool:
        return self.status == AttemptStatus.COMPLETED

    @property
    def answered_count(self) -> int:
        return len([a for a in self.answers if a.answered_at is not None])

    @property
    def total_questions(self) -> int:
        return len(self.questions)
