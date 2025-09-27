import os
import sys
from loguru import logger
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def setup_logging():
    """
    根据环境变量配置日志系统
    """
    # 移除默认的日志处理器
    logger.remove()
    
    # 获取日志配置
    log_level = os.getenv("LOGGING_LEVEL", "INFO")
    console_enabled = os.getenv("LOGGING_CONSOLE_ENABLED", "true").lower() == "true"
    console_format = os.getenv("LOGGING_CONSOLE_FORMAT", "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    file_enabled = os.getenv("LOGGING_FILE_ENABLED", "true").lower() == "true"
    file_path = os.getenv("LOGGING_FILE_PATH", "./logs/app.log")
    file_rotation = os.getenv("LOGGING_FILE_ROTATION", "500 MB")
    file_retention = os.getenv("LOGGING_FILE_RETENTION", "30 days")
    file_compression = os.getenv("LOGGING_FILE_COMPRESSION", "zip")
    file_format = os.getenv("LOGGING_FILE_FORMAT", "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")
    
    error_file_enabled = os.getenv("LOGGING_ERROR_FILE_ENABLED", "true").lower() == "true"
    error_file_path = os.getenv("LOGGING_ERROR_FILE_PATH", "./logs/error.log")
    error_file_level = os.getenv("LOGGING_ERROR_FILE_LEVEL", "ERROR")
    error_file_rotation = os.getenv("LOGGING_ERROR_FILE_ROTATION", "100 MB")
    error_file_retention = os.getenv("LOGGING_ERROR_FILE_RETENTION", "60 days")
    error_file_compression = os.getenv("LOGGING_ERROR_FILE_COMPRESSION", "zip")
    error_file_format = os.getenv("LOGGING_ERROR_FILE_FORMAT", "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message} | {extra}")
    
    # 配置控制台日志
    if console_enabled:
        logger.add(
            sys.stdout,
            format=console_format,
            level=log_level,
            colorize=True
        )
    
    # 确保日志目录存在
    if file_enabled or error_file_enabled:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        os.makedirs(os.path.dirname(error_file_path), exist_ok=True)
    
    # 配置文件日志
    if file_enabled:
        logger.add(
            file_path,
            format=file_format,
            level=log_level,
            rotation=file_rotation,
            retention=file_retention,
            compression=file_compression,
            encoding="utf-8"
        )
    
    # 配置错误文件日志
    if error_file_enabled:
        logger.add(
            error_file_path,
            format=error_file_format,
            level=error_file_level,
            rotation=error_file_rotation,
            retention=error_file_retention,
            compression=error_file_compression,
            encoding="utf-8"
        )
    
    return logger

# 初始化日志配置
app_logger = setup_logging()