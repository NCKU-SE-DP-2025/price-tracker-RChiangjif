from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# 從 src/database.py 引入 Base
from ..database import Base 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    
    # 關聯到 news 模組的 NewsArticle 模型
    upvoted_news = relationship(
        "NewsArticle",
        secondary="user_news_upvotes", 
        back_populates="upvoted_by_users",
    )
