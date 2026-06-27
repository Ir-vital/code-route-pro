"""
Point d'entrée de l'application FastAPI.
Initialise l'app, enregistre les middlewares, les handlers et les routers.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api_router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.middleware import register_middlewares
from app.core.redis import close_redis_pool, get_redis_pool
from app.modules.notifications.api.router import ws_router

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestion du cycle de vie : startup / shutdown."""
    logger.info("Starting up CodeRoute Pro API", env=settings.ENV)

    # Vérification de la connexion Redis au démarrage
    try:
        redis = await get_redis_pool()
        await redis.ping()
        logger.info("Redis connection OK")
    except Exception as e:
        logger.warning("Redis connection failed", error=str(e))

    # Démarrer le listener WebSocket Redis pub/sub
    from app.modules.notifications.infrastructure.ws_manager import ws_manager
    await ws_manager.start()

    yield

    logger.info("Shutting down...")
    await ws_manager.stop()
    await close_redis_pool()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API de la plateforme d'apprentissage du code de la route",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Middlewares
    register_middlewares(app)

    # Handlers d'exceptions
    register_exception_handlers(app)

    # Routers REST
    app.include_router(api_router)

    # Router WebSocket (hors préfixe /api/v1)
    app.include_router(ws_router)

    # Health check
    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok", "version": settings.APP_VERSION})

    return app


app = create_app()
