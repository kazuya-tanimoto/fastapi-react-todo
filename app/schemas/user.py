from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class UserInfo(BaseModel):
    """
    ユーザー情報
    - id: ユーザーのID
    - email: ユーザーのメールアドレス
    """
    # X | Y annotation cause Uvicorn to crash
    # id: str | None = None
    id: Optional[str] = None
    email: str


class UserBody(BaseModel):
    """
    ユーザー情報の入力データ
    - email: ユーザーのメールアドレス
    - password: ユーザーのパスワード
    """
    email: str
    password: str
