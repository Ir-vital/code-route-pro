"""Tests d'intégration des endpoints d'authentification."""

import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    @pytest.mark.asyncio
    async def test_register(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Password1",
                "first_name": "Jean",
                "last_name": "Dupont",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "WrongPass1"},
        )
        assert response.status_code == 401
