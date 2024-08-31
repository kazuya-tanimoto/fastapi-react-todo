from __future__ import annotations

from bson import ObjectId
from motor import motor_asyncio

from utils.common import convert_document
from utils.dependencies import connect_to_api_database


class TodoService:
    def __init__(self, db: motor_asyncio.AsyncIOMotorDatabase = connect_to_api_database()) -> None:
        """
        コンストラクタ

        :param db: DBインスタンス
        :return: なし
        """
        self.collection = db.todo

    async def register(self, data: dict) -> dict | bool:
        """
        todoを登録する

        :param data: 登録するデータ
        :return: 登録されたデータオブジェクト
        """
        todo = await self.collection.insert_one(data)
        new_todo = await self.collection.find_one({"_id": todo.inserted_id})
        if new_todo:
            return convert_document(new_todo, ["_id", "title", "description"])
        return False

    async def get_todos(self) -> list:
        """
        todoのリストを取得する

        :return: todoのリスト
        """
        todo_list = await self.collection.find().to_list(length=100)
        return [convert_document(todo, ["_id", "title", "description"]) for todo in todo_list]

    async def get_single(self, _id: str) -> dict | bool:
        """
        単一のtodoを取得する

        :param _id: ドキュメントのID
        :return: todo
        """
        todo = await self.collection.find_one({"_id": ObjectId(_id)})
        if todo:
            return convert_document(todo, ["_id", "title", "description"])
        return False

    async def update(self, _id: str, data: dict) -> dict | bool:
        """
        todoを更新する

        :param _id: ドキュメントのID
        :param data: 更新データ
        :return: 更新後データ
        """
        todo = await self.collection.find_one({"_id": ObjectId(_id)})
        if todo:
            updated_todo = await self.collection.update_one({"_id": ObjectId(_id)}, {"$set": data})
            if updated_todo.modified_count > 0:
                new_todo = await self.collection.find_one({"_id": ObjectId(_id)})
                return convert_document(new_todo, ["_id", "title", "description"])
        return False

    async def delete(self, _id: str) -> bool:
        """
        todoを削除する
        :param _id: ドキュメントのID
        :return: 削除の成否
        """
        todo = await self.collection.find_one({"_id": ObjectId(_id)})
        if todo:
            deleted_todo = await self.collection.delete_one({"_id": ObjectId(_id)})
            if deleted_todo.deleted_count > 0:
                return True
            return False
