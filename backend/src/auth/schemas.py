from pydantic import BaseModel

class UserAuthSchema(BaseModel):
    """
    用於用戶註冊和登入請求的 Pydantic 模型。
    """
    username: str
    password: str

class Token(BaseModel):
    """
    用於登入成功後返回 JWT Token 的響應模型。
    """
    access_token: str
    token_type: str = "bearer"
