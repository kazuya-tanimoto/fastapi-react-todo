from pydantic import BaseModel


class Todo(BaseModel):
    """
    todoアイテム
    - id: アイテムのID
    - title: アイテムのタイトル
    - description アイテムの詳細説明
    """
    id: str
    title: str
    description: str


class TodoBody(BaseModel):
    """
    Todoアイテムのタイトルと詳細説明を保持
    - title: アイテムのタイトル
    - description アイテムの詳細説明
    """
    title: str
    description: str
