from typing import Union

from sqlalchemy.orm import Session

from .models import User
from .schemas import UserAuthSchema
from .utils import get_password_hash, verify_password

class UserService:
    @staticmethod
    def verify_user_password(db: Session, username: str, pwd: str) -> Union[User, bool]:
        """
        驗證用戶名和密碼。
        如果驗證成功，返回 User 物件；否則返回 False。
        """
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            return False
            
        # 使用 utils 驗證密碼
        if not verify_password(pwd, user.hashed_password):
            return False
            
        return user
    
    @staticmethod
    def create_user(db: Session, user_data: UserAuthSchema) -> User:
        """
        創建一個新用戶並將其儲存到數據庫。
        """
        # 使用 utils 雜湊密碼
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(username=user_data.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
