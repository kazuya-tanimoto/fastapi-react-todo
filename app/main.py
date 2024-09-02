from decouple import config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel
from routers import auth, todo
from schemas.common import SuccessMessage
from starlette.middleware.cors import CORSMiddleware

# 設定の定数を定義
LOCALHOST_ORIGIN = "http://localhost:3000"


class CsrfSettings(BaseModel):
    secret_key: str = config("CSRF_SECRET_KEY")
    cookie_samesite: str = "none"


def create_app() -> FastAPI:
    """
    アプリケーションの作成と設定を行う

    :return: FastAPI
    """
    fastapi = FastAPI()
    fastapi.include_router(todo.router)
    fastapi.include_router(auth.router)
    add_cors_middleware(fastapi, [LOCALHOST_ORIGIN])
    configure_csrf(fastapi)
    return fastapi


def add_cors_middleware(fastapi: FastAPI, origins: list[str]) -> None:
    """
    CORSミドルウェアを追加する

    :param fastapi: FastAPIインスタンス
    :param origins: 許可するオリジンのリスト
    :return: なし
    """
    fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )


def configure_csrf(fastapi: FastAPI) -> None:
    """
    CSRFを設定する

    :param fastapi: FastAPIインスタンス
    :return: なし
    """

    @CsrfProtect.load_config
    def load_csrf_settings() -> CsrfSettings:
        return CsrfSettings()

    @fastapi.exception_handler(CsrfProtectError)
    def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "url": str(request.url)},
        )


app = create_app()


@app.get("/", response_model=SuccessMessage)
def root() -> dict:
    """ルートエンドポイント"""
    return {"message": "Welcome to the FastAPI!"}
