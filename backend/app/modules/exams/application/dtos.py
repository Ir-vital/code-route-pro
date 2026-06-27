"""DTOs internes du module exams."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.shared.domain.enums import AttemptStatus, Difficulty, ExamType, QuestionType


@dataclass
class CreateQuestionOptionDTO:
    content: str
    is_correct: bool = False
    display_order: int = 0


@dataclass
class CreateQuestionDTO:
    category_id: uuid.UUID
    content: str
    options: list[CreateQuestionOptionDTO] = field(default_factory=list)
    question_type: QuestionType = QuestionType.SINGLE_CHOICE
    difficulty: Difficulty = Difficulty.EASY
    sign_id: uuid.UUID | None = None
    image_url: str | None = None
    explanation: str | None = None


@dataclass
class UpdateQuestionDTO:
    question_id: uuid.UUID
    content: str | None = None
    explanation: str | None = None
    difficulty: Difficulty | None = None
    is_active: bool | None = None


@dataclass
class CreateExamDTO:
    title: str
    exam_type: ExamType
    question_count: int
    time_limit_seconds: int
    description: str | None = None
    category_id: uuid.UUID | None = None
    passing_score_percentage: float = 80.0
    difficulty: Difficulty = Difficulty.MIXED


@dataclass
class UpdateExamDTO:
    exam_id: uuid.UUID
    title: str | None = None
    description: str | None = None
    question_count: int | None = None
    time_limit_seconds: int | None = None
    passing_score_percentage: float | None = None
    is_active: bool | None = None


@dataclass
class StartAttemptDTO:
    user_id: uuid.UUID
    exam_id: uuid.UUID


@dataclass
class SubmitAnswerDTO:
    attempt_id: uuid.UUID
    question_id: uuid.UUID
    selected_option_ids: list[uuid.UUID]
    user_id: uuid.UUID


@dataclass
class SubmitAttemptDTO:
    attempt_id: uuid.UUID
    user_id: uuid.UUID


@dataclass
class AttemptResultDTO:
    attempt_id: uuid.UUID
    exam_title: str
    score_percentage: float
    is_passed: bool
    duration_seconds: int | None
    total_questions: int
    correct_answers: int
    finished_at: datetime | None
    answers: list["AnswerResultDTO"] = field(default_factory=list)


@dataclass
class AnswerResultDTO:
    question_id: uuid.UUID
    question_content: str
    is_correct: bool
    selected_option_ids: list[uuid.UUID]
    correct_option_ids: list[uuid.UUID]
    explanation: str | None = None
