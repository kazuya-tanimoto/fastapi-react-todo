from decouple import config
from pydantic import BaseModel

CRSF_SECRET_KEY = config("CSRF_SECRET_KEY")


class CsrfSettings(BaseModel):
    """
    CSRF設定
    - secret_key: CSRFトークンの秘密鍵
    - cookie_samesite: CSRFトークンのCookie
    """
    secret_key: str = CRSF_SECRET_KEY
    if config("ENVIRONMENT") == "production":
        cookie_samesite: str = "none"
        cookie_secure: bool = True


class CsrfToken(BaseModel):
    """
    CSRFトークン
    - csrf_token: CSRFトークン
    """
    csrf_token: str
