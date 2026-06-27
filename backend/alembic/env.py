"""
Configuration Alembic pour les migrations async (asyncpg).
Importe tous les modèles pour que la détection d'autogenerate fonctionne.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ─── Import de la Base et de tous les modèles ─────────────────────────────────
# Tous les modèles doivent être importés ici pour qu'Alembic les détecte.
from app.core.database import Base  # noqa: F401
from app.core.config import settings

# Modules — imports pour enregistrer les modèles dans la metadata
from app.modules.auth.infrastructure.models import (  # noqa: F401
    UserModel, RefreshTokenModel, PasswordResetTokenModel,
)
from app.modules.content.infrastructure.models import (  # noqa: F401
    CategoryModel, SignModel, FavoriteModel,
)
from app.modules.exams.infrastructure.models import (  # noqa: F401
    QuestionModel, QuestionOptionModel, ExamModel,
    ExamAttemptModel, AttemptQuestionModel, AttemptAnswerModel, AttemptAnswerOptionModel,
)
from app.modules.progress.infrastructure.models import (  # noqa: F401
    UserProgressModel, CategoryMasteryModel,
)
from app.modules.gamification.infrastructure.models import (  # noqa: F401
    BadgeModel, UserBadgeModel,
)
from app.modules.recommendations.infrastructure.models import RecommendationModel  # noqa: F401
from app.modules.notifications.infrastructure.models import NotificationModel  # noqa: F401
from app.modules.admin.infrastructure.models import AuditLogModel  # noqa: F401

# ─── Config Alembic ───────────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override avec l'URL depuis les settings Python (ignore alembic.ini sqlalchemy.url)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
