from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from routers import todo, auth
from schemas.common import SuccessMessage
from schemas.auth import CsrfSettings
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

app = FastAPI()
app.include_router(todo.router)
app.include_router(auth.router)

origins = ['http://localhost:3000']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/", response_model=SuccessMessage)
def _root():
    return {"message": "Welcome to the FastAPI!"}
