from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
def mock_user_service(mocker):
    """
    UserService をモックし、authenticate と register メソッドが期待される値を返すように設定するフィクスチャ。
    """
    mock_service = MagicMock()
    mock_service.authenticate = AsyncMock(return_value="jwt_token")
    mock_service.register = AsyncMock(return_value={"email": "test@example.com"})
    mocker.patch("services.user.UserService", return_value=mock_service)
    return mock_service


@pytest.fixture
async def async_client():
    """
    非同期テスト用のAsyncClientフィクスチャ。
    ASGITransportを使用して明示的にアプリケーションを指定。
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver.local") as ac:
        yield ac
