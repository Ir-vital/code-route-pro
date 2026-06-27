"""
Use cases du module auth.
Chaque classe = une action métier unique (SRP).
Aucune dépendance sur FastAPI, SQLAlchemy ou Redis directement.
"""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.modules.auth.application.dtos import (
    AuthUserDTO,
    ChangePasswordDTO,
    ForgotPasswordDTO,
    LoginDTO,
    RefreshTokenDTO,
    RegisterDTO,
    ResetPasswordDTO,
    TokenPairDTO,
)
from app.modules.auth.domain.entities import (
    PasswordResetTokenEntity,
    RefreshTokenEntity,
    UserEntity,
)
from app.modules.auth.domain.exceptions import (
    InvalidCredentialsException,
    InvalidPasswordException,
    PasswordResetTokenAlreadyUsedException,
    PasswordResetTokenExpiredException,
    PasswordResetTokenInvalidException,
    UserAlreadyExistsException,
    UserInactiveException,
    UserNotFoundException,
)
from app.modules.auth.domain.repositories import (
    IPasswordResetTokenRepository,
    IRefreshTokenRepository,
    IUserRepository,
)


def _hash_token(token: str) -> str:
    """Hache un token brut avant stockage (SHA-256)."""
    return hashlib.sha256(token.encode()).hexdigest()


class RegisterUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, dto: RegisterDTO) -> UserEntity:
        if await self._user_repo.email_exists(dto.email.lower()):
            raise UserAlreadyExistsException()

        user = UserEntity(
            email=dto.email.lower().strip(),
            hashed_password=hash_password(dto.password),
            first_name=dto.first_name.strip(),
            last_name=dto.last_name.strip(),
        )
        created = await self._user_repo.create(user)

        # Email de bienvenue (non-bloquant)
        from app.core.email import get_email_service, render_welcome_email
        html, text = render_welcome_email(created.first_name)
        await get_email_service().send(created.email, "Bienvenue sur CodeRoute Pro !", html, text)

        return created


class LoginUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        refresh_token_repo: IRefreshTokenRepository,
    ) -> None:
        self._user_repo = user_repo
        self._refresh_token_repo = refresh_token_repo

    async def execute(self, dto: LoginDTO) -> AuthUserDTO:
        user = await self._user_repo.get_by_email(dto.email.lower())
        if not user:
            raise InvalidCredentialsException()

        if not verify_password(dto.password, user.hashed_password):
            raise InvalidCredentialsException()

        if not user.can_login():
            raise UserInactiveException()

        # Mise à jour du last_login_at
        user.last_login_at = datetime.now(UTC)
        await self._user_repo.update(user)

        # Génération des tokens
        extra_claims = {"role": user.role.value}
        access_token = create_access_token(str(user.id), extra_claims)
        raw_refresh = create_refresh_token(str(user.id))

        # Persistance du refresh token (hash uniquement)
        refresh_entity = RefreshTokenEntity(
            user_id=user.id,
            token_hash=_hash_token(raw_refresh),
            expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            user_agent=dto.user_agent,
            ip_address=dto.ip_address,
        )
        await self._refresh_token_repo.create(refresh_entity)

        return AuthUserDTO(
            user_id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            tokens=TokenPairDTO(
                access_token=access_token,
                refresh_token=raw_refresh,
            ),
        )


class RefreshTokenUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        refresh_token_repo: IRefreshTokenRepository,
    ) -> None:
        self._user_repo = user_repo
        self._refresh_token_repo = refresh_token_repo

    async def execute(self, dto: RefreshTokenDTO) -> TokenPairDTO:
        from app.core.security import verify_refresh_token
        from jose import JWTError

        try:
            payload = verify_refresh_token(dto.refresh_token)
        except JWTError:
            raise InvalidCredentialsException()

        token_record = await self._refresh_token_repo.get_by_token_hash(
            _hash_token(dto.refresh_token)
        )
        if not token_record or not token_record.is_valid:
            raise InvalidCredentialsException()

        user_id = uuid.UUID(payload["sub"])
        user = await self._user_repo.get_by_id(user_id)
        if not user or not user.can_login():
            raise InvalidCredentialsException()

        # Rotation du refresh token (révocation de l'ancien, émission d'un nouveau)
        await self._refresh_token_repo.revoke(token_record.id)

        extra_claims = {"role": user.role.value}
        new_access = create_access_token(str(user.id), extra_claims)
        new_refresh = create_refresh_token(str(user.id))

        new_refresh_entity = RefreshTokenEntity(
            user_id=user.id,
            token_hash=_hash_token(new_refresh),
            expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            user_agent=dto.user_agent,
            ip_address=dto.ip_address,
        )
        await self._refresh_token_repo.create(new_refresh_entity)

        return TokenPairDTO(access_token=new_access, refresh_token=new_refresh)


