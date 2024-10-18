from datetime import datetime

import pytest
from httpx import AsyncClient

# @pytest.mark.asyncio
# async def test_generate_csrf_token(async_client: AsyncClient):
#     # CSRFトークンを取得
#     response = await async_client.get("/api/csrf-token")
#     assert response.status_code == 200, "Failed to get CSRF token"
#     assert "csrf_token" in response.json(), "CSRF token not in response"
#
#     # クッキーが設定されていることを確認
#     csrf_cookie = response.cookies.get("fastapi-csrf-token")
#     assert csrf_cookie is not None, "'fastapi-csrf-token' Cookie not set"


@pytest.mark.asyncio
async def test_signup(async_client: AsyncClient, mock_user_service):
    # CSRFトークンを取得
    csrf_response = await async_client.get("/api/csrf-token")
    assert csrf_response.status_code == 200, "Failed to get CSRF token"
    csrf_token = csrf_response.json().get("csrf_token")
    assert csrf_token is not None, "CSRF token not in response"

    # クッキーが設定されていることを確認
    csrf_cookie = csrf_response.cookies.get("fastapi-csrf-token")
    assert csrf_cookie is not None, "'fastapi-csrf-token' Cookie not set"

    # ユーザー登録データの準備
    register_email = datetime.now().strftime("%Y%m%d%H%M%S") + "@example.com"
    user_data = {"email": register_email, "password": "Password_1234567"}
    headers = {"X-CSRF-Token": csrf_token}

    # ユーザー登録
    response = await async_client.post("/api/register", json=user_data, headers=headers)
    assert response.status_code == 200, "Failed to register user"
    assert "email" in response.json(), "Email not in response"
    assert response.json()["email"] == register_email, "Email does not match"


@pytest.mark.asyncio
async def test_login(async_client: AsyncClient, mock_user_service):
    # CSRFトークンを取得
    csrf_response = await async_client.get("/api/csrf-token")
    assert csrf_response.status_code == 200, "Failed to get CSRF token"
    csrf_token = csrf_response.json().get("csrf_token")
    assert csrf_token is not None, "CSRF token not in response"

    # クッキーが設定されていることを確認
    csrf_cookie = csrf_response.cookies.get("fastapi-csrf-token")
    assert csrf_cookie is not None, "'fastapi-csrf-token' Cookie not set"

    # ログインデータの準備
    headers = {"X-CSRF-Token": csrf_token}
    user_data = {"email": "test@example.com", "password": "password"}

    # ログイン
    login_response = await async_client.post("/api/login", json=user_data, headers=headers)
    assert login_response.status_code == 200, "Failed to login"
    assert login_response.json()["message"] == "Login successful", "Login message mismatch"
    assert login_response.cookies.get("access_token") is not None, "'access_token' Cookie not set"


@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient, mock_user_service):
    # CSRFトークンを取得
    csrf_response = await async_client.get("/api/csrf-token")
    assert csrf_response.status_code == 200, "Failed to get CSRF token"
    csrf_token = csrf_response.json().get("csrf_token")
    assert csrf_token is not None, "CSRF token not in response"

    # クッキーが設定されていることを確認
    csrf_cookie = csrf_response.cookies.get("fastapi-csrf-token")
    assert csrf_cookie is not None, "'fastapi-csrf-token' Cookie not set"

    # ログアウトヘッダーの準備
    headers = {"X-CSRF-Token": csrf_token}

    # ログアウト
    response = await async_client.post("/api/logout", headers=headers)
    assert response.status_code == 200, "Failed to logout"
    assert response.json()["message"] == "Logout successful", "Logout message mismatch"


@pytest.mark.asyncio
async def test_get_user_refresh_jwt(async_client: AsyncClient, mock_user_service):
    # CSRFトークンを取得
    csrf_response = await async_client.get("/api/csrf-token")
    assert csrf_response.status_code == 200, "Failed to get CSRF token"
    csrf_token = csrf_response.json().get("csrf_token")
    assert csrf_token is not None, "CSRF token not in response"

    # クッキーが設定されていることを確認
    csrf_cookie = csrf_response.cookies.get("fastapi-csrf-token")
    assert csrf_cookie is not None, "'fastapi-csrf-token' Cookie not set"

    # ログインデータの準備
    headers = {"X-CSRF-Token": csrf_token}
    user_data = {"email": "test@example.com", "password": "password"}

    # ログインしてCookieを取得
    login_response = await async_client.post("/api/login", json=user_data, headers=headers)
    assert login_response.status_code == 200, "Failed to login"

    # アクセストークンがクッキーに設定されていることを確認
    access_token_cookie = login_response.cookies.get("access_token")
    assert access_token_cookie is not None, "'access_token' Cookie not set"

    # AsyncClientにクッキーをセット（不要な場合は削除）
    async_client.cookies.set("access_token", access_token_cookie, domain="testserver.local", path="/")

    # /api/user にアクセス
    response = await async_client.get("/api/user")
    assert response.status_code == 200, "Failed to get user info"
    assert "email" in response.json(), "Email not in response"
    assert response.json()["email"] == "test@example.com", "Email does not match"
