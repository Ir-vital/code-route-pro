"""Modèles SQLAlchemy du module gamification."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.domain.enums import BadgeCriteriaType
from app.shared.mixins import UUIDMixin


class BadgeModel(Base, UUIDMixin):
    __tablename__ = "badges"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    criteria_type: Mapped[BadgeCriteriaType] = mapped_column(
        Enum(BadgeCriteriaType, name="badge_criteria_type_enum"), nullable=False
    )
    criteria_value: Mapped[int] = mapped_column(Integer, nullable=False)


class UserBadgeModel(Base, UUIDMixin):
    __tablename__ = "user_badges"
    __table_args__ = (
        UniqueConstraint("user_id", "badge_id", name="uq_user_badges_user_badge"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    badge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("badges.id", ondelete="CASCADE"),
        nullable=False,
    )
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
