from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_201_CREATED
from fastapi_csrf_protect import CsrfProtect
from schemas.todo import Todo, TodoBody
from services.todo import TodoService
from utils.auth import AuthJwtCsrf

router = APIRouter()
auth = AuthJwtCsrf()
service = TodoService()


@router.post('/api/todo', response_model=Todo)
async def create(request: Request, response: Response, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_update_csrf_jwt(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await service.register(todo)
    response.status_code = HTTP_201_CREATED
    auth.set_jwt_cookie(response, new_token)
    if res:
        return res
    raise HTTPException(status_code=400, detail='Failed to create todo')


@router.get('/api/todos', response_model=list[Todo])
async def fetch_todos(request: Request):
    auth.verify_jwt(request)
    return await service.get_todos()


@router.get('/api/todos/{id}', response_model=Todo)
async def fetch_single(request: Request, response: Response, id: str):
    _, new_token = auth.verify_update_jwt(request)
    todo = await service.get_single(id)
    auth.set_jwt_cookie(response, new_token)
    if todo:
        return todo
    raise HTTPException(status_code=404, detail=f'Todo(id:{id}) not found')


@router.put('/api/todos/{id}', response_model=Todo)
async def update_single(request: Request, response: Response, id: str, data: TodoBody,
                        csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_update_csrf_jwt(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await service.update(id, todo)
    auth.set_jwt_cookie(response, new_token)
    if res:
        return res
    raise HTTPException(status_code=404, detail=f'Update failed for Todo(id:{id})')


@router.delete('/api/todos/{id}', response_model=dict)
async def delete_single(request: Request, response: Response, id: str, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_update_csrf_jwt(request, csrf_protect, request.headers)
    res = await service.delete(id)
    auth.set_jwt_cookie(response, new_token)
    if res:
        return {'message': 'Todo deleted successfully'}
    raise HTTPException(status_code=404, detail=f'Delete failed for Todo(id:{id})')
