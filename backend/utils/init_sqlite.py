from sqlmodel import SQLModel, create_engine
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.rss_source import RssSource
from models.document import Document

# Try to load dotenv to support reading environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("Note: python-dotenv library is not installed, environment variables will be read from the system.")
    logger.info("If you need to load environment variables from .env file, please run: pip install python-dotenv")

def init_db():
    """
    Initializes the SQLite database and creates tables based on SQLModel metadata.
    """
    db_path = os.getenv("DATABASE_PATH")
    if not db_path:
        logger.error("DATABASE_PATH environment variable is not set.")
        return
    logger.info(f"Database path: {db_path}")
    engine = create_engine(f"sqlite:///{db_path}")
    
    logger.info("Creating database and tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database and tables created successfully.")

if __name__ == "__main__":
    init_db()