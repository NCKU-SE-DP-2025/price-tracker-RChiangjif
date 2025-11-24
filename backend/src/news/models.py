from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

# 引入核心數據庫配置
from src.database import Base

# --- 關聯表：用戶點讚新聞 ---
user_news_association_table = Table(
    "user_news_upvotes",
    Base.metadata,
    # 引用 users.id (假設 users 表在 auth 模組的 models.py 中定義)
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column(
        "news_articles_id", Integer, ForeignKey("news_articles.id"), primary_key=True
    ),
)

# --- 新聞文章模型 ---
class NewsArticle(Base):
    __tablename__ = "news_articles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    time = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    
    # 與 User 模型的反向關聯
    upvoted_by_users = relationship(
        "User", 
        secondary=user_news_association_table, 
        back_populates="upvoted_news"
    )
