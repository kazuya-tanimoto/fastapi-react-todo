from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
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
    # Get CSRF token
    response = client.get("/api/csrf-token")
    assert response.status_code == 200, "Failed to get CSRF token"
    assert "csrf_token" in response.json(), "CSRF token not in response"

    # Verify that the CSRF cookie is set
    csrf_cookie = response.cookies.get("fastapi-csrf-token")
    assert csrf_cookie is not None, "'fastapi-csrf-token' Cookie not set"


def test_signup(mock_user_service) -> None:
    # Get CSRF token
    response = client.get("/api/csrf-token")
    assert response.status_code == 200, "Failed to get CSRF token"
    csrf_token = response.json().get("csrf_token")

    # Register a new user
    register_email = datetime.now().strftime("%Y%m%d%H%M%S") + "@example.com"
    user_data = {"email": register_email, "password": "Password_1234567"}
    headers = {"X-CSRF-Token": csrf_token}
    response = client.post("/api/register", json=user_data, headers=headers)

    # Verify that the user was registered
    print(response.json())
    assert response.status_code == 200, "Failed to register user"
    assert "email" in response.json(), "Email not in response"
    assert response.json()["email"] == register_email, "Email does not match"


@pytest.mark.asyncio
async def test_login(mock_user_service) -> None:
    # Get CSRF token
    response = client.get("/api/csrf-token")
    assert response.status_code == 200, "Failed to get CSRF token"
    csrf_token = response.json().get("csrf_token")

    # Login
    headers = {"X-CSRF-Token": csrf_token}
    user_data = {"email": "test@example.com", "password": "password"}
    response = client.post("/api/login", json=user_data, headers=headers)

    # Verify that the user was logged in
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"


def test_logout() -> None:
    # Get CSRF token
    response = client.get("/api/csrf-token")
    assert response.status_code == 200, "Failed to get CSRF token"
    csrf_token = response.json().get("csrf_token")

    # Logout
    headers = {"X-CSRF-Token": csrf_token}
    response = client.post("/api/logout", headers=headers)

    # Verify that the user was logged out
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"


async def test_get_user_refresh_jwt(mock_user_service) -> None:
    # Get CSRF token
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    headers = {"X-CSRF-Token": csrf_token}
    user_data = {"email": "test@example.com", "password": "password"}

    # Login for JWT
    login_response = client.post("/api/login", json=user_data, headers=headers)
    assert login_response.status_code == 200

    # Set JWT cookie
    login_cookie = login_response.cookies.get("access_token")
    client.cookies.set("access_token", login_cookie)

    # Get user info
    response = client.get("/api/user")
    assert response.status_code == 200
    assert "email" in response.json()
    assert response.json()["email"] == "test@example.com"
