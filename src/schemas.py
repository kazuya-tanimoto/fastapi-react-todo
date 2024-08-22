from pydantic import BaseModel

class Todo(BaseModel):
    id: str
    title: str
    description: str

class TodoBody(BaseModel):
    title: str
    description: str

class SuccessMessage(BaseModel):
    message: str