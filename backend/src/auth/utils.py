from datetime import datetime, timedelta
from typing import Optional
import hashlib

from jose import jwt
from passlib.context import CryptContext

# 從 src/config.py 引入配置
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# --- Password Utilities ---
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼是否匹配雜湊值。"""
    # 先用 SHA-256 預處理密碼以確保長度不超過 72 字節
    processed_password = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(processed_password, hashed_password)

def get_password_hash(password: str) -> str:
    """對密碼進行雜湊處理。"""
    # 先用 SHA-256 預處理密碼以確保長度不超過 72 字節
    processed_password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(processed_password)

# --- JWT Utilities ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """創建 JWT Access Token。"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
