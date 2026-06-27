"""Modèles SQLAlchemy du module progress."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.mixins import UUIDMixin


class UserProgressModel(Base):
    """Progression globale de l'utilisateur — relation 1:1 avec users."""
    __tablename__ = "user_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    xp_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow()
    )


class CategoryMasteryModel(Base, UUIDMixin):
    """Taux de maîtrise par catégorie pour un utilisateur."""
    __tablename__ = "category_mastery"
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", name="uq_category_mastery_user_cat"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    mastery_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    last_practiced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
