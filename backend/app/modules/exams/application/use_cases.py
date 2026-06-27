"""Use cases du module exams."""

import uuid
from datetime import UTC, datetime

from app.core.exceptions import ForbiddenException, NotFoundException, UnprocessableException
from app.modules.exams.application.dtos import (
    AnswerResultDTO,
    AttemptResultDTO,
    CreateExamDTO,
    CreateQuestionDTO,
    StartAttemptDTO,
    SubmitAnswerDTO,
    SubmitAttemptDTO,
    UpdateExamDTO,
    UpdateQuestionDTO,
)
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
from app.shared.domain.enums import AttemptStatus
from app.shared.pagination import PaginatedResponse, PaginationParams


# ─── Questions ────────────────────────────────────────────────────────────────

class ListQuestionsUseCase:
    def __init__(self, repo: IQuestionRepository) -> None:
        self._repo = repo

    async def execute(
        self, *, offset: int = 0, limit: int = 20,
        category_id: uuid.UUID | None = None, **kwargs
    ) -> tuple[list[QuestionEntity], int]:
        return await self._repo.get_all(
            offset=offset, limit=limit, category_id=category_id, **kwargs
        )


class GetQuestionUseCase:
    def __init__(self, repo: IQuestionRepository) -> None:
        self._repo = repo

    async def execute(self, question_id: uuid.UUID) -> QuestionEntity:
        q = await self._repo.get_by_id(question_id)
        if not q:
            raise NotFoundException("Question", str(question_id))
        return q


class CreateQuestionUseCase:
    def __init__(self, repo: IQuestionRepository) -> None:
        self._repo = repo

    async def execute(self, dto: CreateQuestionDTO) -> QuestionEntity:
        if len(dto.options) < 2:
            raise UnprocessableException("Une question doit avoir au moins 2 options")
        correct_count = sum(1 for o in dto.options if o.is_correct)
        if correct_count == 0:
            raise UnprocessableException("Une question doit avoir au moins une bonne réponse")

        import uuid as _uuid
        question_id = _uuid.uuid4()

        entity = QuestionEntity(
            id=question_id,
            category_id=dto.category_id,
            content=dto.content,
            question_type=dto.question_type,
            difficulty=dto.difficulty,
            sign_id=dto.sign_id,
            image_url=dto.image_url,
            explanation=dto.explanation,
            options=[
                QuestionOptionEntity(
                    question_id=question_id,
                    content=o.content,
                    is_correct=o.is_correct,
                    display_order=o.display_order,
                )
                for o in dto.options
            ],
        )
        return await self._repo.create(entity)


class UpdateQuestionUseCase:
    def __init__(self, repo: IQuestionRepository) -> None:
        self._repo = repo

    async def execute(self, dto: UpdateQuestionDTO) -> QuestionEntity:
        q = await self._repo.get_by_id(dto.question_id)
        if not q:
            raise NotFoundException("Question", str(dto.question_id))
        if dto.content is not None:
            q.content = dto.content
        if dto.explanation is not None:
            q.explanation = dto.explanation
        if dto.difficulty is not None:
            q.difficulty = dto.difficulty
        if dto.is_active is not None:
            q.is_active = dto.is_active
        return await self._repo.update(q)


class DeleteQuestionUseCase:
    def __init__(self, repo: IQuestionRepository) -> None:
        self._repo = repo

    async def execute(self, question_id: uuid.UUID) -> None:
        if not await self._repo.get_by_id(question_id):
            raise NotFoundException("Question", str(question_id))
        await self._repo.delete(question_id)


# ─── Examens ──────────────────────────────────────────────────────────────────

class ListExamsUseCase:
    def __init__(self, repo: IExamRepository) -> None:
        self._repo = repo

    async def execute(self, *, offset: int = 0, limit: int = 20) -> tuple[list[ExamEntity], int]:
        return await self._repo.get_all(offset=offset, limit=limit, is_active=True)


class CreateExamUseCase:
    def __init__(self, repo: IExamRepository) -> None:
        self._repo = repo

    async def execute(self, dto: CreateExamDTO) -> ExamEntity:
        entity = ExamEntity(
            title=dto.title,
            exam_type=dto.exam_type,
            question_count=dto.question_count,
            time_limit_seconds=dto.time_limit_seconds,
            description=dto.description,
            category_id=dto.category_id,
            passing_score_percentage=dto.passing_score_percentage,
            difficulty=dto.difficulty,
        )
        return await self._repo.create(entity)


class UpdateExamUseCase:
    def __init__(self, repo: IExamRepository) -> None:
        self._repo = repo

    async def execute(self, dto: UpdateExamDTO) -> ExamEntity:
        exam = await self._repo.get_by_id(dto.exam_id)
        if not exam:
            raise NotFoundException("Examen", str(dto.exam_id))
        if dto.title is not None:
            exam.title = dto.title
        if dto.description is not None:
            exam.description = dto.description
        if dto.question_count is not None:
            exam.question_count = dto.question_count
        if dto.time_limit_seconds is not None:
            exam.time_limit_seconds = dto.time_limit_seconds
        if dto.passing_score_percentage is not None:
            exam.passing_score_percentage = dto.passing_score_percentage
        if dto.is_active is not None:
            exam.is_active = dto.is_active
        return await self._repo.update(exam)


