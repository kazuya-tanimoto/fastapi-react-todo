from fastapi import APIRouter, Depends, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi_csrf_protect import CsrfProtect

from schemas.auth import CsrfToken
from schemas.common import SuccessMessage
from schemas.user import UserBody, UserInfo
from services.user import UserService
from utils.auth import AuthJwtCsrf

router: APIRouter = APIRouter()
auth = AuthJwtCsrf()
service = UserService()


@router.get('/api/csrf-token', response_model=CsrfToken)
def get_csrf_token(csrf_protect: CsrfProtect = Depends()) -> dict[str, str]:
    csrf_token = csrf_protect.generate_csrf()
    return {"csrf_token": csrf_token}


@router.post('/api/register', response_model=UserInfo)
async def signup(request: Request, user: UserBody, csrf_protect: CsrfProtect = Depends()) -> dict:
    csrf_protect.validate_csrf(csrf_protect.get_csrf_from_headers(request.headers))
    user = jsonable_encoder(user)
    return await service.register(user)


@router.post('/api/login', response_model=SuccessMessage)
async def login(request: Request, response: Response, user: UserBody, csrf_protect: CsrfProtect = Depends()) -> dict:
    csrf_protect.validate_csrf(csrf_protect.get_csrf_from_headers(request.headers))
    user = jsonable_encoder(user)
    token = await service.authenticate(user)
    auth.set_jwt_cookie(response, token)
    return {"message": "Login successful"}


@router.post('/api/logout', response_model=SuccessMessage)
async def logout(request: Request, response: Response, csrf_protect: CsrfProtect = Depends()) -> dict:
    csrf_protect.validate_csrf(csrf_protect.get_csrf_from_headers(request.headers))
    auth.clear_jwt_cookie(response)
    return {"message": "Logout successful"}


@router.get('/api/user', response_model=UserInfo)
def get_user_refresh_jwt(request: Request, response: Response) -> dict:
    subject, new_token = auth.verify_update_jwt(request)
    auth.set_jwt_cookie(response, new_token)
    return {"email": subject}
