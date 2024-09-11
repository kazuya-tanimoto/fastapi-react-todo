from datetime import datetime, timedelta, timezone

import jwt
from decouple import config
from fastapi import HTTPException
from pytest_mock import MockFixture
from utils.auth import AuthJwtCsrf

JWT_SECRET_KEY = config("JWT_SECRET_KEY")


def test_hash_password_with_valid_password() -> None:
    auth = AuthJwtCsrf()
    hashed: str = auth.hash_password("securepassword")
    assert auth.verify_password("securepassword", hashed)


def test_hash_password_with_invalid_password() -> None:
    auth = AuthJwtCsrf()
    hashed: str = auth.hash_password("securepassword")
    assert not auth.verify_password("wrongpassword", hashed)


def test_encode_jwt_with_valid_email() -> None:
    token: str = AuthJwtCsrf.encode_jwt("test@example.com")
    assert isinstance(token, str)


def test_decode_jwt_with_valid_token() -> None:
    token: str = AuthJwtCsrf.encode_jwt("test@example.com")
    email: str = AuthJwtCsrf.decode_jwt(token)
    assert email == "test@example.com"


def test_decode_jwt_with_expired_token() -> None:
    expired_token: str = jwt.encode(
        {
            "exp": datetime.now(tz=timezone.utc) - timedelta(minutes=1),
            "iat": datetime.now(tz=timezone.utc),
            "sub": "test@example.com"
        },
        JWT_SECRET_KEY,
        algorithm="HS256"
    )
    try:
        AuthJwtCsrf.decode_jwt(expired_token)
    except HTTPException as e:
        assert e.detail == AuthJwtCsrf.SIGNATURE_EXPIRED_ERROR


def test_decode_jwt_with_invalid_token() -> None:
    invalid_token: str = "invalid.token.value"
    try:
        AuthJwtCsrf.decode_jwt(invalid_token)
    except HTTPException as e:
        assert e.detail == AuthJwtCsrf.INVALID_TOKEN_ERROR


def test_verify_jwt_with_valid_token(mocker: MockFixture) -> None:
    request = mocker.Mock()
    request.cookies.get.return_value = "Bearer valid.token.value"
    mocker.patch("utils.auth.AuthJwtCsrf.decode_jwt", return_value="test@example.com")
    auth = AuthJwtCsrf()
    email: str = auth.verify_jwt(request)
    assert email == "test@example.com"


def test_verify_jwt_with_missing_token(mocker: MockFixture) -> None:
    request = mocker.Mock()
    request.cookies.get.return_value = None
    auth = AuthJwtCsrf()
    try:
        auth.verify_jwt(request)
    except HTTPException as e:
        assert e.detail == AuthJwtCsrf.TOKEN_MISSING_ERROR


def test_update_jwt_with_valid_token(mocker: MockFixture) -> None:
    request = mocker.Mock()
    request.cookies.get.return_value = "Bearer valid.token.value"
    mocker.patch("utils.auth.AuthJwtCsrf.decode_jwt", return_value="test@example.com")
    auth = AuthJwtCsrf()
    email, new_token = auth.update_jwt(request)
    assert email == "test@example.com"
    assert isinstance(new_token, str)


def test_set_jwt_cookie_with_valid_token(mocker: MockFixture) -> None:
    response = mocker.Mock()
    token: str = "valid.token.value"
    AuthJwtCsrf.set_jwt_cookie(response, token)
    response.set_cookie.assert_called_with(key="access_token", value=f"Bearer {token}", httponly=True, samesite="none",
                                           secure=True)


def test_clear_jwt_cookie(mocker: MockFixture) -> None:
    response = mocker.Mock()
    AuthJwtCsrf.clear_jwt_cookie(response)
    response.set_cookie.assert_called_with(key="access_token", value="", httponly=True, samesite="none", secure=True)
