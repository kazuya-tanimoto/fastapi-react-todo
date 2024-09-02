from fastapi import HTTPException
from motor import motor_asyncio
from utils.auth import AuthJwtCsrf
from utils.common import convert_document
from utils.dependencies import connect_to_api_database


class UserService:
    def __init__(self, db: motor_asyncio.AsyncIOMotorDatabase = connect_to_api_database()) -> None:
        """
        コンストラクタ

        :param db: DBインスタンス
        :rtype: None
        """
        self.collection = db.user
        self.auth = AuthJwtCsrf()

    async def register(self, data: dict) -> dict:
        """
        ユーザー情報を登録する

        :param data: 登録するユーザーの情報が含まれた辞書型データ
        :return: 登録されたユーザーの情報が含まれた辞書型データ
        """
        email = data.get("email")
        password = data.get("password")
        user = await self.collection.find_one({"email": email})

        if user:
            raise HTTPException(status_code=409, detail="User already exists")

        if not password or len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

        self.validate_password(password)

        user = await self.collection.insert_one({"email": email, "password": self.auth.hash_password(password)})
        registered_user = await self.collection.find_one({"_id": user.inserted_id})
        return convert_document(registered_user, ["_id", "email"])

    @staticmethod
    def validate_password(password: str) -> None:
        """
        パスワードが下記の要件を満たしているか検証する
        - 12桁以上
        - 大文字、小文字、数字、記号をそれぞれ1文字以上含む
        - 先頭はアルファベットで始まる
        :param password: パスワード
        :return: なし
        """
        if not password[0].isalpha():
            raise HTTPException(status_code=400, detail="Password must start with an alphabet")
        if len(password) < 12:
            raise HTTPException(status_code=400, detail="Password must be at least 12 characters long")
        if not any(char.isupper() for char in password):
            raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in password):
            raise HTTPException(status_code=400, detail="Password must contain at least one digit")
        if not any(char in "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~" for char in password):
            raise HTTPException(status_code=400, detail="Password must contain at least one symbol")

    async def authenticate(self, data: dict) -> str:
        """
        ログイン認証を行う。認証成功時はJWTトークンを返す。

        :param data: 辞書型データ。"email"と"password"のキーを持つ。
        :return: JWTトークンを文字列として返す。

        """
        email = data.get("email")
        password = data.get("password")
        user = await self.collection.find_one({"email": email})

        if not user or not self.auth.verify_password(password, user["password"]):
            raise HTTPException(status_code=400, detail="Invalid email or password")
        return self.auth.encode_jwt(user["email"])
