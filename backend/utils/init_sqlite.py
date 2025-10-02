import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlmodel import SQLModel, create_engine
from utils.logging_config import app_logger
from models.rss_source import RssSource
from models.document import Document
from models.user import User
from models.analysis import Analysis

# Try to load dotenv to support reading environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    app_logger.warning("Note: python-dotenv library is not installed, environment variables will be read from the system.")
    app_logger.info("If you need to load environment variables from .env file, please run: pip install python-dotenv")

def init_db():
    """
    Initializes the SQLite database and creates tables based on SQLModel metadata.
    """
    db_path = os.getenv("DATABASE_PATH")
    if not db_path:
        app_logger.error("DATABASE_PATH environment variable is not set.")
        return
    app_logger.info(f"Database path: {db_path}")
    engine = create_engine(f"sqlite:///{db_path}")
    
    app_logger.info("Creating database and tables...")
    SQLModel.metadata.create_all(engine)
    app_logger.info("Database and tables created successfully.")

if __name__ == "__main__":
    init_db()