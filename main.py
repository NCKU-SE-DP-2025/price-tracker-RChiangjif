import sentry_sdk
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import CORS_ORIGINS, SENTRY_DSN, SCHEDULER_INTERVAL_MINUTES
from .database import Base, engine, SessionLocal
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

# 3. Router Inclusion
app.include_router(auth_router)
app.include_router(news_router)
app.include_router(prices_router)

# 4. Scheduler Events
@app.on_event("startup")
def start_scheduler():
    db: Session = SessionLocal()
    # Initial population logic
    if db.query(NewsArticle).count() == 0:
        NewsScrapingService.get_news(db) # Pass db session to service
    db.close()
    
    # Schedule recurring job
    background_scheduler.add_job(
        NewsScrapingService.get_news_job, # Use a wrapper job to manage DB session
        "interval", 
        minutes=SCHEDULER_INTERVAL_MINUTES
    )
    background_scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    background_scheduler.shutdown()

# 5. Root Endpoint (can be moved to misc/prices router)
@app.get("/")
def read_root():
  return 50
