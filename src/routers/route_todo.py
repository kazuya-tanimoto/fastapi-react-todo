from fastapi import APIRouter
from fastapi import Request, Response, HTTPException
from fastapi.encoders import jsonable_encoder
from schemas.todo import Todo, TodoBody
from todo import register, update, delete
from starlette.status import HTTP_201_CREATED
from todo import get_todos, get_single

router = APIRouter()


@router.post('/api/todo', response_model=Todo)
async def create(request: Request, response: Response, data: TodoBody):
    todo = jsonable_encoder(data)
    res = await register(todo)
    response.status_code = HTTP_201_CREATED
    if res:
        return res
    raise HTTPException(status_code=400, detail='Failed to create todo')


@router.get('/api/todos', response_model=list[Todo])
async def fetch_todos():
    return await get_todos()


@router.get('/api/todos/{id}', response_model=Todo)
async def fetch_single(id: str):
    todo = await get_single(id)
    if todo:
        return todo
    raise HTTPException(status_code=404, detail=f'Todo(id:{id}) not found')

@router.put('/api/todos/{id}', response_model=Todo)
async def update_single(id: str, data: TodoBody):
    todo = jsonable_encoder(data)
    res = await update(id, todo)
    if res:
        return res
    raise HTTPException(status_code=404, detail=f'Update failed for Todo(id:{id})')

@router.delete('/api/todos/{id}', response_model=dict)
async def delete_single(id: str):
    res = await delete(id)
    if res:
        return {'message': 'Todo deleted successfully'}
    raise HTTPException(status_code=404, detail=f'Delete failed for Todo(id:{id})')