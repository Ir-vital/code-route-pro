"""Interfaces repository du module exams."""

import uuid
from abc import ABC, abstractmethod

from app.modules.exams.domain.entities import (
    AttemptAnswerEntity,
    ExamAttemptEntity,
    ExamEntity,
    QuestionEntity,
)
from app.shared.domain.enums import AttemptStatus, Difficulty


class IQuestionRepository(ABC):

    @abstractmethod
    async def get_by_id(self, question_id: uuid.UUID) -> QuestionEntity | None: ...

    @abstractmethod
    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        category_id: uuid.UUID | None = None,
        difficulty: Difficulty | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[QuestionEntity], int]: ...

    @abstractmethod
    async def get_random_for_exam(
        self,
        count: int,
        *,
        category_id: uuid.UUID | None = None,
        difficulty: Difficulty | None = None,
    ) -> list[QuestionEntity]: ...

    @abstractmethod
    async def create(self, entity: QuestionEntity) -> QuestionEntity: ...

    @abstractmethod
    async def update(self, entity: QuestionEntity) -> QuestionEntity: ...

    @abstractmethod
    async def delete(self, question_id: uuid.UUID) -> None: ...


class IExamRepository(ABC):

    @abstractmethod
    async def get_by_id(self, exam_id: uuid.UUID) -> ExamEntity | None: ...

    @abstractmethod
    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        is_active: bool | None = True,
    ) -> tuple[list[ExamEntity], int]: ...

    @abstractmethod
    async def create(self, entity: ExamEntity) -> ExamEntity: ...

    @abstractmethod
    async def update(self, entity: ExamEntity) -> ExamEntity: ...

    @abstractmethod
    async def delete(self, exam_id: uuid.UUID) -> None: ...


class IExamAttemptRepository(ABC):

    @abstractmethod
    async def get_by_id(self, attempt_id: uuid.UUID) -> ExamAttemptEntity | None: ...

    @abstractmethod
    async def get_by_user(
        self,
        user_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[ExamAttemptEntity], int]: ...

    @abstractmethod
    async def get_in_progress(
        self, user_id: uuid.UUID, exam_id: uuid.UUID
    ) -> ExamAttemptEntity | None: ...

    @abstractmethod
    async def create(self, entity: ExamAttemptEntity) -> ExamAttemptEntity: ...

    @abstractmethod
    async def update(self, entity: ExamAttemptEntity) -> ExamAttemptEntity: ...

    @abstractmethod
    async def save_answer(self, answer: AttemptAnswerEntity) -> AttemptAnswerEntity: ...

    @abstractmethod
    async def get_answer(
        self, attempt_id: uuid.UUID, question_id: uuid.UUID
    ) -> AttemptAnswerEntity | None: ...
