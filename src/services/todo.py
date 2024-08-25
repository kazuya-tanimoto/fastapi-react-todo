from bson import ObjectId
from typing import Union
from utils.dependencies import get_database
from utils.common import serialize


class TodoService:
    def __init__(self, db=get_database()) -> None:
        self.collection = db.todo

    async def register(self, data: dict) -> Union[dict, bool]:
        todo = await self.collection.insert_one(data)
        new_todo = await self.collection.find_one({'_id': todo.inserted_id})
        if new_todo:
            return serialize(new_todo, ['_id', 'title', 'description'])
        return False

    async def get_todos(self) -> list:
        todos = []
        for todo in await self.collection.find().to_list(length=100):
            todos.append(serialize(todo, ['_id', 'title', 'description']))
        return todos

    async def get_single(self, id: str) -> Union[dict, bool]:
        todo = await self.collection.find_one({'_id': ObjectId(id)})
        if todo:
            return serialize(todo, ['_id', 'title', 'description'])
        return False

    async def update(self, id: str, data: dict) -> Union[dict, bool]:
        todo = await self.collection.find_one({'_id': ObjectId(id)})
        if todo:
            updated_todo = await self.collection.update_one({'_id': ObjectId(id)}, {'$set': data})
            if updated_todo.modified_count > 0:
                new_todo = await self.collection.find_one({'_id': ObjectId(id)})
                return serialize(new_todo, ['_id', 'title', 'description'])
        return False

    async def delete(self, id: str) -> bool:
        todo = await self.collection.find_one({'_id': ObjectId(id)})
        if todo:
            deleted_todo = await self.collection.delete_one({'_id': ObjectId(id)})
            if deleted_todo.deleted_count > 0:
                return True
            return False
