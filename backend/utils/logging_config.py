import os
import sys
from loguru import logger
from config.settings import settings

def setup_logging():
    """
    根据环境变量配置日志系统
    """
    # 移除默认的日志处理器
    logger.remove()
    
    # 获取日志配置
    log_level = settings.LOG_LEVEL
    console_enabled = settings.LOGGING_CONSOLE_ENABLED
    console_format = settings.LOGGING_CONSOLE_FORMAT
    
    file_enabled = settings.LOGGING_FILE_ENABLED
    file_path = settings.LOGGING_FILE_PATH
    file_rotation = settings.LOGGING_FILE_ROTATION
    file_retention = settings.LOGGING_FILE_RETENTION
    file_compression = settings.LOGGING_FILE_COMPRESSION
    file_format = settings.LOGGING_FILE_FORMAT
    
    error_file_enabled = settings.LOGGING_ERROR_FILE_ENABLED
    error_file_path = settings.LOGGING_ERROR_FILE_PATH
    error_file_level = settings.LOGGING_ERROR_FILE_LEVEL
    error_file_rotation = settings.LOGGING_ERROR_FILE_ROTATION
    error_file_retention = settings.LOGGING_ERROR_FILE_RETENTION
    error_file_compression = settings.LOGGING_ERROR_FILE_COMPRESSION
    error_file_format = settings.LOGGING_ERROR_FILE_FORMAT
    
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