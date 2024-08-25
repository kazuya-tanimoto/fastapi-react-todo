from fastapi import APIRouter, Request, Response, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_csrf_protect import CsrfProtect
from schemas.user import UserInfo, UserBody
from schemas.security import CsrfToken
from user import register, authenticate
from auth_utils import AuthJwtCsrf
from schemas.common import SuccessMessage

router = APIRouter()
auth = AuthJwtCsrf()


@router.get('/api/csrf-token', response_model=CsrfToken)
def get_csrf_token(csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.generate_csrf()
    return {"csrf_token": csrf_token}


@router.post('/api/register', response_model=UserInfo)
async def signup(request: Request, user: UserBody, csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf(csrf_protect.get_csrf_from_headers(request.headers))
    user = jsonable_encoder(user)
    return await register(user)


@router.post('/api/login', response_model=SuccessMessage)
async def login(request: Request, response: Response, user: UserBody, csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf(csrf_protect.get_csrf_from_headers(request.headers))
    user = jsonable_encoder(user)
    token = await authenticate(user)
    response.set_cookie(
        key='access_token', value=f"Bearer {token}", httponly=True, samesite='none', secure=True)
    return {"message": "Login successful"}


@router.post('/api/logout', response_model=SuccessMessage)
async def logout(request: Request, response: Response, csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf(csrf_protect.get_csrf_from_headers(request.headers))
    response.set_cookie(
        key='access_token', value="", httponly=True, samesite='none', secure=True)
    return {"message": "Logout successful"}


@router.get('/api/user', response_model=UserInfo)
def get_user_refresh_jwt(request: Request, response: Response):
    subject, new_token = auth.verify_update_jwt(request)
    response.set_cookie(
        key='access_token', value=f"Bearer {new_token}", httponly=True, samesite='none', secure=True)
    return {"email": subject}
