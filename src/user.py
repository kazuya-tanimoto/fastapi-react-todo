from pprint import pprint

from fastapi import HTTPException
from bson import ObjectId
from decouple import config
from typing import Union
from motor import  motor_asyncio
from auth_utils import AuthJwtCsrf

MONGO_API_KEY = config('MONGO_API_KEY')

client = motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
database = client.API_DB
collection = database.user
auth = AuthJwtCsrf()

def serializer(user) -> dict:
    return {
        'id': str(user['_id']),
        'email': user['email'],
    }

async def register(data:dict) -> dict:
    email = data.get('email')
    password = data.get('password')
    user = await collection.find_one({'email': email})
    if user:
        raise HTTPException(status_code=409, detail='User already exists')
    if not password or len(password) < 8:
        raise HTTPException(status_code=400, detail='Password must be at least 8 characters long')
    user = await collection.insert_one({"email":email, "password": auth.hash_password(password)})
    return serializer(await collection.find_one({'_id': user.inserted_id}))

async def authenticate(data:dict) -> str:
    email = data.get('email')
    password = data.get('password')
    user = await collection.find_one({'email': email})
    if not user or not auth.verify_password(password, user['password']):
        raise HTTPException(status_code=400, detail='Invalid email or password')
    return auth.encode_jwt(user['email'])