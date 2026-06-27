"""Exceptions métier spécifiques au module auth."""

from app.core.exceptions import (
    AlreadyExistsException,
    BadRequestException,
    ForbiddenException,
    InvalidCredentialsException,
    InvalidTokenException,
    NotFoundException,
    RateLimitException,
    TokenExpiredException,
    UnauthorizedException,
)


class UserAlreadyExistsException(AlreadyExistsException):
    def __init__(self) -> None:
        super().__init__("Un compte avec cet email")


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: str | None = None) -> None:
        super().__init__("Utilisateur", user_id)


class UserInactiveException(ForbiddenException):
    def __init__(self) -> None:
        super().__init__("Ce compte est désactivé. Contactez le support.")


class InvalidPasswordException(BadRequestException):
    def __init__(self) -> None:
        super().__init__("Mot de passe incorrect", code="INVALID_PASSWORD")


class PasswordResetTokenExpiredException(TokenExpiredException):
    pass


class PasswordResetTokenInvalidException(InvalidTokenException):
    pass


class PasswordResetTokenAlreadyUsedException(BadRequestException):
    def __init__(self) -> None:
        super().__init__("Ce lien de réinitialisation a déjà été utilisé", code="TOKEN_ALREADY_USED")


# Re-export des exceptions core utilisées par ce module
__all__ = [
    "UserAlreadyExistsException",
    "UserNotFoundException",
    "UserInactiveException",
    "InvalidPasswordException",
    "InvalidCredentialsException",
    "UnauthorizedException",
    "RateLimitException",
    "PasswordResetTokenExpiredException",
    "PasswordResetTokenInvalidException",
    "PasswordResetTokenAlreadyUsedException",
]
