"""
UDN News Scraper Module

This module provides the UDNCrawler class for fetching, parsing, and saving news articles from the UDN website.
The class extends the NewsCrawlerBase and includes functionalities to search for news articles based on a search term,
parse the details of individual articles, and save them to a database using SQLAlchemy ORM.

Classes:
    UDNCrawler: A class to scrape news from UDN.

Exceptions:
    DomainMismatchException: Raised when the URL domain does not match the expected domain for the crawler.

Usage Example:
    crawler = UDNCrawler(timeout=10)
    headlines = crawler.startup("technology")
    for headline in headlines:
        news = crawler.parse(headline.url)
        crawler.save(news, db_session)

UDNCrawler Methods:
    __init__(self, timeout: int = 5): Initializes the crawler with a default timeout for HTTP requests.
    startup(self, search_term: str) -> list[Headline]: Fetches news headlines for a given search term across multiple pages.
    get_headline(self, search_term: str, page: int | tuple[int, int]) -> list[Headline]: Fetches news headlines for specified pages.
    _fetch_news(self, page: int, search_term: str) -> list[Headline]: Helper method to fetch news headlines for a specific page.
    _create_search_params(self, page: int, search_term: str): Creates the parameters for the search request.
    _perform_request(self, params: dict): Performs the HTTP request to fetch news data.
    _parse_headlines(response): Parses the response to extract headlines.
    parse(self, url: str) -> News: Parses a news article from a given URL.
    _extract_news(soup, url: str) -> News: Extracts news details from the BeautifulSoup object.
    save(self, news: News, db: Session): Saves a news article to the database.
    _commit_changes(db: Session): Commits the changes to the database with error handling.
"""

from typing import Optional
from urllib.parse import quote
import logging
import requests
from requests import Response
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from .crawler_base import NewsCrawlerBase, Headline, News
from src.news.models import NewsArticle

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class UDNCrawler(NewsCrawlerBase):
    CHANNEL_ID = 2

    def __init__(self, timeout: int = 5) -> None:
        super().__init__()
        self.news_website_url = "https://udn.com/api/more"
        self.timeout = timeout
        self.session = requests.Session()
        # Set headers to mimic a browser to avoid being blocked
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def startup(self, search_term: str) -> list[Headline]:
        """
        Initializes the application by fetching news headlines for a given search term across multiple pages.
        This method is typically called at the beginning of the program when there is no data available,
        hence it fetches headlines from the first 10 pages.

        :param search_term: The term to search for in news headlines.
        :return: A list of Headline namedtuples containing the title and URL of news articles.
        :rtype: list[Headline]
        """
        return self.get_headline(search_term, page=(1, 10))

    def get_headline(
        self, search_term: str, page: int | tuple[int, int]
    ) -> list[Headline]:
        """
        Fetches news headlines for a given search term from specified pages.

        :param search_term: The term to search for in news headlines.
        :param page: A page number (int) or a tuple of start and end page numbers (tuple[int, int]).
        :return: A list of Headline namedtuples containing the title and URL of news articles.
        """
        # Calculate the range of pages to fetch news from.
        # If 'page' is a tuple, unpack it and create a range representing those pages (inclusive).
        # If 'page' is an int, create a list containing only that single page number.
        page_range = range(page[0], page[1] + 1) if isinstance(page, tuple) else [page]
        
        all_headlines = []
        for page_num in page_range:
            headlines = self._fetch_news(page_num, search_term)
            all_headlines.extend(headlines)
        
        return all_headlines

    def _fetch_news(self, page: int, search_term: str) -> list[Headline]:
        """
        Helper method to fetch news headlines for a specific page.

        :param page: The page number to fetch.
        :param search_term: The search term for the news.
        :return: A list of Headline namedtuples for the given page.
        """
        params = self._create_search_params(page, search_term)
        response = self._perform_request(params=params)
        
        if response.status_code == 200:
            return self._parse_headlines(response)
        
        return []

    def _create_search_params(self, page: int, search_term: str) -> dict:
        """
        Creates the parameters for the search request to UDN API.

        :param page: The page number for the search.
        :param search_term: The search term for the news.
        :return: A dictionary containing the search parameters.
        """
        return {
            "page": page,
            "id": f"search:{quote(search_term)}",
            "channelId": self.CHANNEL_ID,
            "type": "searchword",
        }

    def _perform_request(
        self, url: str | None = None, params: dict | None = None
    ) -> Response:
        """
        Performs the HTTP request to fetch news data from UDN API.

        :param url: Optional custom URL for the request. Defaults to news_website_url.
        :param params: The query parameters for the request.
        :return: A Response object from the HTTP request.
        """
        request_url = url or self.news_website_url
        try:
            response = self.session.get(request_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error performing request to {request_url}: {e}")
            return Response()

    @staticmethod
    def _parse_headlines(response: Response) -> list[Headline]:
        """
        Parses the response from UDN API to extract headlines.

        :param response: The Response object from the API request.
        :return: A list of Headline namedtuples extracted from the response.
        """
        try:
            data = response.json().get("lists", [])
            headlines = []
            
            for item in data:
                headline = Headline(
                    title=item.get("title", ""),
                    url=item.get("titleLink", "")
                )
                headlines.append(headline)
            
            return headlines
        except Exception as e:
            logger.error(f"Error parsing headlines: {e}")
            return []

    def parse(self, url: str) -> News | None:
        """
        Parses a news article from a given URL.

        :param url: The URL of the news article to be parsed.
        :return: A News object containing the title, URL, time, and content of the news article.
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            return self._extract_news(soup, url)
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return None

    @staticmethod
    def _extract_news(soup: BeautifulSoup, url: str) -> News | None:
        """
        Extracts news details from the BeautifulSoup object.

        :param soup: The BeautifulSoup object of the parsed HTML.
        :param url: The URL of the news article.
        :return: A News object containing the extracted details.
        """
        try:
            title_elem = soup.find("h1", class_="article-content__title")
            title = title_elem.text.strip() if title_elem else ""
            
            time_elem = soup.find("time", class_="article-content__time")
            time = time_elem.text.strip() if time_elem else ""
            
            content_section = soup.find("section", class_="article-content__editor")
            
            if content_section:
                paragraphs = [
                    p.text.strip()
                    for p in content_section.find_all("p")
                    if p.text.strip() != "" and "▪" not in p.text
                ]
                content = " ".join(paragraphs)
            else:
                content = ""
            
            return News(
                title=title,
                url=url,
                time=time,
                content=content,
            )
        except Exception as e:
            logger.error(f"Error extracting news from soup: {e}")
            return None

    def save(self, news: News, db: Session):
        """
        Saves a news article to the database.

        :param news: A News object containing the news details including summary and reason.
        :param db: An instance of the database session to use for saving the news.
        """
        try:
            # Check if the news already exists in the database
            existing_article = db.query(NewsArticle).filter_by(url=str(news.url)).first()
            
            if existing_article:
                logger.info(f"News article already exists: {news.url}")
                return
            
            # Create a new NewsArticle object
            # Ensure summary and reason are strings, defaulting to empty string if None
            news_article = NewsArticle(
                url=str(news.url),
                title=news.title,
                time=news.time,
                content=news.content,
                summary=news.summary or "",
                reason=news.reason or "",
            )
            
            db.add(news_article)
            self._commit_changes(db)
        except Exception as e:
            logger.error(f"Error saving news: {e}")
            db.rollback()

    @staticmethod
    def _commit_changes(db: Session):
        """
        Commits the changes to the database with error handling.

        :param db: An instance of the database session.
        """
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing changes to database: {e}")
            raise