class DeleteExamUseCase:
    def __init__(self, repo: IExamRepository) -> None:
        self._repo = repo

    async def execute(self, exam_id: uuid.UUID) -> None:
        if not await self._repo.get_by_id(exam_id):
            raise NotFoundException("Examen", str(exam_id))
        await self._repo.delete(exam_id)


# ─── Tentatives ───────────────────────────────────────────────────────────────

class StartAttemptUseCase:
    def __init__(
        self,
        exam_repo: IExamRepository,
        question_repo: IQuestionRepository,
        attempt_repo: IExamAttemptRepository,
    ) -> None:
        self._exam_repo = exam_repo
        self._question_repo = question_repo
        self._attempt_repo = attempt_repo

    async def execute(self, dto: StartAttemptDTO) -> ExamAttemptEntity:
        exam = await self._exam_repo.get_by_id(dto.exam_id)
        if not exam:
            raise NotFoundException("Examen", str(dto.exam_id))
        if not exam.is_active:
            raise UnprocessableException("Cet examen n'est plus disponible")

        # Tirage aléatoire des questions
        questions = await self._question_repo.get_random_for_exam(
            exam.question_count,
            category_id=exam.category_id,
            difficulty=None if exam.difficulty.value == "mixed" else exam.difficulty,
        )
        if len(questions) < exam.question_count:
            raise UnprocessableException(
                f"Pas assez de questions disponibles (demandées: {exam.question_count}, "
                f"disponibles: {len(questions)})"
            )

        attempt = ExamAttemptEntity(
            user_id=dto.user_id,
            exam_id=dto.exam_id,
            started_at=datetime.now(UTC),
        )
        saved_attempt = await self._attempt_repo.create(attempt)

        # Snapshot des questions
        saved_attempt.questions = [
            AttemptQuestionEntity(
                attempt_id=saved_attempt.id,
                question_id=q.id,
                display_order=idx,
            )
            for idx, q in enumerate(questions)
        ]
        return await self._attempt_repo.update(saved_attempt)


class GetAttemptUseCase:
    def __init__(self, repo: IExamAttemptRepository) -> None:
        self._repo = repo

    async def execute(self, attempt_id: uuid.UUID, user_id: uuid.UUID) -> ExamAttemptEntity:
        attempt = await self._repo.get_by_id(attempt_id)
        if not attempt:
            raise NotFoundException("Tentative", str(attempt_id))
        if attempt.user_id != user_id:
            raise ForbiddenException()
        return attempt


class SubmitAnswerUseCase:
    def __init__(
        self,
        attempt_repo: IExamAttemptRepository,
        question_repo: IQuestionRepository,
    ) -> None:
        self._attempt_repo = attempt_repo
        self._question_repo = question_repo

    async def execute(self, dto: SubmitAnswerDTO) -> AttemptAnswerEntity:
        attempt = await self._attempt_repo.get_by_id(dto.attempt_id)
        if not attempt:
            raise NotFoundException("Tentative", str(dto.attempt_id))
        if attempt.user_id != dto.user_id:
            raise ForbiddenException()
        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise UnprocessableException("Cette tentative est déjà terminée")

        # Vérifier que la question fait partie de la tentative
        question_ids = {aq.question_id for aq in attempt.questions}
        if dto.question_id not in question_ids:
            raise UnprocessableException("Cette question ne fait pas partie de cet examen")

        answer = AttemptAnswerEntity(
            attempt_id=dto.attempt_id,
            question_id=dto.question_id,
            selected_option_ids=dto.selected_option_ids,
            answered_at=datetime.now(UTC),
        )
        return await self._attempt_repo.save_answer(answer)


