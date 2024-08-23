import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
from decouple import config

JWT_SECRET_KEY = config('JWT_SECRET_KEY')


class AuthJwtCsrf:
    ctx = CryptContext(schemes=['bcrypt'], deperecate='auto')

    def pash_password(self, password) -> str:
        return self.ctx.hash(password)

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.ctx.verify(plain_password, hashed_password)

    @staticmethod
    def encode_jwt(email) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'sub': email
        }

        return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

    @staticmethod
    def decode_jwt(token) -> str:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')
