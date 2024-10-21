from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi_csrf_protect import CsrfProtect
from schemas.todo import Todo, TodoBody
from services.todo import TodoService
from starlette.status import HTTP_201_CREATED
from utils.auth import AuthJwtCsrf

router = APIRouter()
auth = AuthJwtCsrf()
service = TodoService()


@router.post("/api/todo", response_model=Todo)
async def create(request: Request, response: Response, data: TodoBody, csrf_protect: CsrfProtect = Depends()) -> dict:
    """
    todoを作成する
    :param request: リクエスト
    :param response: レスポンス
    :param data: todoの情報
    :param csrf_protect: CsrfProtectインスタンス
    :return: 作成したtodo
    """
    new_token = auth.update_jwt_with_csrf(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await service.register(todo)
    response.status_code = HTTP_201_CREATED
    auth.set_jwt_cookie(response, new_token)
    if res:
        return res
    raise HTTPException(status_code=400, detail="Failed to create todo")


@router.get("/api/todos", response_model=list[Todo])
async def fetch_todos(request: Request) -> list[dict]:
    """
    全てのtodoを取得する
    :param request: リクエスト
    :return: todoのリスト
    """
    # auth.verify_jwt(request)
    return await service.get_todos()


@router.get("/api/todos/{_id}", response_model=Todo)
async def fetch_single(request: Request, response: Response, _id: str) -> dict:
    """
    単一のtodoを取得する
    :param request: リクエスト
    :param response: レスポンス
    :param _id: todoのID
    :return: 取得したtodo
    """
    _, new_token = auth.update_jwt(request)
    todo = await service.get_single(_id)
    auth.set_jwt_cookie(response, new_token)
    if todo:
        return todo
    raise HTTPException(status_code=404, detail=f"Todo(id:{_id}) not found")


@router.put("/api/todos/{_id}", response_model=Todo)
async def update_single(request: Request, response: Response, _id: str, data: TodoBody,
                        csrf_protect: CsrfProtect = Depends()) -> dict:
    """
    todoを更新する
    :param request: リクエスト
    :param response: レスポンス
    :param _id: todoのID
    :param data: 更新データ
    :param csrf_protect: CsrfProtectインスタンス
    :return: 更新したtodo
    """
    new_token = auth.update_jwt_with_csrf(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await service.update(_id, todo)
    auth.set_jwt_cookie(response, new_token)
    if res:
        return res
    raise HTTPException(status_code=404, detail=f"Update failed for Todo(id:{_id})")


@router.delete("/api/todos/{_id}", response_model=dict)
async def delete_single(request: Request, response: Response, _id: str, csrf_protect: CsrfProtect = Depends()) -> dict:
    """
    todoを削除する
    :param request: リクエスト
    :param response: レスポンス
    :param _id: todoのID
    :param csrf_protect: CsrfProtectインスタンス
    :return: 削除の成否
    """
    new_token = auth.update_jwt_with_csrf(request, csrf_protect, request.headers)
    res = await service.delete(_id)
    auth.set_jwt_cookie(response, new_token)
    if res:
        return {"message": "Todo deleted successfully"}
    raise HTTPException(status_code=404, detail=f"Delete failed for Todo(id:{_id})")
