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


@router.get("/api/csrf-token", response_model=CsrfToken)
def generate_csrf_token(response: Response, csrf_protect: CsrfProtect = Depends()) -> dict[str, str]:
    """
    CSRFトークンを生成する
    :param response:
    :param csrf_protect: CsrfProtectインスタンス
    :return: CSRFトークン
    """
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(signed_token, response)

    return {"csrf_token": csrf_token}


@router.post("/api/register", response_model=UserInfo)
async def signup(request: Request, user: UserBody, csrf_protect: CsrfProtect = Depends()) -> dict:
    """
    ユーザー登録する
    :param request: リクエスト
    :param user: ユーザー情報
    :param csrf_protect: CsrfProtectインスタンス
    :return: 登録した情報
    """
    try:
        await csrf_protect.validate_csrf(request)
        user = jsonable_encoder(user)
        return await service.register(user)
    except Exception as e:
        print(e)
        return {"message": str(e)}


@router.post("/api/login", response_model=SuccessMessage)
async def login(request: Request, response: Response, user: UserBody, csrf_protect: CsrfProtect = Depends()) -> dict:
    """
    ログイン認証を行う
    :param request: リクエスト
    :param response: レスポンス
    :param user: ユーザー情報
    :param csrf_protect: CsrfProtectインスタンス
    :return: ログイン成功メッセージ
    """
    try:
        # csrf_protect.validate_csrf(csrf_protect.get_csrf_from_headers(request.headers))
        await csrf_protect.validate_csrf(request)
        user = jsonable_encoder(user)
        token = await service.authenticate(user)
        auth.set_jwt_cookie(response, token)
        return {"message": "Login successful"}
    except Exception as e:
        print(e)
        return {"message": str(e)}


@router.post("/api/logout", response_model=SuccessMessage)
async def logout(request: Request, response: Response, csrf_protect: CsrfProtect = Depends()) -> dict:
    """
    ログアウトする
    :param request: リクエスト
    :param response: レスポンス
    :param csrf_protect: CsrfProtectインスタンス
    :return: ログアウト成功メッセージ
    """
    # csrf_protect.validate_csrf(csrf_protect.get_csrf_from_headers(request.headers))
    await csrf_protect.validate_csrf(request)
    auth.clear_jwt_cookie(response)
    return {"message": "Logout successful"}


@router.get("/api/user", response_model=UserInfo)
def get_user_refresh_jwt(request: Request, response: Response) -> dict:
    """
    ユーザー情報を取得する
    :param request: リクエスト
    :param response: レスポンス
    :return: メールアドレス
    """
    print(request.cookies)
    subject, new_token = auth.update_jwt(request)
    auth.set_jwt_cookie(response, new_token)
    return {"email": subject}
