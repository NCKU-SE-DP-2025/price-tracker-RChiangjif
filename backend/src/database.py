from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL

Base = declarative_base() # All models will inherit from this

engine = create_engine(DATABASE_URL, echo=False)

# SessionLocal is used to instantiate a DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    """Called on startup to create tables if they don't exist."""
    Base.metadata.create_all(engine)
