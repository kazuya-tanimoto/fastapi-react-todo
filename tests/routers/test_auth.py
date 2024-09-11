import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from main import app

client = TestClient(app)


def test_generate_csrf_token() -> None:
    response = client.get("/api/csrf-token")
    assert response.status_code == 200
    assert "csrf_token" in response.json()


def test_signup() -> None:
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    headers = {"X-CSRF-Token": csrf_token}
    user_data = {"username": "testuser", "password": "testpassword"}

    response = client.post("/api/register", json=user_data, headers=headers)
    assert response.status_code == 200
    assert "email" in response.json()


@pytest.mark.anyio
# @pytest.mark.asyncio
async def test_login() -> None:
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    headers = {"X-CSRF-Token": csrf_token}
    user_data = {"email": "test@example.com", "password": "password"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as ac:
        response = await  ac.post("/api/login", json=user_data, headers=headers)

    # response = await login()
    print("\nresponse.json()-------------\n")
    print(response.json())
    assert response.status_code == 200
    # assert response.status_code == 422
    assert response.json()["message"] == "Login successful"


def test_logout() -> None:
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    headers = {"X-CSRF-Token": csrf_token}

    response = client.post("/api/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"


def test_get_user_refresh_jwt() -> None:
    # 事前に認証が必要なので、ログインから始める
    # csrf_response = client.get("/api/csrf-token")
    # csrf_token = csrf_response.json()["csrf_token"]
    #
    # headers = {"X-CSRF-Token": csrf_token}
    # user_data = {"username": "testuser", "password": "testpassword"}
    #
    # login_response = client.post("/api/login", json=user_data, headers=headers)
    login_response = login()
    assert login_response.status_code == 200

    cookies = login_response.cookies

    response = client.get("/api/user", cookies=cookies)
    assert response.status_code == 200
    assert "email" in response.json()


async def login():
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    headers = {"X-CSRF-Token": csrf_token}
    user_data = {"email": "test@example.com", "password": "password"}

    response = client.post("http://localhost:8000/api/login", json=user_data, headers=headers)
    # response = await client.post("/api/login", json=user_data, headers=headers)
    return response
