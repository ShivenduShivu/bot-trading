"""
Database configuration
Supports both SQLite (development) and PostgreSQL (production)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment or use SQLite as fallback
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # Railway uses postgres:// but SQLAlchemy needs postgresql://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    # Development: use SQLite
    DATABASE_URL = "sqlite:///./algo_trading.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Production: use PostgreSQL
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()