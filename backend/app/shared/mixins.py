"""
Mixins SQLAlchemy réutilisables par tous les modèles.
- UUIDMixin     : clé primaire UUID générée automatiquement
- TimestampMixin: created_at / updated_at gérés automatiquement
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """Clé primaire UUID auto-générée côté Python (pas côté DB)."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampMixin:
    """
    Colonnes created_at / updated_at gérées automatiquement.
    - created_at : set à l'INSERT, jamais modifié après
    - updated_at : set à l'INSERT et mis à jour à chaque UPDATE
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
