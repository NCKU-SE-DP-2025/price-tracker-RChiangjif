import json
import itertools
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup 
from urllib.parse import quote
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import delete, insert, select

from src.news.models import NewsArticle, user_news_association_table
# 引入核心配置和依賴
from src.config import OPENAI_API_KEY
from src.database import get_db

# --- Database Operations (CRUD) ---

class DatabaseService:
    """處理與 NewsArticle 和 Upvote 關聯表相關的數據庫操作。"""
    
    @staticmethod
    def add_news(db: Session, news_data: Dict[str, Any]): 
        """添加新的新聞文章到數據庫。"""
        db.add(NewsArticle(
            url=news_data["url"],
            title=news_data["title"],
            time=news_data["time"],
            content=news_data["content"],  # content 現在應該是字串
            summary=news_data["summary"],
            reason=news_data["reason"],
        ))
        db.commit()

    @staticmethod
    def get_article_upvote_details(article_id: int, uid: Optional[int], db: Session):
        """獲取文章點讚總數和指定用戶的點讚狀態。"""
        upvote_count = (
            db.query(user_news_association_table)
            .filter_by(news_articles_id=article_id)
            .count()
        )
        voted = False
        if uid:
            voted = (
                    db.query(user_news_association_table)
                    .filter_by(news_articles_id=article_id, user_id=uid)
                    .first()
                    is not None
            )
        return upvote_count, voted

    @staticmethod
    def toggle_upvote(news_id: int, user_id: int, db: Session):
        """切換文章的點讚狀態 (點讚或取消點讚)。"""
        # ... (使用 delete 和 insert 語句的原始邏輯)
        existing_upvote = db.execute(
            select(user_news_association_table).where(
                user_news_association_table.c.news_articles_id == news_id,
                user_news_association_table.c.user_id == user_id,
            )
        ).scalar()

        if existing_upvote:
            delete_stmt = delete(user_news_association_table).where(
                user_news_association_table.c.news_articles_id == news_id,
                user_news_association_table.c.user_id == user_id,
            )
            db.execute(delete_stmt)
            db.commit()
            return "Upvote removed"
        else:
            insert_stmt = insert(user_news_association_table).values(
                news_articles_id=news_id, user_id=user_id
            )
            db.execute(insert_stmt)
            db.commit()
            return "Article upvoted"
            
# --- Web Scraping and AI Operations ---

