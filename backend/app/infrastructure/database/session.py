"""
Database session and connection management
"""
import os
from typing import Generator

from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker, Session  # type: ignore

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sat_tutor")

# Create engine with appropriate settings
engine = create_engine(
    DATABASE_URL,
    # Connection pool settings
    pool_pre_ping=True,  # Verify connection is still valid before use
    pool_size=5,  # Default connections in pool
    max_overflow=10  # Allow up to 10 additional connections
)

# Create a session factory
# Disable "expire on commit" for better performance
# This means we have to be careful with relationships after session commits
# but it's worth it for the performance boost
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False
)

# Create a base class for our declarative models
Base = declarative_base()

def get_db_session() -> Generator[Session, None, None]:
    """
    Get a database session for use in API endpoints
    
    Yields:
        SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()