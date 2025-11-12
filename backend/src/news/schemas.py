from pydantic import BaseModel, Field, AnyHttpUrl
from typing import List

class PromptRequest(BaseModel):
    """
    用於 /search_news 端點的請求模型。
    """
    prompt: str

class NewsSumaryRequestSchema(BaseModel):
    """
    用於 /news_summary 端點的請求模型。
    """
    content: str
    
# --- 響應模型 ---
class NewsBase(BaseModel):
    """
    用於返回新聞文章列表的響應模型 (包含 upvote 狀態)。
    """
    id: int
    url: AnyHttpUrl
    title: str
    time: str
    content: str
    summary: str
    reason: str
    
    # 額外的業務邏輯欄位
    upvotes: int = Field(..., description="總點讚數")
    is_upvoted: bool = Field(..., description="當前用戶是否點讚")

    class Config:
        # 允許從 SQLAlchemy 物件讀取屬性
        orm_mode = True 
        # 為了容納 SQLAlchemy 的 _sa_instance_state 屬性
        from_attributes = True
