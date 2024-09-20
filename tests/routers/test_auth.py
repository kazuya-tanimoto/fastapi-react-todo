from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from main import app

client = TestClient(app)


# MongoDBコレクションをモックするためのヘルパーフィクスチャ
@pytest.fixture
def mock_user_service(mocker):
    mock_service = MagicMock()
    mock_service.authenticate = AsyncMock(return_value="jwt_token")
    mock_service.register = AsyncMock(return_value={"email": "test@example.com"})
    mocker.patch("services.user.UserService", return_value=mock_service)
    return mock_service


def test_generate_csrf_token() -> None:
    response = client.get("/api/csrf-token")
    assert response.status_code == 200
    assert "csrf_token" in response.json()


def test_signup(mock_user_service) -> None:
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    register_email = datetime.now().strftime("%Y%m%d%H%M%S") + "@example.com"

    headers = {"X-CSRF-Token": csrf_token}
    user_data = {"email": register_email, "password": "Password_1234567"}
    # user_data = {"email": "testuser@example.com", "password": "Password_1234567"}

    response = client.post("/api/register", json=user_data, headers=headers)
    print(response.json())
    assert response.status_code == 200
    assert "email" in response.json()
    assert response.json()["email"] == register_email


@pytest.mark.anyio
async def test_login(mock_user_service) -> None:
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    headers = {"X-CSRF-Token": csrf_token}
    user_data = {"email": "test@example.com", "password": "password"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as ac:
        response = await ac.post("/api/login", json=user_data, headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    mock_user_service.authenticate.assert_called_once_with(user_data)


def test_logout() -> None:
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    headers = {"X-CSRF-Token": csrf_token}

    response = client.post("/api/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"


@pytest.mark.anyio
async def test_get_user_refresh_jwt(mock_user_service) -> None:
    # ログイン処理をモック
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    headers = {"X-CSRF-Token": csrf_token}
    user_data = {"email": "test@example.com", "password": "password"}

    # ログインしてCookieを取得
    login_response = client.post("/api/login", json=user_data, headers=headers)
    assert login_response.status_code == 200

    cookies = login_response.cookies

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as ac:
        response = await ac.get("/api/user", cookies=cookies)

    assert response.status_code == 200
    assert "email" in response.json()
    assert response.json()["email"] == "test@example.com"