class SubmitAttemptUseCase:
    """
    Finalise une tentative : calcule le score, marque comme terminée,
    retourne le résultat détaillé, déclenche le service post-examen.
    """

    def __init__(
        self,
        attempt_repo: IExamAttemptRepository,
        exam_repo: IExamRepository,
        question_repo: IQuestionRepository,
        db_session=None,  # AsyncSession optionnelle pour le post-exam service
    ) -> None:
        self._attempt_repo = attempt_repo
        self._exam_repo = exam_repo
        self._question_repo = question_repo
        self._db_session = db_session

    async def execute(self, dto: SubmitAttemptDTO) -> AttemptResultDTO:
        attempt = await self._attempt_repo.get_by_id(dto.attempt_id)
        if not attempt:
            raise NotFoundException("Tentative", str(dto.attempt_id))
        if attempt.user_id != dto.user_id:
            raise ForbiddenException()
        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise UnprocessableException("Cette tentative est déjà terminée")

        exam = await self._exam_repo.get_by_id(attempt.exam_id)
        if not exam:
            raise NotFoundException("Examen", str(attempt.exam_id))

        # Récupérer toutes les questions avec leurs options
        question_map: dict[uuid.UUID, QuestionEntity] = {}
        for aq in attempt.questions:
            q = await self._question_repo.get_by_id(aq.question_id)
            if q:
                question_map[q.id] = q

        # Corriger les réponses
        answers_result: list[AnswerResultDTO] = []
        correct_count = 0

        for aq in attempt.questions:
            question = question_map.get(aq.question_id)
            if not question:
                continue

            answer = await self._attempt_repo.get_answer(attempt.id, aq.question_id)
            selected_ids = answer.selected_option_ids if answer else []
            correct_ids = question.correct_option_ids

            is_correct = set(selected_ids) == set(correct_ids)
            if is_correct:
                correct_count += 1

            # Persister la correction
            if answer:
                answer.is_correct = is_correct
                await self._attempt_repo.save_answer(answer)

            answers_result.append(
                AnswerResultDTO(
                    question_id=question.id,
                    question_content=question.content,
                    is_correct=is_correct,
                    selected_option_ids=selected_ids,
                    correct_option_ids=correct_ids,
                    explanation=question.explanation,
                )
            )

        total = len(attempt.questions)
        score_pct = (correct_count / total * 100) if total > 0 else 0.0
        is_passed = score_pct >= exam.passing_score_percentage
        now = datetime.now(UTC)
        duration = int((now - attempt.started_at).total_seconds()) if attempt.started_at else None

        attempt.status = AttemptStatus.COMPLETED
        attempt.finished_at = now
        attempt.duration_seconds = duration
        attempt.score_percentage = score_pct
        attempt.is_passed = is_passed
        await self._attempt_repo.update(attempt)

        result = AttemptResultDTO(
            attempt_id=attempt.id,
            exam_title=exam.title,
            score_percentage=score_pct,
            is_passed=is_passed,
            duration_seconds=duration,
            total_questions=total,
            correct_answers=correct_count,
            finished_at=now,
            answers=answers_result,
        )

        # Déclencher le service post-examen si une session DB est disponible
        if self._db_session is not None:
            from app.modules.exams.application.post_exam_service import PostExamService
            svc = PostExamService(self._db_session)
            await svc.process(
                user_id=attempt.user_id,
                exam_id=attempt.exam_id,
                category_id=exam.category_id,
                result=result,
            )

        return result


class GetAttemptHistoryUseCase:
    def __init__(self, repo: IExamAttemptRepository) -> None:
        self._repo = repo

    async def execute(
        self, user_id: uuid.UUID, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[ExamAttemptEntity], int]:
        return await self._repo.get_by_user(user_id, offset=offset, limit=limit)


class GetAttemptResultUseCase:
    def __init__(
        self,
        attempt_repo: IExamAttemptRepository,
        exam_repo: IExamRepository,
        question_repo: IQuestionRepository,
    ) -> None:
        self._attempt_repo = attempt_repo
        self._exam_repo = exam_repo
        self._question_repo = question_repo

    async def execute(self, attempt_id: uuid.UUID, user_id: uuid.UUID) -> AttemptResultDTO:
        attempt = await self._attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise NotFoundException("Tentative", str(attempt_id))
        if attempt.user_id != user_id:
            raise ForbiddenException()
        if not attempt.is_complete:
            raise UnprocessableException("Cette tentative n'est pas encore terminée")

        exam = await self._exam_repo.get_by_id(attempt.exam_id)
        exam_title = exam.title if exam else "Examen supprimé"

        answers_result: list[AnswerResultDTO] = []
        correct_count = 0

        for aq in attempt.questions:
            question = await self._question_repo.get_by_id(aq.question_id)
            if not question:
                continue
            answer = await self._attempt_repo.get_answer(attempt.id, aq.question_id)
            selected_ids = answer.selected_option_ids if answer else []
            is_correct = answer.is_correct if answer else False
            if is_correct:
                correct_count += 1
            answers_result.append(
                AnswerResultDTO(
                    question_id=question.id,
                    question_content=question.content,
                    is_correct=bool(is_correct),
                    selected_option_ids=selected_ids,
                    correct_option_ids=question.correct_option_ids,
                    explanation=question.explanation,
                )
            )

        return AttemptResultDTO(
            attempt_id=attempt.id,
            exam_title=exam_title,
            score_percentage=attempt.score_percentage or 0.0,
            is_passed=attempt.is_passed or False,
            duration_seconds=attempt.duration_seconds,
            total_questions=len(attempt.questions),
            correct_answers=correct_count,
            finished_at=attempt.finished_at,
            answers=answers_result,
        )
