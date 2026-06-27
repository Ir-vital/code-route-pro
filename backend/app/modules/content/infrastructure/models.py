"""Modèles SQLAlchemy du module content."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.domain.enums import Difficulty
from app.shared.mixins import TimestampMixin, UUIDMixin


class CategoryModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    signs: Mapped[list["SignModel"]] = relationship(back_populates="category")


class SignModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "signs"

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    official_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    meaning: Mapped[str] = mapped_column(Text, nullable=False)
    rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, name="difficulty_enum"),
        nullable=False,
        default=Difficulty.EASY,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped["CategoryModel"] = relationship(back_populates="signs")
    favorites: Mapped[list["FavoriteModel"]] = relationship(
        back_populates="sign", cascade="all, delete-orphan"
    )


class FavoriteModel(Base, UUIDMixin):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "sign_id", name="uq_favorites_user_sign"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("signs.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow()
    )

    sign: Mapped["SignModel"] = relationship(back_populates="favorites")
