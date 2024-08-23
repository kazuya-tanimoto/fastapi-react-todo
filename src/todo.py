from bson import ObjectId
from decouple import config
from typing import Union
from motor import  motor_asyncio

MONGO_API_KEY = config('MONGO_API_KEY')

client = motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
database = client.API_DB
collection = database.todo

def serializer(todo) -> dict:
    return {
        'id': str(todo['_id']),
        'title': todo['title'],
        'description': todo['description'],
    }

async def register(data:dict) -> Union[dict, bool]:
    todo = await collection.insert_one(data)
    new_todo = await collection.find_one({'_id': todo.inserted_id})
    if new_todo:
        return serializer(new_todo)
    return False

async def get_todos() -> list:
    todos = []
    for todo in await collection.find().to_list(length=100):
        todos.append(serializer(todo))
    return todos

async def get_single(id:str) -> Union[dict, bool]:
    todo = await collection.find_one({'_id': ObjectId(id)})
    if todo:
        return serializer(todo)
    return False

async def update(id:str, data:dict) -> Union[dict, bool]:
    todo = await collection.find_one({'_id': ObjectId(id)})
    if todo:
        updated_todo = await collection.update_one({'_id': ObjectId(id)}, {'$set': data})
        if updated_todo.modified_count > 0:
            new_todo = await collection.find_one({'_id': ObjectId(id)})
            return serializer(new_todo)
    return False

async def delete(id:str) -> bool:
    todo = await collection.find_one({'_id': ObjectId(id)})
    if todo:
        deleted_todo = await collection.delete_one({'_id': ObjectId(id)})
        if deleted_todo.deleted_count > 0:
            return True
        return False