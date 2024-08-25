import jwt
from fastapi import HTTPException, Request
from passlib.context import CryptContext
from datetime import datetime, timedelta
from decouple import config
from fastapi_csrf_protect import CsrfProtect
from starlette.datastructures import Headers

JWT_SECRET_KEY = config('JWT_SECRET_KEY')


class AuthJwtCsrf:
    TOKEN_MISSING_ERROR = 'Token is missing'
    SIGNATURE_EXPIRED_ERROR = 'Signature has expired'
    INVALID_TOKEN_ERROR = 'Invalid token'

    def __init__(self):
        self.ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def hash_password(self, password: str) -> str:
        return self.ctx.hash(password)

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.ctx.verify(plain_password, hashed_password)

    @staticmethod
    def encode_jwt(email: str) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'sub': email
        }

        return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

    @staticmethod
    def decode_jwt(token: str) -> str:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail=AuthJwtCsrf.SIGNATURE_EXPIRED_ERROR)
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail=AuthJwtCsrf.INVALID_TOKEN_ERROR)

    def verify_jwt(self, request: Request) -> str:
        token = request.cookies.get('access_token')
        if not token:
            raise HTTPException(status_code=401, detail=AuthJwtCsrf.TOKEN_MISSING_ERROR)
        _, _, value = token.partition(' ')
        subject = self.decode_jwt(value)
        return subject

    def verify_update_jwt(self, request: Request) -> tuple[str, str]:
        subject = self.verify_jwt(request)
        new_token = self.encode_jwt(subject)
        return subject, new_token

    def verify_update_csrf_jwt(self, request: Request, csrf_protect: CsrfProtect, headers: Headers) -> str:
        csrf_token = csrf_protect.get_csrf_from_headers(headers)
        csrf_protect.validate_csrf(csrf_token)
        subject = self.verify_jwt(request)
        new_token = self.encode_jwt(subject)
        return new_token
