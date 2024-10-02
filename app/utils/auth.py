from datetime import datetime, timedelta, timezone

import jwt
from decouple import config
from fastapi import HTTPException, Request, Response
from fastapi_csrf_protect import CsrfProtect
from passlib.context import CryptContext
from starlette.datastructures import Headers

JWT_SECRET_KEY = config("JWT_SECRET_KEY")


class AuthJwtCsrf:
    TOKEN_MISSING_ERROR = "Token is missing"
    SIGNATURE_EXPIRED_ERROR = "Signature has expired"
    INVALID_TOKEN_ERROR = "Invalid token"

    def __init__(self) -> None:
        self.ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.ctx.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.ctx.verify(plain_password, hashed_password)

    @staticmethod
    def encode_jwt(email: str) -> str:
        """
        メールアドレスからJWTを生成する

        :param email: エンコードするメールアドレス
        :return: エンコードされたJWT
        """
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=0, minutes=5),
            "iat": datetime.now(tz=timezone.utc),
            "sub": email
        }

        return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def decode_jwt(token: str) -> str:
        """
        JWTトークンをデコードしてメールアドレスを取得する

        :param token: デコードするJWTトークン
        :return: メールアドレス
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail=AuthJwtCsrf.SIGNATURE_EXPIRED_ERROR) from None
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail=AuthJwtCsrf.INVALID_TOKEN_ERROR) from None

    def verify_jwt(self, request: Request) -> str:
        """
        JWTを検証する

        :param request: 検証するリクエスト
        :return: メールアドレス
        """
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail=AuthJwtCsrf.TOKEN_MISSING_ERROR)
        _, _, value = token.partition(" ")
        email = self.decode_jwt(value)
        return email

    def update_jwt(self, request: Request) -> tuple[str, str]:
        """
        JWTトークンを更新する

        :param request: リクエスト
        :return: 更新されたJWTトークン
        """
        email = self.verify_jwt(request)
        new_token = self.encode_jwt(email)
        return email, new_token

    def update_jwt_with_csrf(self, request: Request, csrf_protect: CsrfProtect, headers: Headers) -> str:
        """
        CSRFの検証を行った上でJWTトークンを更新する

        :param request: リクエスト
        :param csrf_protect: CsrfProtectインスタンス
        :param headers: リクエストヘッダー
        :return: 更新されたJWTトークン
        """
        csrf_protect.validate_csrf(request)
        email = self.verify_jwt(request)
        new_token = self.encode_jwt(email)
        return new_token

    @staticmethod
    def set_jwt_cookie(response: Response, token: str) -> None:
        """
        CookieにJWTトークンを設定する

        :param response: クッキーを設定するレスポンス
        :param token: JWTトークン
        """
        response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, samesite="none", secure=True)

    @staticmethod
    def clear_jwt_cookie(response: Response) -> None:
        """
        CookieのJWTトークンをクリアする

        :param response: クッキーを設定するレスポンス
        """
        response.set_cookie(key="access_token", value="", httponly=True, samesite="none", secure=True)