class NewsScrapingService:
    """處理新聞爬蟲、AI 交互和排程任務的業務邏輯。"""
    _id_counter = itertools.count(start=1000000)
    
    @classmethod
    def get_client(cls):
        """Get or create OpenAI client."""
        # Always try to create a client when needed (allows mocking to work)
        try:
            return OpenAI(api_key=OPENAI_API_KEY)
        except Exception:
            # If initialization fails, return None
            return None

    @staticmethod
    def get_news_info(search_term: str, is_initial: bool = False) -> List[Dict[str, Any]]:
        """從 udn API 獲取新聞列表。"""
        # ... (原始的 get_news_info 邏輯)
        all_news_data = []
        page_range = range(1, 10) if is_initial else range(1, 2)
        
        for page_number in page_range:
            params = {
                "page": page_number,
                "id": f"search:{quote(search_term)}",
                "channelId": 2,
                "type": "searchword",
            }
            response = requests.get("https://udn.com/api/more", params=params)
            
            if response.status_code == 200:
                data = response.json().get("lists", [])
                if is_initial:
                    all_news_data.extend(data)
                else:
                    return data # For non-initial, just return first page list

        return all_news_data

    @staticmethod
    def extract_full_content(url: str) -> Optional[Dict[str, Any]]:
        """爬取單個文章的詳細內容。"""
        # ... (原始的 BeautifulSoup 爬取邏輯)
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser") 
            title = soup.find("h1", class_="article-content__title").text
            time = soup.find("time", class_="article-content__time").text
            content_section = soup.find("section", class_="article-content__editor")

            paragraphs = [
                p.text
                for p in content_section.find_all("p")
                if p.text.strip() != "" and "▪" not in p.text
            ]
            
            # 將內容轉換為單一字串，以便存入 DB/傳輸
            full_content = " ".join(paragraphs) 

            return {
                "url": url,
                "title": title,
                "time": time,
                "content": full_content,
            }
        except Exception:
            # 處理可能因網頁結構不同導致的解析錯誤
            return None

    @classmethod
    def analyze_relevance(cls, title: str) -> str:
        """使用 GPT 判斷新聞標題的關聯度。"""
        relevance_messages = [
            {
                "role": "system",
                "content": "你是一個關聯度評估機器人，請評估新聞標題是否與「民生用品的價格變化」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)",
            },
            {"role": "user", "content": f"{title}"},
        ]
        client = cls.get_client()
        if not client:
            return "medium"  # Default to medium if client not available
        ai_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=relevance_messages,
        )
        return ai_response.choices[0].message.content.strip()

    @classmethod
    def generate_summary(cls, content: str) -> Dict[str, str]:
        """使用 GPT 生成新聞摘要 (影響與原因)。"""
        summary_messages = [
            {
                "role": "system",
                "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
            },
            {"role": "user", "content": f"{content}"},
        ]

        client = cls.get_client()
        if not client:
            return {"影響": "摘要生成失敗", "原因": "摘要生成失敗"}
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=summary_messages,
        )
        result = completion.choices[0].message.content
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"影響": "摘要生成失敗", "原因": "摘要生成失敗"}

    @classmethod
    def get_news(cls, db: Session, search_term: str = "價格", is_initial: bool = False):
        """
        排程/啟動時執行的主要流程：爬取 -> 分析 -> 摘要 -> 存入 DB。
        """
        news_data_list = cls.get_news_info(search_term, is_initial=is_initial)
        
        for news in news_data_list:
            relevance = cls.analyze_relevance(news["title"])
            
            if relevance.lower() == "high":
                detailed_news = cls.extract_full_content(news["titleLink"])
                
                if detailed_news:
                    # 獲取摘要，並將結果合併
                    summary_result = cls.generate_summary(detailed_news["content"])
                    detailed_news["summary"] = summary_result.get("影響", "N/A")
                    detailed_news["reason"] = summary_result.get("原因", "N/A")
                    
                    DatabaseService.add_news(db, detailed_news)

    @classmethod
    def get_news_job(cls):
        """
        Scheduler 任務包裝器，用於安全地管理 DB Session。
        這個方法會在 src/main.py 的排程中被呼叫。
        """
        db = next(get_db()) # 獲取一個新的 session
        try:
            cls.get_news(db, search_term="價格", is_initial=False)
        finally:
            db.close() # 確保 session 關閉

    @classmethod
    def search_news(cls, prompt: str) -> List[Dict[str, Any]]:
        """
        根據用戶提示搜尋新聞 (不存入 DB，即時爬取)。
        """
        # 1. 提取關鍵字
        keyword_messages = [
            {
                "role": "system",
                "content": "你是一個關鍵字提取機器人，請提取出用戶希望看見的關鍵字。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
            },
            {"role": "user", "content": f"{prompt}"},
        ]

        client = cls.get_client()
        if not client:
            return []  # Return empty list if client not available
        ai_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=keyword_messages,
        )
        keywords = ai_response.choices[0].message.content

        # 2. 爬取新聞
        news_items = cls.get_news_info(keywords, is_initial=False)
        news_list = []
        
        for news in news_items:
            detailed_news = cls.extract_full_content(news["titleLink"])
            if detailed_news:
                # 賦予臨時 ID (非 DB ID)
                detailed_news["id"] = next(cls._id_counter) 
                news_list.append(detailed_news)
                
        # 3. 排序並返回
        return sorted(news_list, key=lambda x: x["time"], reverse=True)

