import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlmodel import SQLModel, create_engine
from utils.logging_config import app_logger
from models.source import Source
from models.document import Document
from models.user import User
from models.analysis import Analysis

# Import settings for database configuration
from config.settings import settings

# Create engine instance
db_path = settings.DATABASE_PATH
if not db_path:
    app_logger.error("DATABASE_PATH environment variable is not set.")
    engine = None
else:
    app_logger.info(f"Database path: {db_path}")
    engine = create_engine(
        f"sqlite:///{db_path}",
        pool_size=20,
        max_overflow=30,
        pool_timeout=60,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False
    )

def init_db():
    """
    Initializes the SQLite database and creates tables based on SQLModel metadata.
    """
    if not engine:
        app_logger.error("Database engine is not available. Cannot initialize database.")
        return
    
    app_logger.info("Creating database and tables...")
    SQLModel.metadata.create_all(engine)
    app_logger.info("Database and tables created successfully.")

if __name__ == "__main__":
    init_db()