from decouple import config
from pydantic import BaseModel

CRSF_SECRET_KEY = config('CSRF_SECRET_KEY')

class CsrfSettings(BaseModel):
    secret_key: str = CRSF_SECRET_KEY
    cookie_samesite: str = "none"
