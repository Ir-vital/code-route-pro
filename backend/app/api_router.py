"""
Agrégateur de tous les routers /api/v1.
Ce fichier est le seul endroit où les routers de modules sont enregistrés.
"""

from fastapi import APIRouter

from app.modules.admin.api.router import router as admin_router
from app.modules.auth.api.router import router as auth_router
from app.modules.content.api.router import (
    categories_router,
    favorites_router,
    signs_router,
)
from app.modules.exams.api.router import exams_router, questions_router
from app.modules.gamification.api.router import router as badges_router
from app.modules.notifications.api.router import router as notifications_router
from app.modules.progress.api.router import router as dashboard_router
from app.modules.recommendations.api.router import router as recommendations_router
from app.modules.users.api.router import router as users_router

api_router = APIRouter(prefix="/api/v1")

# ─── Auth & Users ─────────────────────────────────────────────────────────────
api_router.include_router(auth_router)
api_router.include_router(users_router)

# ─── Content ──────────────────────────────────────────────────────────────────
api_router.include_router(categories_router)
api_router.include_router(signs_router)
api_router.include_router(favorites_router)

# ─── Exams ────────────────────────────────────────────────────────────────────
api_router.include_router(questions_router)
api_router.include_router(exams_router)

# ─── Dashboard / Progress ────────────────────────────────────────────────────
api_router.include_router(dashboard_router)
api_router.include_router(recommendations_router, prefix="/dashboard")

# ─── Gamification ─────────────────────────────────────────────────────────────
api_router.include_router(badges_router)

# ─── Notifications ────────────────────────────────────────────────────────────
api_router.include_router(notifications_router)

# ─── Admin ────────────────────────────────────────────────────────────────────
api_router.include_router(admin_router)
