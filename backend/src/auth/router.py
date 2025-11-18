from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .schemas import UserAuthSchema, Token
from .service import UserService
from .utils import create_access_token
# 引入 dependencies 檔案中的依賴函數
from .dependencies import get_current_user 
from ..database import get_db

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    用戶登入，成功則返回 JWT Access Token。
    """
    # 核心驗證邏輯委託給 service
    user = UserService.verify_user_password(db, form_data.username, form_data.password)
    
    if user == False:
        # 使用 HTTPException 來返回標準 FastAPI 錯誤響應
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect username or password"
        )
    
    # 使用 utils 創建 Token
    access_token = create_access_token(
        data={"sub": str(user.username)} # sub 是 JWT 標準的 Subject 欄位
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserAuthSchema)
def create_user(user: UserAuthSchema, db: Session = Depends(get_db)):
    """
    新用戶註冊。
    """
    # 檢查用戶是否已存在 (這是註冊的基本檢查，應該在 service 層實現，這裡簡化)
    if db.query(UserService.User).filter_by(username=user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
        
    return UserService.create_user(db, user)

@router.get("/me")
def read_users_me(user=Depends(get_current_user)):
    """
    獲取當前登入用戶的資訊。
    """
    # get_current_user 已經驗證了 Token 並返回 User 物件
    return {"username": user.username}
