"""Router FastAPI du module auth — /api/v1/auth"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import RateLimitException
from app.core.redis import RedisCache, get_redis
from app.modules.auth.api.dependencies import CurrentUser
from app.modules.auth.api.schemas import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenPairResponse,
    UserResponse,
)
from app.modules.auth.application.dtos import (
    ForgotPasswordDTO,
    LoginDTO,
    LogoutRequest as LogoutDTO,
    RefreshTokenDTO,
    RegisterDTO,
    ResetPasswordDTO,
)
from app.modules.auth.application.use_cases import (
    ForgotPasswordUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
    RegisterUseCase,
    ResetPasswordUseCase,
)
from app.modules.auth.infrastructure.repositories import (
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    UserRepository,
)
from app.core.config import settings
from redis.asyncio import Redis

router = APIRouter(prefix="/auth", tags=["Auth"])


# ─── POST /register ───────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte élève",
)
async def register(
    body: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    use_case = RegisterUseCase(UserRepository(db))
    user = await use_case.execute(
        RegisterDTO(
            email=body.email,
            password=body.password,
            first_name=body.first_name,
            last_name=body.last_name,
        )
    )
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        avatar_url=user.avatar_url,
    )


# ─── POST /login ──────────────────────────────────────────────────────────────

@router.post("/login", response_model=AuthResponse, summary="Authentification")
async def login(
    body: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> AuthResponse:
    # Rate limiting
    cache = RedisCache(redis, prefix="rate_limit:login")
    client_ip = request.client.host if request.client else "unknown"
    count = await cache.increment(f"ip:{client_ip}", ttl=settings.LOGIN_RATE_LIMIT_WINDOW)
    if count > settings.LOGIN_RATE_LIMIT:
        raise RateLimitException()

    use_case = LoginUseCase(UserRepository(db), RefreshTokenRepository(db))
    result = await use_case.execute(
        LoginDTO(
            email=body.email,
            password=body.password,
            user_agent=request.headers.get("user-agent"),
            ip_address=client_ip,
        )
    )
    return AuthResponse(
        user=UserResponse(
            id=result.user_id,
            email=result.email,
            first_name=result.first_name,
            last_name=result.last_name,
            role=result.role,
            is_active=True,
            is_verified=False,
        ),
        tokens=TokenPairResponse(
            access_token=result.tokens.access_token,
            refresh_token=result.tokens.refresh_token,
        ),
    )


# ─── POST /refresh ────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenPairResponse, summary="Renouveler l'access token")
async def refresh_token(
    body: RefreshTokenRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenPairResponse:
    use_case = RefreshTokenUseCase(UserRepository(db), RefreshTokenRepository(db))
    tokens = await use_case.execute(
        RefreshTokenDTO(
            refresh_token=body.refresh_token,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
    )
    return TokenPairResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


# ─── POST /logout ─────────────────────────────────────────────────────────────

@router.post("/logout", response_model=MessageResponse, summary="Déconnexion")
async def logout(
    body: LogoutRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
    _: CurrentUser,
) -> MessageResponse:
    # Extraire l'access token du header pour le blacklister
    access_token: str | None = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ", 1)[1]

    use_case = LogoutUseCase(RefreshTokenRepository(db), redis=redis)
    await use_case.execute(body.refresh_token, access_token=access_token)
    return MessageResponse(message="Déconnexion réussie")


# ─── POST /forgot-password ────────────────────────────────────────────────────

@router.post("/forgot-password", response_model=MessageResponse, summary="Demande de réinitialisation")
async def forgot_password(
    body: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    use_case = ForgotPasswordUseCase(
        UserRepository(db), PasswordResetTokenRepository(db)
    )
    await use_case.execute(ForgotPasswordDTO(email=body.email))
    # Toujours répondre 200 pour éviter l'énumération d'emails
    return MessageResponse(message="Si cet email existe, un lien de réinitialisation a été envoyé.")


# ─── POST /reset-password ─────────────────────────────────────────────────────

@router.post("/reset-password", response_model=MessageResponse, summary="Réinitialiser le mot de passe")
async def reset_password(
    body: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    use_case = ResetPasswordUseCase(
        UserRepository(db),
        PasswordResetTokenRepository(db),
        RefreshTokenRepository(db),
    )
    await use_case.execute(ResetPasswordDTO(token=body.token, new_password=body.new_password))
    return MessageResponse(message="Mot de passe réinitialisé avec succès.")


# ─── GET /me ──────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse, summary="Profil de l'utilisateur courant")
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        avatar_url=current_user.avatar_url,
    )
