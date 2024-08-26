from typing import Optional

from pydantic import BaseModel


class UserBody(BaseModel):
    email: str
    password: str


class UserInfo(BaseModel):
    id: Optional[str] = None
    email: str
