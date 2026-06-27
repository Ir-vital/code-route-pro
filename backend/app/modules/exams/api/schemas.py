"""Schémas Pydantic du module exams."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.shared.domain.enums import AttemptStatus, Difficulty, ExamType, QuestionType


# ─── Questions ────────────────────────────────────────────────────────────────

class QuestionOptionResponse(BaseModel):
    id: uuid.UUID
    content: str
    display_order: int
    # is_correct n'est PAS exposé aux élèves — uniquement dans la correction

    model_config = {"from_attributes": True}


class QuestionOptionWithCorrectResponse(QuestionOptionResponse):
    """Version admin avec is_correct visible."""
    is_correct: bool


class QuestionResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    sign_id: uuid.UUID | None = None
    content: str
    image_url: str | None = None
    explanation: str | None = None
    question_type: QuestionType
    difficulty: Difficulty
    is_active: bool
    options: list[QuestionOptionWithCorrectResponse] = []

    model_config = {"from_attributes": True}


class CreateQuestionOptionRequest(BaseModel):
    content: str = Field(min_length=1, max_length=500)
    is_correct: bool = False
    display_order: int = 0


class CreateQuestionRequest(BaseModel):
    category_id: uuid.UUID
    content: str = Field(min_length=1)
    options: list[CreateQuestionOptionRequest] = Field(min_length=2)
    question_type: QuestionType = QuestionType.SINGLE_CHOICE
    difficulty: Difficulty = Difficulty.EASY
    sign_id: uuid.UUID | None = None
    image_url: str | None = None
    explanation: str | None = None


class UpdateQuestionRequest(BaseModel):
    content: str | None = None
    explanation: str | None = None
    difficulty: Difficulty | None = None
    is_active: bool | None = None


# ─── Examens ──────────────────────────────────────────────────────────────────

class ExamResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    exam_type: ExamType
    category_id: uuid.UUID | None = None
    question_count: int
    time_limit_seconds: int
    passing_score_percentage: float
    difficulty: Difficulty
    is_active: bool

    model_config = {"from_attributes": True}


class CreateExamRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    exam_type: ExamType
    question_count: int = Field(ge=1, le=100)
    time_limit_seconds: int = Field(ge=60)
    description: str | None = None
    category_id: uuid.UUID | None = None
    passing_score_percentage: float = Field(default=80.0, ge=0, le=100)
    difficulty: Difficulty = Difficulty.MIXED


class UpdateExamRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    question_count: int | None = Field(default=None, ge=1, le=100)
    time_limit_seconds: int | None = Field(default=None, ge=60)
    passing_score_percentage: float | None = Field(default=None, ge=0, le=100)
    is_active: bool | None = None


# ─── Tentatives ───────────────────────────────────────────────────────────────

class AttemptQuestionResponse(BaseModel):
    """Question dans le contexte d'une tentative (sans is_correct sur les options)."""
    id: uuid.UUID
    content: str
    image_url: str | None = None
    question_type: QuestionType
    options: list[QuestionOptionResponse] = []


class AttemptResponse(BaseModel):
    id: uuid.UUID
    exam_id: uuid.UUID
    status: AttemptStatus
    started_at: datetime | None = None
    total_questions: int
    answered_count: int


class SubmitAnswerRequest(BaseModel):
    question_id: uuid.UUID
    selected_option_ids: list[uuid.UUID]


class AnswerResultResponse(BaseModel):
    question_id: uuid.UUID
    question_content: str
    is_correct: bool
    selected_option_ids: list[uuid.UUID]
    correct_option_ids: list[uuid.UUID]
    explanation: str | None = None


class AttemptResultResponse(BaseModel):
    attempt_id: uuid.UUID
    exam_title: str
    score_percentage: float
    is_passed: bool
    duration_seconds: int | None = None
    total_questions: int
    correct_answers: int
    finished_at: datetime | None = None
    answers: list[AnswerResultResponse] = []


class AttemptHistoryResponse(BaseModel):
    id: uuid.UUID
    exam_id: uuid.UUID
    status: AttemptStatus
    score_percentage: float | None = None
    is_passed: bool | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_seconds: int | None = None
