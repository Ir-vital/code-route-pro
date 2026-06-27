"""
Énumérations partagées entre les modules.
Ces types appartiennent au domaine — aucune dépendance externe.
"""

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    STUDENT = "student"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    MIXED = "mixed"


class ExamType(StrEnum):
    PRACTICE = "practice"
    MOCK_OFFICIAL = "mock_official"
    CATEGORY_FOCUS = "category_focus"


class AttemptStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class QuestionType(StrEnum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"


class BadgeCriteriaType(StrEnum):
    EXAM_COUNT = "exam_count"
    PERFECT_SCORE = "perfect_score"
    STREAK = "streak"
    CATEGORY_MASTERY = "category_mastery"


class NotificationType(StrEnum):
    EXAM_RESULT = "exam_result"
    NEW_EXAM_AVAILABLE = "new_exam_available"
    PROGRESS_UPDATE = "progress_update"
    BADGE_EARNED = "badge_earned"
    SYSTEM = "system"
