"""
Application settings and configuration management.
"""
import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings."""
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/database.db")
    
    # Application
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "5001"))
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
    
    # RSS Scheduler
    AUTO_START_SCHEDULER: bool = os.getenv("AUTO_START_SCHEDULER", "true").lower() == "true"
    ALLOW_MANUAL_SCHEDULER_START: bool = os.getenv("ALLOW_MANUAL_SCHEDULER_START", "true").lower() == "true"
    
    # AI Models
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    RERANK_MODEL_NAME: str = os.getenv("RERANK_MODEL_NAME", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    
    # Vector Store
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "./data/index.faiss")
    
    # External APIs
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # Email Notifications
    NOTIFICATION_EMAILS: List[str] = os.getenv("NOTIFICATION_EMAILS", "").split(",") if os.getenv("NOTIFICATION_EMAILS") else []
    
    # SMTP Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
    EMAIL_USERNAME: Optional[str] = os.getenv("EMAIL_USERNAME")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173", 
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # File Upload
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: set = {"xlsx", "xls", "pdf", "txt"}
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # Detailed Logging Configuration
    LOGGING_CONSOLE_ENABLED: bool = os.getenv("LOGGING_CONSOLE_ENABLED", "true").lower() == "true"
    LOGGING_CONSOLE_FORMAT: str = os.getenv("LOGGING_CONSOLE_FORMAT", "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    LOGGING_FILE_ENABLED: bool = os.getenv("LOGGING_FILE_ENABLED", "true").lower() == "true"
    LOGGING_FILE_PATH: str = os.getenv("LOGGING_FILE_PATH", "./logs/app.log")
    LOGGING_FILE_ROTATION: str = os.getenv("LOGGING_FILE_ROTATION", "500 MB")
    LOGGING_FILE_RETENTION: str = os.getenv("LOGGING_FILE_RETENTION", "30 days")
    LOGGING_FILE_COMPRESSION: str = os.getenv("LOGGING_FILE_COMPRESSION", "zip")
    LOGGING_FILE_FORMAT: str = os.getenv("LOGGING_FILE_FORMAT", "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")
    
    LOGGING_ERROR_FILE_ENABLED: bool = os.getenv("LOGGING_ERROR_FILE_ENABLED", "true").lower() == "true"
    LOGGING_ERROR_FILE_PATH: str = os.getenv("LOGGING_ERROR_FILE_PATH", "./logs/error.log")
    LOGGING_ERROR_FILE_LEVEL: str = os.getenv("LOGGING_ERROR_FILE_LEVEL", "ERROR")
    LOGGING_ERROR_FILE_ROTATION: str = os.getenv("LOGGING_ERROR_FILE_ROTATION", "100 MB")
    LOGGING_ERROR_FILE_RETENTION: str = os.getenv("LOGGING_ERROR_FILE_RETENTION", "60 days")
    LOGGING_ERROR_FILE_COMPRESSION: str = os.getenv("LOGGING_ERROR_FILE_COMPRESSION", "zip")
    LOGGING_ERROR_FILE_FORMAT: str = os.getenv("LOGGING_ERROR_FILE_FORMAT", "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message} | {extra}")


# Global settings instance
settings = Settings()
