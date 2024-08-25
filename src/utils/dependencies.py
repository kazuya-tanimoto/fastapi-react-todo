from motor import motor_asyncio
from decouple import config

MONGO_API_KEY = config('MONGO_API_KEY')

def get_database() -> motor_asyncio.AsyncIOMotorDatabase:
    client = motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
    return client.API_DB