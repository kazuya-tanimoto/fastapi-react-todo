import certifi
from decouple import config
from motor import motor_asyncio

MONGO_API_KEY = config("MONGO_API_KEY")
DATABASE_NAME = "API_DB"


def connect_database() -> motor_asyncio.AsyncIOMotorDatabase:
    """
    接続しているMongoDBクライアントからAPI データベースを取得する

    :return: API_DBデータベースのインスタンス
    """
    mongo_client = motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY, tlsCAFile=certifi.where())
    return mongo_client[DATABASE_NAME]
