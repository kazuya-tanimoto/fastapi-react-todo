from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_201_CREATED
from fastapi_csrf_protect import CsrfProtect
from schemas.todo import Todo, TodoBody
from todo import get_todos, get_single, register, update, delete
from auth_utils import AuthJwtCsrf

router = APIRouter()
auth = AuthJwtCsrf()


@router.post('/api/todo', response_model=Todo)
async def create(request: Request, response: Response, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_update_csrf_jwt(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await register(todo)
    response.status_code = HTTP_201_CREATED
    response.set_cookie(key='access_token', value=f'Bearer {new_token}', httponly=True, samesite='none', secure=True)
    if res:
        return res
    raise HTTPException(status_code=400, detail='Failed to create todo')


@router.get('/api/todos', response_model=list[Todo])
async def fetch_todos(request: Request):
    auth.verify_jwt(request)
    return await get_todos()


@router.get('/api/todos/{id}', response_model=Todo)
async def fetch_single(request: Request, response: Response, id: str):
    new_token = auth.verify_update_jwt(request)
    todo = await get_single(id)
    response.set_cookie(key='access_token', value=f'Bearer {new_token}', httponly=True, samesite='none', secure=True)
    if todo:
        return todo
    raise HTTPException(status_code=404, detail=f'Todo(id:{id}) not found')


@router.put('/api/todos/{id}', response_model=Todo)
async def update_single(request: Request, response: Response, id: str, data: TodoBody,
                        csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_update_csrf_jwt(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await update(id, todo)
    response.set_cookie(key='access_token', value=f'Bearer {new_token}', httponly=True, samesite='none', secure=True)
    if res:
        return res
    raise HTTPException(status_code=404, detail=f'Update failed for Todo(id:{id})')


@router.delete('/api/todos/{id}', response_model=dict)
async def delete_single(request: Request, response: Response, id: str, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_update_csrf_jwt(request, csrf_protect, request.headers)
    res = await delete(id)
    response.set_cookie(key='access_token', value=f'Bearer {new_token}', httponly=True, samesite='none', secure=True)
    if res:
        return {'message': 'Todo deleted successfully'}
    raise HTTPException(status_code=404, detail=f'Delete failed for Todo(id:{id})')
