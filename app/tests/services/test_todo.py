from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from services.todo import TodoService


@pytest.fixture
def mock_db() -> MagicMock:
    # MagicMock クラスを使ってモックDBオブジェクトを作成
    mock_db = MagicMock()
    # AsyncMock クラスを使ってモックコレクションオブジェクトを作成
    mock_collection = AsyncMock()
    # コレクションをモックDBに割り当てて返す
    mock_db.todo = mock_collection
    return mock_db


@pytest.mark.asyncio
async def test_register(mock_db: MagicMock) -> None:
    service = TodoService(mock_db)

    mock_db.todo.insert_one.return_value.inserted_id = ObjectId()
    mock_db.todo.find_one.return_value = {
        "_id": ObjectId(), "title": "Test", "description": "Test description"
    }

    data = {"title": "Test", "description": "Test description"}
    result = await service.register(data)

    assert result["title"] == data["title"]
    assert result["description"] == data["description"]


@pytest.mark.asyncio
async def test_get_todos(mock_db: MagicMock) -> None:
    mock_collection = MagicMock()  # MagicMockに変更

    # find() メソッドの戻り値を正しく設定
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [
        {"_id": ObjectId(), "title": "Test 1", "description": "Test description 1"},
        {"_id": ObjectId(), "title": "Test 2", "description": "Test description 2"}
    ]
    mock_collection.find.return_value = mock_cursor

    mock_db.todo = mock_collection

    service = TodoService(mock_db)

    result = await service.get_todos()

    assert len(result) == 2
    assert result[0]["title"] == "Test 1"
    assert result[1]["title"] == "Test 2"


@pytest.mark.asyncio
async def test_get_single(mock_db: MagicMock) -> None:
    service = TodoService(mock_db)

    _id = ObjectId()
    mock_db.todo.find_one.return_value = {
        "_id": _id, "title": "Test", "description": "Test description"
    }

    result = await service.get_single(str(_id))

    assert result["title"] == "Test"
    assert result["description"] == "Test description"


@pytest.mark.asyncio
async def test_update(mock_db: MagicMock) -> None:
    service = TodoService(mock_db)

    _id = ObjectId()
    mock_db.todo.find_one.return_value = {
        "_id": _id, "title": "Test", "description": "Test description"
    }
    mock_db.todo.update_one.return_value.modified_count = 1
    mock_db.todo.find_one.return_value = {
        "_id": _id, "title": "Updated Test", "description": "Updated description"
    }

    result = await service.update(str(_id), {"title": "Updated Test", "description": "Updated description"})

    assert result["title"] == "Updated Test"
    assert result["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete(mock_db: MagicMock) -> None:
    service = TodoService(mock_db)

    _id = ObjectId()
    mock_db.todo.find_one.return_value = {
        "_id": _id, "title": "Test", "description": "Test description"
    }
    mock_db.todo.delete_one.return_value.deleted_count = 1

    result = await service.delete(str(_id))

    assert result is True
