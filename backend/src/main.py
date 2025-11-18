import sentry_sdk
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS, SENTRY_DSN, SCHEDULER_INTERVAL_MINUTES
from .database import create_db_and_tables, get_db
from .news.service import NewsScrapingService
from .auth.router import router as auth_router
from .news.router import router as news_router
from .prices.router import router as prices_router

# 1. Sentry Initialization
sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = FastAPI()
background_scheduler = BackgroundScheduler()

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Router Inclusion (Crucial step for linking all domains)
app.include_router(auth_router)
app.include_router(news_router)
app.include_router(prices_router)


# 4. Scheduler Events
@app.on_event("startup")
def start_scheduler():
    create_db_and_tables() # Create tables on startup
    
    # Run initial scrape (Get session via iterator)
    db = next(get_db())
    if db.query(NewsScrapingService.NewsArticle).count() == 0: 
        NewsScrapingService.get_news(db, is_initial=True)
    db.close()
    
    # Schedule recurring job
    background_scheduler.add_job(
        NewsScrapingService.get_news_job, 
        "interval", 
        minutes=SCHEDULER_INTERVAL_MINUTES
    )
    background_scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    background_scheduler.shutdown()

# 5. Root Endpoint (can also be moved to a /misc or /prices router)
@app.get("/")
def read_root():
  # Original return 50
  return {"message": "Welcome to the FastAPI project"}
