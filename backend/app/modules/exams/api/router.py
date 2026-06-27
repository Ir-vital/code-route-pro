"""Router FastAPI du module exams — /api/v1/exams, /api/v1/questions"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.api.dependencies import CurrentAdmin, CurrentUser
from app.modules.exams.api.schemas import (
    AnswerResultResponse,
    AttemptHistoryResponse,
    AttemptResponse,
    AttemptResultResponse,
    CreateExamRequest,
    CreateQuestionRequest,
    ExamResponse,
    QuestionResponse,
    SubmitAnswerRequest,
    UpdateExamRequest,
    UpdateQuestionRequest,
)
from app.modules.exams.application.dtos import (
    CreateExamDTO,
    CreateQuestionDTO,
    CreateQuestionOptionDTO,
    StartAttemptDTO,
    SubmitAnswerDTO,
    SubmitAttemptDTO,
    UpdateExamDTO,
    UpdateQuestionDTO,
)
from app.modules.exams.application.use_cases import (
    CreateExamUseCase,
    CreateQuestionUseCase,
    DeleteExamUseCase,
    DeleteQuestionUseCase,
    GetAttemptHistoryUseCase,
    GetAttemptResultUseCase,
    GetAttemptUseCase,
    ListExamsUseCase,
    ListQuestionsUseCase,
    StartAttemptUseCase,
    SubmitAnswerUseCase,
    SubmitAttemptUseCase,
    UpdateExamUseCase,
    UpdateQuestionUseCase,
)
from app.modules.exams.infrastructure.repositories import (
    ExamAttemptRepository,
    ExamRepository,
    QuestionRepository,
)
from app.shared.pagination import PaginatedResponse, PaginationParams

# ─── Questions (Admin) ────────────────────────────────────────────────────────
questions_router = APIRouter(prefix="/questions", tags=["Exams — Questions (Admin)"])


@questions_router.get("/", response_model=PaginatedResponse[QuestionResponse])
async def list_questions(
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category_id: uuid.UUID | None = Query(default=None),
) -> PaginatedResponse[QuestionResponse]:
    params = PaginationParams(page=page, page_size=page_size)
    uc = ListQuestionsUseCase(QuestionRepository(db))
    questions, total = await uc.execute(
        offset=params.offset, limit=params.limit, category_id=category_id
    )
    items = [_q_to_response(q) for q in questions]
    return PaginatedResponse.create(items=items, total=total, params=params)


@questions_router.get("/{question_id}", response_model=QuestionResponse, summary="[Admin] Détail d'une question")
async def get_question(
    question_id: uuid.UUID,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuestionResponse:
    uc = GetQuestionUseCase(QuestionRepository(db))
    q = await uc.execute(question_id)
    return _q_to_response(q)


@questions_router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    body: CreateQuestionRequest,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuestionResponse:
    uc = CreateQuestionUseCase(QuestionRepository(db))
    dto = CreateQuestionDTO(
        category_id=body.category_id,
        content=body.content,
        question_type=body.question_type,
        difficulty=body.difficulty,
        sign_id=body.sign_id,
        image_url=body.image_url,
        explanation=body.explanation,
        options=[
            CreateQuestionOptionDTO(
                content=o.content, is_correct=o.is_correct, display_order=o.display_order
            )
            for o in body.options
        ],
    )
    q = await uc.execute(dto)
    return _q_to_response(q)


@questions_router.patch("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: uuid.UUID,
    body: UpdateQuestionRequest,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuestionResponse:
    uc = UpdateQuestionUseCase(QuestionRepository(db))
    q = await uc.execute(UpdateQuestionDTO(question_id=question_id, **body.model_dump()))
    return _q_to_response(q)


@questions_router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: uuid.UUID,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await DeleteQuestionUseCase(QuestionRepository(db)).execute(question_id)


# ─── Examens ──────────────────────────────────────────────────────────────────
exams_router = APIRouter(prefix="/exams", tags=["Exams"])


@exams_router.get("/", response_model=PaginatedResponse[ExamResponse])
async def list_exams(
    _user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[ExamResponse]:
    params = PaginationParams(page=page, page_size=page_size)
    uc = ListExamsUseCase(ExamRepository(db))
    exams, total = await uc.execute(offset=params.offset, limit=params.limit)
    items = [_exam_to_response(e) for e in exams]
    return PaginatedResponse.create(items=items, total=total, params=params)


@exams_router.post("/", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(
    body: CreateExamRequest,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExamResponse:
    uc = CreateExamUseCase(ExamRepository(db))
    e = await uc.execute(CreateExamDTO(**body.model_dump()))
    return _exam_to_response(e)


@exams_router.patch("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: uuid.UUID,
    body: UpdateExamRequest,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExamResponse:
    uc = UpdateExamUseCase(ExamRepository(db))
    e = await uc.execute(UpdateExamDTO(exam_id=exam_id, **body.model_dump()))
    return _exam_to_response(e)


@exams_router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: uuid.UUID,
    _admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await DeleteExamUseCase(ExamRepository(db)).execute(exam_id)


# ─── Tentatives ───────────────────────────────────────────────────────────────

@exams_router.post("/{exam_id}/start", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED)
async def start_attempt(
    exam_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AttemptResponse:
    uc = StartAttemptUseCase(ExamRepository(db), QuestionRepository(db), ExamAttemptRepository(db))
    attempt = await uc.execute(StartAttemptDTO(user_id=current_user.id, exam_id=exam_id))
    return AttemptResponse(
        id=attempt.id, exam_id=attempt.exam_id, status=attempt.status,
        started_at=attempt.started_at,
        total_questions=attempt.total_questions,
        answered_count=attempt.answered_count,
    )


@exams_router.get("/attempts", response_model=PaginatedResponse[AttemptHistoryResponse])
async def my_attempts(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[AttemptHistoryResponse]:
    params = PaginationParams(page=page, page_size=page_size)
    uc = GetAttemptHistoryUseCase(ExamAttemptRepository(db))
    attempts, total = await uc.execute(current_user.id, offset=params.offset, limit=params.limit)
    items = [
        AttemptHistoryResponse(
            id=a.id, exam_id=a.exam_id, status=a.status,
            score_percentage=a.score_percentage, is_passed=a.is_passed,
            started_at=a.started_at, finished_at=a.finished_at,
            duration_seconds=a.duration_seconds,
        )
        for a in attempts
    ]
    return PaginatedResponse.create(items=items, total=total, params=params)


@exams_router.get("/attempts/{attempt_id}", response_model=AttemptResponse)
async def get_attempt(
    attempt_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AttemptResponse:
    uc = GetAttemptUseCase(ExamAttemptRepository(db))
    attempt = await uc.execute(attempt_id, current_user.id)
    return AttemptResponse(
        id=attempt.id, exam_id=attempt.exam_id, status=attempt.status,
        started_at=attempt.started_at,
        total_questions=attempt.total_questions,
        answered_count=attempt.answered_count,
    )


@exams_router.get("/attempts/{attempt_id}/questions", response_model=list[dict])
async def get_attempt_questions(
    attempt_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[dict]:
    """
    Retourne les questions d'une tentative en cours — sans is_correct sur les options.
    Utilisé par l'interface de passage d'examen.
    """
    uc = GetAttemptUseCase(ExamAttemptRepository(db))
    attempt = await uc.execute(attempt_id, current_user.id)

    questions = []
    for aq in attempt.questions:
        q = await QuestionRepository(db).get_by_id(aq.question_id)
        if not q:
            continue
        questions.append({
            "id": str(q.id),
            "content": q.content,
            "image_url": q.image_url,
            "question_type": q.question_type.value,
            "options": [
                {
                    "id": str(opt.id),
                    "content": opt.content,
                    "display_order": opt.display_order,
                    # is_correct volontairement omis
                }
                for opt in sorted(q.options, key=lambda o: o.display_order)
            ],
        })
    # Trier par display_order de la tentative
    order_map = {aq.question_id: aq.display_order for aq in attempt.questions}
    questions.sort(key=lambda q: order_map.get(uuid.UUID(q["id"]), 0))
    return questions


@exams_router.post("/attempts/{attempt_id}/answer", response_model=dict)
async def submit_answer(
    attempt_id: uuid.UUID,
    body: SubmitAnswerRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    uc = SubmitAnswerUseCase(ExamAttemptRepository(db), QuestionRepository(db))
    await uc.execute(
        SubmitAnswerDTO(
            attempt_id=attempt_id,
            question_id=body.question_id,
            selected_option_ids=body.selected_option_ids,
            user_id=current_user.id,
        )
    )
    return {"message": "Réponse enregistrée"}


@exams_router.post("/attempts/{attempt_id}/submit", response_model=AttemptResultResponse)
async def submit_attempt(
    attempt_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AttemptResultResponse:
    uc = SubmitAttemptUseCase(
        ExamAttemptRepository(db),
        ExamRepository(db),
        QuestionRepository(db),
        db_session=db,  # Passe la session pour le post-exam service
    )
    result = await uc.execute(SubmitAttemptDTO(attempt_id=attempt_id, user_id=current_user.id))
    return _result_to_response(result)


@exams_router.get("/attempts/{attempt_id}/result", response_model=AttemptResultResponse)
async def get_attempt_result(
    attempt_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AttemptResultResponse:
    uc = GetAttemptResultUseCase(ExamAttemptRepository(db), ExamRepository(db), QuestionRepository(db))
    result = await uc.execute(attempt_id, current_user.id)
    return _result_to_response(result)


# ─── Helpers de mapping ───────────────────────────────────────────────────────

def _q_to_response(q) -> QuestionResponse:
    from app.modules.exams.api.schemas import QuestionOptionWithCorrectResponse
    return QuestionResponse(
        id=q.id, category_id=q.category_id, sign_id=q.sign_id,
        content=q.content, image_url=q.image_url, explanation=q.explanation,
        question_type=q.question_type, difficulty=q.difficulty, is_active=q.is_active,
        options=[
            QuestionOptionWithCorrectResponse(
                id=o.id, content=o.content, display_order=o.display_order, is_correct=o.is_correct
            )
            for o in q.options
        ],
    )


def _exam_to_response(e) -> ExamResponse:
    return ExamResponse(
        id=e.id, title=e.title, description=e.description,
        exam_type=e.exam_type, category_id=e.category_id,
        question_count=e.question_count, time_limit_seconds=e.time_limit_seconds,
        passing_score_percentage=e.passing_score_percentage,
        difficulty=e.difficulty, is_active=e.is_active,
    )


def _result_to_response(r) -> AttemptResultResponse:
    return AttemptResultResponse(
        attempt_id=r.attempt_id, exam_title=r.exam_title,
        score_percentage=r.score_percentage, is_passed=r.is_passed,
        duration_seconds=r.duration_seconds,
        total_questions=r.total_questions, correct_answers=r.correct_answers,
        finished_at=r.finished_at,
        answers=[
            AnswerResultResponse(
                question_id=a.question_id, question_content=a.question_content,
                is_correct=a.is_correct, selected_option_ids=a.selected_option_ids,
                correct_option_ids=a.correct_option_ids, explanation=a.explanation,
            )
            for a in r.answers
        ],
    )
