from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from fastapi import HTTPException
from pytest import MonkeyPatch
from services.user import UserService


@pytest.fixture
def mock_db() -> MagicMock:
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_db.user = mock_collection
    return mock_db


@pytest.mark.asyncio
async def test_register(mock_db: MagicMock) -> None:
    service = UserService(mock_db)

    # 1回目のfind_oneはNone、2回目はユーザー情報を返す
    mock_db.user.find_one.side_effect = [None, {"_id": ObjectId(), "email": "test@example.com",
                                                "password": "hashed_password"}]
    mock_db.user.insert_one.return_value.inserted_id = ObjectId()

    data = {"email": "test@example.com", "password": "ValidPassword123!"}
    result = await service.register(data)

    assert result["email"] == data["email"]


@pytest.mark.asyncio
async def test_register_existing_user(mock_db: MagicMock) -> None:
    service = UserService(mock_db)

    mock_db.user.find_one.return_value = {"_id": ObjectId(), "email": "test@example.com", "password": "hashed_password"}

    data = {"email": "test@example.com", "password": "ValidPassword123!"}

    with pytest.raises(HTTPException) as exc_info:
        await service.register(data)
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "User already exists"


@pytest.mark.asyncio
async def test_register_short_password(mock_db: MagicMock) -> None:
    service = UserService(mock_db)

    mock_db.user.find_one.return_value = None

    data = {"email": "test@example.com", "password": "short"}

    with pytest.raises(HTTPException) as exc_info:
        await service.register(data)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must be at least 8 characters long"


@pytest.mark.asyncio
async def test_authenticate(mock_db: MagicMock, monkeypatch: MonkeyPatch) -> None:
    service = UserService(mock_db)

    mock_db.user.find_one.return_value = {"_id": ObjectId(), "email": "test@example.com", "password": "hashed_password"}
    monkeypatch.setattr("utils.auth.AuthJwtCsrf.verify_password", lambda x, y, z: True)
    monkeypatch.setattr("utils.auth.AuthJwtCsrf.encode_jwt", lambda x, y: "jwt_token")

    data = {"email": "test@example.com", "password": "ValidPassword123!"}
    result = await service.authenticate(data)

    assert result == "jwt_token"


@pytest.mark.asyncio
async def test_authenticate_invalid_credentials(mock_db: MagicMock) -> None:
    service = UserService(mock_db)

    mock_db.user.find_one.return_value = None

    data = {"email": "test@example.com", "password": "InvalidPassword"}

    with pytest.raises(HTTPException) as exc_info:
        await service.authenticate(data)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid email or password"


def test_validate_password_valid() -> None:
    # 有効なパスワード
    valid_password = "ValidPassword123!"
    try:
        UserService.validate_password(valid_password)
    except HTTPException:
        pytest.fail("HTTPException raised with a valid password")


def test_validate_password_too_short() -> None:
    # 短すぎるパスワード
    short_password = "Short1!"
    with pytest.raises(HTTPException) as exc_info:
        UserService.validate_password(short_password)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must be at least 12 characters long"


def test_validate_password_no_uppercase() -> None:
    # 大文字が含まれていないパスワード
    no_uppercase_password = "validpassword123!"
    with pytest.raises(HTTPException) as exc_info:
        UserService.validate_password(no_uppercase_password)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must contain at least one uppercase letter"


def test_validate_password_no_lowercase() -> None:
    # 小文字が含まれていないパスワード
    no_lowercase_password = "VALIDPASSWORD123!"
    with pytest.raises(HTTPException) as exc_info:
        UserService.validate_password(no_lowercase_password)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must contain at least one lowercase letter"


def test_validate_password_no_digit() -> None:
    # 数字が含まれていないパスワード
    no_digit_password = "ValidPassword!"
    with pytest.raises(HTTPException) as exc_info:
        UserService.validate_password(no_digit_password)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must contain at least one digit"


def test_validate_password_no_symbol() -> None:
    # 記号が含まれていないパスワード
    no_symbol_password = "ValidPassword123"
    with pytest.raises(HTTPException) as exc_info:
        UserService.validate_password(no_symbol_password)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must contain at least one symbol"


def test_validate_password_no_alphabet_start() -> None:
    # アルファベットで始まらないパスワード
    no_alphabet_start_password = "1ValidPassword!"
    with pytest.raises(HTTPException) as exc_info:
        UserService.validate_password(no_alphabet_start_password)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must start with an alphabet"
