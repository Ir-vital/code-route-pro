"""
Exceptions métier de base et handlers FastAPI.
Toutes les exceptions métier héritent de AppException pour un traitement uniforme.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


# ─── Exceptions de base ───────────────────────────────────────────────────────

class AppException(Exception):
    """Exception de base pour toutes les erreurs métier de l'application."""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


# ─── Erreurs 400 ──────────────────────────────────────────────────────────────

class ValidationException(AppException):
    def __init__(self, message: str = "Données invalides", details: dict | None = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR", status_code=400, details=details)


class BadRequestException(AppException):
    def __init__(self, message: str = "Requête invalide", code: str = "BAD_REQUEST") -> None:
        super().__init__(message, code=code, status_code=400)


# ─── Erreurs 401 / 403 ────────────────────────────────────────────────────────

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentification requise") -> None:
        super().__init__(message, code="UNAUTHORIZED", status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Accès interdit") -> None:
        super().__init__(message, code="FORBIDDEN", status_code=403)


class InvalidCredentialsException(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Email ou mot de passe incorrect",
            code="INVALID_CREDENTIALS",
            status_code=401,
        )


class TokenExpiredException(AppException):
    def __init__(self) -> None:
        super().__init__("Token expiré", code="TOKEN_EXPIRED", status_code=401)


class InvalidTokenException(AppException):
    def __init__(self) -> None:
        super().__init__("Token invalide", code="INVALID_TOKEN", status_code=401)


# ─── Erreurs 404 ──────────────────────────────────────────────────────────────

class NotFoundException(AppException):
    def __init__(self, resource: str = "Ressource", resource_id: str | None = None) -> None:
        message = f"{resource} introuvable"
        if resource_id:
            message = f"{resource} '{resource_id}' introuvable"
        super().__init__(message, code="NOT_FOUND", status_code=404)


# ─── Erreurs 409 ──────────────────────────────────────────────────────────────

class ConflictException(AppException):
    def __init__(self, message: str = "Conflit de données", code: str = "CONFLICT") -> None:
        super().__init__(message, code=code, status_code=409)


class AlreadyExistsException(AppException):
    def __init__(self, resource: str = "Ressource") -> None:
        super().__init__(f"{resource} existe déjà", code="ALREADY_EXISTS", status_code=409)


# ─── Erreurs 422 ──────────────────────────────────────────────────────────────

class UnprocessableException(AppException):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, code="UNPROCESSABLE", status_code=422, details=details)


# ─── Erreurs 429 ──────────────────────────────────────────────────────────────

class RateLimitException(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Trop de tentatives. Réessayez dans quelques minutes.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )


# ─── Handlers FastAPI ─────────────────────────────────────────────────────────

def _error_response(code: str, message: str, status_code: int, details: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Enregistre tous les handlers d'exceptions sur l'application FastAPI."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return _error_response(exc.code, exc.message, exc.status_code, exc.details)

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        return _error_response("NOT_FOUND", "Endpoint introuvable", 404)

    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc: Exception) -> JSONResponse:
        return _error_response("METHOD_NOT_ALLOWED", "Méthode non autorisée", 405)
