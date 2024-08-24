from fastapi import APIRouter, Response
from fastapi.encoders import jsonable_encoder
from schemas.user import UserInfo, UserBody
from user import register, authenticate
from auth_utils import AuthJwtCsrf
from schemas.common import SuccessMessage

router = APIRouter()
auth = AuthJwtCsrf()


@router.post('/api/register', response_model=UserInfo)
async def signup(user: UserBody):
    user = jsonable_encoder(user)
    return await register(user)


@router.post('/api/login', response_model=SuccessMessage)
async def login(response: Response, user: UserBody):
    user = jsonable_encoder(user)
    token = await authenticate(user)
    response.set_cookie(
        key='access_token', value=f"Bearer {token}", httponly=True, samesite='none', secure=True)
    return {"message": "Login successful"}
