"""
Configuration du logging JSON structuré.
En production : logs JSON parsables par Datadog, Loki, CloudWatch, etc.
En développement : logs lisibles avec couleurs (via rich).
"""

import logging
import sys
from typing import Any

from app.core.config import settings

try:
    import structlog

    _USE_STRUCTLOG = True
except ImportError:
    _USE_STRUCTLOG = False


def setup_logging() -> None:
    """Configure le logging de l'application."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    if _USE_STRUCTLOG:
        import structlog

        processors: list[Any] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
        ]

        if settings.is_production:
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
        )
    else:
        # Fallback sur le logging standard
        log_format = (
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
            if settings.is_production
            else "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
        logging.basicConfig(
            level=log_level,
            format=log_format,
            stream=sys.stdout,
        )

    # Réduire le bruit des librairies tierces
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DATABASE_ECHO else logging.WARNING
    )


def get_logger(name: str) -> Any:
    """Retourne un logger pour le module donné."""
    if _USE_STRUCTLOG:
        import structlog
        return structlog.get_logger(name)
    return logging.getLogger(name)
