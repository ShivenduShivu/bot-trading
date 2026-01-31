"""
Database Connection and Session Management
Handles SQLite database setup and connections
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./algo_trading.db")

# Create database engine
# connect_args only needed for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite specific
)

# Create session factory
# Sessions are like "conversations" with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for database models
Base = declarative_base()


# Dependency to get database session
def get_db():
    """
    Create a new database session for each request
    Automatically closes when done
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()