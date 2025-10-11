"""
Dependency injection functions for FastAPI/Flask compatibility.
"""
from typing import Generator
from sqlmodel import Session
from core.database import get_database_session


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Can be used with FastAPI Depends() or similar dependency injection.
    """
    with get_database_session() as session:
        yield session


def get_db_session_sync() -> Session:
    """
    Get database session for synchronous use.
    Use this when you need a session outside of dependency injection.
    """
    from core.database import db_manager
    return db_manager.get_session_sync()
