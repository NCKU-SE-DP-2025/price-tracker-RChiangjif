from datetime import timedelta

# --- General Config ---
SECRET_KEY = "1892dhianiandowqd0n"  # IMPORTANT: Should use environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Database Config ---
DATABASE_URL = "sqlite:///news_database.db"

# --- External Service Config ---
SENTRY_DSN = "..." # Your Sentry DSN
OPENAI_API_KEY = "xxx"
SCHEDULER_INTERVAL_MINUTES = 100

# --- CORS Config ---
CORS_ORIGINS = ["http://localhost:8080"]
