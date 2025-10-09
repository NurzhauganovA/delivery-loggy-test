import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_cdek_auth_success(monkeypatch):
    """Проверяем, что при корректном secret_key возвращается JWT токен"""

    # Подменяем конфигурацию на тестовую
    monkeypatch.setenv("CDEK_SECRET_KEY", "123456")
    monkeypatch.setenv("CDEK_EXPIRATION_SECONDS", "3600")
    monkeypatch.setenv("CDEK_ALGORITHM", "HS256")

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v2/crm/auth-cdek",
            json={"secret_key": "123456"}
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Проверяем, что структура ответа корректная
    assert "access_token" in data
    assert "token_type" in data
    assert "expires_in" in data
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 3600


@pytest.mark.asyncio
async def test_cdek_auth_invalid_key():
    """Проверяем, что при неверном ключе возвращается 401"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v2/crm/auth-cdek",
            json={"secret_key": "wrong_key"}
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == "Invalid secret key"
