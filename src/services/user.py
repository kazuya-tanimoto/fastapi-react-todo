from fastapi import HTTPException
from utils.auth import AuthJwtCsrf
from utils.common import serialize
from utils.dependencies import get_database

class UserService:
    def __init__(self, db=get_database()):
        self.collection = db.user
        self.auth = AuthJwtCsrf()

    async def register(self, data: dict) -> dict:
        email = data.get('email')
        password = data.get('password')
        user = await self.collection.find_one({'email': email})

        if user:
            raise HTTPException(status_code=409, detail='User already exists')

        if not password or len(password) < 8:
            raise HTTPException(status_code=400, detail='Password must be at least 8 characters long')

        user = await self.collection.insert_one({"email": email, "password": self.auth.hash_password(password)})
        registered_user = await self.collection.find_one({'_id': user.inserted_id})
        return serialize(registered_user, ['_id', 'email'])

    async def authenticate(self, data: dict) -> str:
        email = data.get('email')
        password = data.get('password')
        user = await self.collection.find_one({'email': email})

        if not user or not self.auth.verify_password(password, user['password']):
            raise HTTPException(status_code=400, detail='Invalid email or password')
        return self.auth.encode_jwt(user['email'])
