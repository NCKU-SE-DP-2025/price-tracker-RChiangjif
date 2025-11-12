from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from .models import NewsArticle
from .schemas import PromptRequest, NewsSumaryRequestSchema, NewsBase
from .service import DatabaseService, NewsScrapingService
# 引入核心依賴
from ..database import get_db
# 引入 auth 模組的依賴和模型 (處理授權)
from ..auth.dependencies import get_current_user
from ..auth.models import User 

router = APIRouter(prefix="/api/v1/news", tags=["news"])

def _format_news_list(news_list: List[NewsArticle], user_id: Optional[int], db: Session) -> List[NewsBase]:
    """Helper function to append upvote details to news objects."""
    result = []
    for article in news_list:
        upvotes, upvoted = DatabaseService.get_article_upvote_details(article.id, user_id, db)
        # 使用 NewsBase Pydantic 驗證並格式化
        result.append(
            NewsBase(
                **article.__dict__, 
                upvotes=upvotes, 
                is_upvoted=upvoted
            )
        )
    return result

@router.get("/news", response_model=List[NewsBase])
def read_news(db: Session = Depends(get_db)):
    """獲取所有新聞文章 (未登入用戶)。"""
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    return _format_news_list(news, None, db)

@router.get("/user_news", response_model=List[NewsBase])
def read_user_news(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """獲取所有新聞文章 (已登入用戶，顯示點讚狀態)。"""
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    return _format_news_list(news, user.id, db)

@router.post("/search_news")
async def search_news(request: PromptRequest):
    """根據用戶提示詞搜尋即時新聞。"""
    return NewsScrapingService.search_news(request.prompt)

@router.post("/news_summary")
async def news_summary(
    payload: NewsSumaryRequestSchema, 
    user: User = Depends(get_current_user) # 需要登入才能使用 AI 摘要
):
    """為提供的文章內容生成摘要和原因分析。"""
    summary_result = NewsScrapingService.generate_summary(payload.content)
    return {
        "summary": summary_result.get("影響"), 
        "reason": summary_result.get("原因")
    }

@router.post("/{id}/upvote")
def upvote_article(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """切換新聞文章的點讚狀態。"""
    # 檢查新聞是否存在
    if db.query(NewsArticle).filter(NewsArticle.id == id).first() is None:
         raise HTTPException(status_code=404, detail="Article not found")
         
    message = DatabaseService.toggle_upvote(id, user.id, db)
    return {"message": message}
