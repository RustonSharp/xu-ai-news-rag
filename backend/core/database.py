"""
Database configuration and session management.
"""
import os
from sqlmodel import create_engine, Session
from typing import Generator
from contextlib import contextmanager
from utils.logging_config import app_logger


class DatabaseManager:
    """Database connection manager."""
    
    def __init__(self):
        self._engine = None
        self._database_path = os.getenv("DATABASE_PATH")
        if not self._database_path:
            raise ValueError("DATABASE_PATH environment variable is not set")
    
    @property
    def engine(self):
        """Get database engine, creating it if necessary."""
        if self._engine is None:
            # Configure connection pool for better performance
            self._engine = create_engine(
                f"sqlite:///{self._database_path}",
                pool_size=20,  # Increase pool size
                max_overflow=30,  # Allow more overflow connections
                pool_timeout=60,  # Increase timeout
                pool_recycle=3600,  # Recycle connections every hour
                pool_pre_ping=True,  # Verify connections before use
                echo=False  # Set to True for SQL debugging
            )
            app_logger.info(f"Database engine created for: {self._database_path}")
        return self._engine
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            app_logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """Get database session for synchronous use."""
        return Session(self.engine)


# Global database manager instance
db_manager = DatabaseManager()


def get_database_engine():
    """Get database engine (for backward compatibility)."""
    return db_manager.engine


def get_database_session() -> Generator[Session, None, None]:
    """Get database session (for dependency injection)."""
    with db_manager.get_session() as session:
        yield session