class LogoutUseCase:
    def __init__(
        self,
        refresh_token_repo: IRefreshTokenRepository,
        redis=None,  # Client Redis optionnel pour blacklister l'access token
    ) -> None:
        self._refresh_token_repo = refresh_token_repo
        self._redis = redis

    async def execute(self, raw_refresh_token: str, access_token: str | None = None) -> None:
        # Révoquer le refresh token en base
        token_record = await self._refresh_token_repo.get_by_token_hash(
            _hash_token(raw_refresh_token)
        )
        if token_record and not token_record.is_revoked:
            await self._refresh_token_repo.revoke(token_record.id)

        # Blacklister l'access token dans Redis (durée = sa durée de vie restante)
        if self._redis and access_token:
            from app.core.security import decode_token
            from jose import JWTError
            try:
                payload = decode_token(access_token)
                exp = payload.get("exp", 0)
                from datetime import UTC, datetime
                ttl = max(0, int(exp - datetime.now(UTC).timestamp()))
                if ttl > 0:
                    await self._redis.setex(
                        f"blacklist:access:{_hash_token(access_token)}",
                        ttl,
                        "1",
                    )
            except JWTError:
                pass  # Token déjà invalide, pas besoin de le blacklister


class ForgotPasswordUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        reset_token_repo: IPasswordResetTokenRepository,
    ) -> None:
        self._user_repo = user_repo
        self._reset_token_repo = reset_token_repo

    async def execute(self, dto: ForgotPasswordDTO) -> None:
        """
        Génère un token de réinitialisation et envoie l'email.
        Toujours répondre 200 côté API pour éviter l'énumération d'emails.
        """
        user = await self._user_repo.get_by_email(dto.email.lower())
        if not user:
            return  # Silencieux volontairement

        raw_token = secrets.token_urlsafe(32)
        entity = PasswordResetTokenEntity(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(
                hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
            ),
        )
        await self._reset_token_repo.create(entity)

        # Envoi de l'email de réinitialisation
        from app.core.email import get_email_service, render_password_reset_email
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
        html, text = render_password_reset_email(reset_url, user.first_name)
        await get_email_service().send(
            user.email,
            "Réinitialisation de votre mot de passe — CodeRoute Pro",
            html,
            text,
        )


class ResetPasswordUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        reset_token_repo: IPasswordResetTokenRepository,
        refresh_token_repo: IRefreshTokenRepository,
    ) -> None:
        self._user_repo = user_repo
        self._reset_token_repo = reset_token_repo
        self._refresh_token_repo = refresh_token_repo

    async def execute(self, dto: ResetPasswordDTO) -> None:
        token_record = await self._reset_token_repo.get_by_token_hash(
            _hash_token(dto.token)
        )
        if not token_record:
            raise PasswordResetTokenInvalidException()
        if token_record.is_used:
            raise PasswordResetTokenAlreadyUsedException()
        if token_record.is_expired:
            raise PasswordResetTokenExpiredException()

        user = await self._user_repo.get_by_id(token_record.user_id)
        if not user:
            raise UserNotFoundException()

        user.hashed_password = hash_password(dto.new_password)
        await self._user_repo.update(user)
        await self._reset_token_repo.mark_used(token_record.id)
        # Invalider toutes les sessions existantes
        await self._refresh_token_repo.revoke_all_for_user(user.id)


class ChangePasswordUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, dto: ChangePasswordDTO) -> None:
        user = await self._user_repo.get_by_id(dto.user_id)
        if not user:
            raise UserNotFoundException()

        if not verify_password(dto.current_password, user.hashed_password):
            raise InvalidPasswordException()

        user.hashed_password = hash_password(dto.new_password)
        await self._user_repo.update(user)
