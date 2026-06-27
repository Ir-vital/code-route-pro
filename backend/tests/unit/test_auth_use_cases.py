"""
Tests unitaires des use cases d'authentification.
Utilise des mocks de repositories — aucune I/O réelle.
"""

from unittest.mock import AsyncMock

import pytest

from app.modules.auth.application.dtos import RegisterDTO
from app.modules.auth.application.use_cases import RegisterUseCase
from app.modules.auth.domain.exceptions import UserAlreadyExistsException


class TestRegisterUseCase:
    @pytest.mark.asyncio
    async def test_register_success(self):
        mock_repo = AsyncMock()
        mock_repo.email_exists.return_value = False
        mock_repo.create.side_effect = lambda e: e

        uc = RegisterUseCase(mock_repo)
        user = await uc.execute(
            RegisterDTO(
                email="test@example.com",
                password="Password1",
                first_name="Jean",
                last_name="Dupont",
            )
        )
        assert user.email == "test@example.com"
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        mock_repo = AsyncMock()
        mock_repo.email_exists.return_value = True

        uc = RegisterUseCase(mock_repo)
        with pytest.raises(UserAlreadyExistsException):
            await uc.execute(
                RegisterDTO(
                    email="existing@example.com",
                    password="Password1",
                    first_name="Jean",
                    last_name="Dupont",
                )
            )
