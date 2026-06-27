"""
Service post-examen : orchestrateur déclenché après SubmitAttemptUseCase.
Responsabilités :
  1. Mettre à jour user_progress (XP, level, streak)
  2. Mettre à jour category_mastery
  3. Vérifier et attribuer les badges
  4. Générer une notification (REST + push WebSocket)
  5. Recalculer les recommandations
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.exams.application.dtos import AttemptResultDTO
from app.modules.gamification.infrastructure.models import BadgeModel, UserBadgeModel
from app.modules.notifications.infrastructure.models import NotificationModel
from app.modules.progress.infrastructure.models import CategoryMasteryModel, UserProgressModel
from app.modules.recommendations.infrastructure.models import RecommendationModel
from app.shared.domain.enums import AttemptStatus, BadgeCriteriaType, NotificationType

if TYPE_CHECKING:
    pass

# ─── Constantes de gamification ──────────────────────────────────────────────
XP_PER_EXAM_PASSED = 50
XP_PER_EXAM_FAILED = 10
XP_PER_CORRECT_ANSWER = 2
XP_PER_LEVEL = 100  # XP nécessaires pour passer un niveau


class PostExamService:
    """
    Service applicatif déclenché après la finalisation d'une tentative.
    Reçoit la session DB et les données du résultat.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def process(
        self,
        user_id: uuid.UUID,
        exam_id: uuid.UUID,
        category_id: uuid.UUID | None,
        result: AttemptResultDTO,
    ) -> None:
        """Point d'entrée principal. Non-bloquant : les erreurs sont loggées, pas reraisées."""
        try:
            xp_earned = await self._update_progress(user_id, result)
            await self._update_category_mastery(user_id, category_id, result)
            new_badges = await self._check_and_award_badges(user_id)
            await self._create_exam_notification(user_id, result, new_badges, xp_earned)
            await self._update_recommendations(user_id)
            await self._db.flush()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                "post_exam_service error", extra={"user_id": str(user_id), "error": str(e)}
            )

    # ─── 1. Progression (XP, level, streak) ──────────────────────────────────

    async def _update_progress(
        self, user_id: uuid.UUID, result: AttemptResultDTO
    ) -> int:
        """Retourne le nombre de XP gagnés."""
        xp_earned = (
            XP_PER_EXAM_PASSED if result.is_passed else XP_PER_EXAM_FAILED
        ) + result.correct_answers * XP_PER_CORRECT_ANSWER

        now = datetime.now(UTC)

        result_row = await self._db.execute(
            select(UserProgressModel).where(UserProgressModel.user_id == user_id)
        )
        progress = result_row.scalar_one_or_none()

        if not progress:
            # Créer l'entrée si elle n'existe pas encore
            progress = UserProgressModel()
            progress.user_id = user_id
            progress.level = 1
            progress.xp_points = 0
            progress.current_streak_days = 0
            progress.longest_streak_days = 0
            self._db.add(progress)
            await self._db.flush()

        new_xp = progress.xp_points + xp_earned
        new_level = max(1, new_xp // XP_PER_LEVEL + 1)

        # Calcul streak
        # Si last_update était hier → +1, si aujourd'hui déjà → inchangé, sinon reset
        new_streak = progress.current_streak_days
        last_updated = progress.updated_at
        if last_updated:
            last_date = last_updated.date() if hasattr(last_updated, 'date') else last_updated
            today = now.date()
            delta = (today - last_date).days
            if delta == 1:
                new_streak += 1
            elif delta > 1:
                new_streak = 1
            # delta == 0 : même jour, streak inchangé

        new_longest = max(progress.longest_streak_days, new_streak)

        await self._db.execute(
            update(UserProgressModel)
            .where(UserProgressModel.user_id == user_id)
            .values(
                xp_points=new_xp,
                level=new_level,
                current_streak_days=new_streak,
                longest_streak_days=new_longest,
                updated_at=now,
            )
        )
        return xp_earned

    # ─── 2. Maîtrise par catégorie ────────────────────────────────────────────

    async def _update_category_mastery(
        self,
        user_id: uuid.UUID,
        category_id: uuid.UUID | None,
        result: AttemptResultDTO,
    ) -> None:
        if not category_id:
            return

        score = result.score_percentage
        now = datetime.now(UTC)

        existing = await self._db.execute(
            select(CategoryMasteryModel).where(
                CategoryMasteryModel.user_id == user_id,
                CategoryMasteryModel.category_id == category_id,
            )
        )
        mastery = existing.scalar_one_or_none()

        if mastery:
            # Moyenne pondérée : 70% nouveau score + 30% historique
            new_mastery = round(0.7 * score + 0.3 * float(mastery.mastery_percentage), 2)
            await self._db.execute(
                update(CategoryMasteryModel)
                .where(
                    CategoryMasteryModel.user_id == user_id,
                    CategoryMasteryModel.category_id == category_id,
                )
                .values(mastery_percentage=new_mastery, last_practiced_at=now)
            )
        else:
            m = CategoryMasteryModel()
            m.user_id = user_id
            m.category_id = category_id
            m.mastery_percentage = score
            m.last_practiced_at = now
            self._db.add(m)

    # ─── 3. Badges ────────────────────────────────────────────────────────────

    async def _check_and_award_badges(self, user_id: uuid.UUID) -> list[str]:
        """Vérifie tous les critères de badges et retourne les noms des nouveaux badges."""
        # Charger les badges déjà obtenus
        earned_result = await self._db.execute(
            select(UserBadgeModel.badge_id).where(UserBadgeModel.user_id == user_id)
        )
        already_earned_ids = {row[0] for row in earned_result.all()}

        # Charger tous les badges du catalogue
        all_badges = await self._db.execute(select(BadgeModel))
        badges = all_badges.scalars().all()

        # Stats actuelles
        progress_row = await self._db.execute(
            select(UserProgressModel).where(UserProgressModel.user_id == user_id)
        )
        progress = progress_row.scalar_one_or_none()

        # Nombre d'examens complétés
        from app.modules.exams.infrastructure.models import ExamAttemptModel
        exam_count_row = await self._db.execute(
            select(func.count(ExamAttemptModel.id)).where(
                ExamAttemptModel.user_id == user_id,
                ExamAttemptModel.status == AttemptStatus.COMPLETED,
            )
        )
        exam_count = exam_count_row.scalar_one()

        # Nombre de scores parfaits
        perfect_row = await self._db.execute(
            select(func.count(ExamAttemptModel.id)).where(
                ExamAttemptModel.user_id == user_id,
                ExamAttemptModel.score_percentage == 100,
            )
        )
        perfect_count = perfect_row.scalar_one()

        # Maîtrise maximale des catégories
        mastery_row = await self._db.execute(
            select(func.max(CategoryMasteryModel.mastery_percentage)).where(
                CategoryMasteryModel.user_id == user_id
            )
        )
        max_mastery = float(mastery_row.scalar_one() or 0)

        streak_days = progress.current_streak_days if progress else 0

        new_badge_names: list[str] = []
        now = datetime.now(UTC)

        for badge in badges:
            if badge.id in already_earned_ids:
                continue

            earned = False
            criteria = BadgeCriteriaType(badge.criteria_type)

            if criteria == BadgeCriteriaType.EXAM_COUNT and exam_count >= badge.criteria_value:
                earned = True
            elif criteria == BadgeCriteriaType.PERFECT_SCORE and perfect_count >= badge.criteria_value:
                earned = True
            elif criteria == BadgeCriteriaType.STREAK and streak_days >= badge.criteria_value:
                earned = True
            elif criteria == BadgeCriteriaType.CATEGORY_MASTERY and max_mastery >= badge.criteria_value:
                earned = True

            if earned:
                ub = UserBadgeModel()
                ub.user_id = user_id
                ub.badge_id = badge.id
                ub.earned_at = now
                self._db.add(ub)
                new_badge_names.append(badge.name)

        return new_badge_names

    # ─── 4. Notifications ─────────────────────────────────────────────────────

    async def _create_exam_notification(
        self,
        user_id: uuid.UUID,
        result: AttemptResultDTO,
        new_badges: list[str],
        xp_earned: int,
    ) -> None:
        now = datetime.now(UTC)

        # Notification résultat d'examen
        exam_notif = NotificationModel()
        exam_notif.user_id = user_id
        exam_notif.type = NotificationType.EXAM_RESULT
        status_label = "Examen réussi" if result.is_passed else "Examen non validé"
        exam_notif.title = f"{status_label} — {result.exam_title}"
        exam_notif.message = (
            f"{result.correct_answers}/{result.total_questions} bonnes réponses "
            f"({result.score_percentage:.1f}%) · +{xp_earned} XP"
        )
        exam_notif.payload = {
            "attempt_id": str(result.attempt_id),
            "score": result.score_percentage,
            "is_passed": result.is_passed,
            "xp_earned": xp_earned,
        }
        exam_notif.created_at = now
        self._db.add(exam_notif)

        # Notifications badges débloqués
        for badge_name in new_badges:
            badge_notif = NotificationModel()
            badge_notif.user_id = user_id
            badge_notif.type = NotificationType.BADGE_EARNED
            badge_notif.title = f"Nouveau badge : {badge_name}"
            badge_notif.message = f"Félicitations ! Vous avez débloqué le badge « {badge_name} »."
            badge_notif.payload = {"badge_name": badge_name}
            badge_notif.created_at = now
            self._db.add(badge_notif)

        # Push WebSocket (non-bloquant — si le manager n'est pas disponible, on ignore)
        try:
            from app.modules.notifications.api.router import ws_manager
            payload = {
                "type": "exam_result",
                "score": result.score_percentage,
                "is_passed": result.is_passed,
                "xp_earned": xp_earned,
                "new_badges": new_badges,
            }
            await ws_manager.send_to_user(str(user_id), payload)
        except Exception:
            pass

    # ─── 5. Recommandations ───────────────────────────────────────────────────

    async def _update_recommendations(self, user_id: uuid.UUID) -> None:
        """
        Recalcule les recommandations : catégories avec le plus faible taux de maîtrise.
        Remplace les recommandations non-dismissées existantes.
        """
        from app.modules.content.infrastructure.models import CategoryModel

        # Supprimer les anciennes recommandations non-dismissées
        existing = await self._db.execute(
            select(RecommendationModel).where(
                RecommendationModel.user_id == user_id,
                RecommendationModel.is_dismissed == False,  # noqa: E712
            )
        )
        for old in existing.scalars().all():
            await self._db.delete(old)

        # Catégories les moins maîtrisées (max 3 recommandations)
        mastery_rows = await self._db.execute(
            select(CategoryMasteryModel)
            .where(CategoryMasteryModel.user_id == user_id)
            .order_by(CategoryMasteryModel.mastery_percentage.asc())
            .limit(3)
        )
        weak_masteries = mastery_rows.scalars().all()

        # Catégories jamais pratiquées (pour les nouveaux utilisateurs)
        if len(weak_masteries) < 3:
            practiced_cat_ids = {m.category_id for m in weak_masteries}
            unpracticed = await self._db.execute(
                select(CategoryModel)
                .where(
                    CategoryModel.is_active == True,  # noqa: E712
                    CategoryModel.id.notin_(practiced_cat_ids),
                )
                .limit(3 - len(weak_masteries))
            )
            unpracticed_cats = unpracticed.scalars().all()
        else:
            unpracticed_cats = []

        now = datetime.now(UTC)

        for i, mastery in enumerate(weak_masteries):
            rec = RecommendationModel()
            rec.user_id = user_id
            rec.category_id = mastery.category_id
            rec.reason = f"Maîtrise à {float(mastery.mastery_percentage):.0f}% — à renforcer"
            rec.priority = 10 - i
            rec.generated_at = now
            self._db.add(rec)

        for i, cat in enumerate(unpracticed_cats):
            rec = RecommendationModel()
            rec.user_id = user_id
            rec.category_id = cat.id
            rec.reason = "Catégorie jamais pratiquée"
            rec.priority = 5 - i
            rec.generated_at = now
            self._db.add(rec)
