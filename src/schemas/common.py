from pydantic import BaseModel


class SuccessMessage(BaseModel):
    """
    成功メッセージ
    - message: メッセージ
    """
    message: str
