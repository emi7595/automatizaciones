"""
Centralized logging configuration for the WhatsApp Automation MVP.
"""
import logging
import logging.config
import sys
from pathlib import Path
from datetime import datetime
from app.core.config import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to the level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging():
    """Set up comprehensive logging configuration."""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Log file paths
    app_log_file = logs_dir / "app.log"
    error_log_file = logs_dir / "errors.log"
    whatsapp_log_file = logs_dir / "whatsapp.log"
    database_log_file = logs_dir / "database.log"
    api_log_file = logs_dir / "api.log"
    
    # Logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(asctime)s | %(levelname)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "colored": {
                "()": ColoredFormatter,
                "format": "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            # Console handler with colors
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "colored",
                "stream": sys.stdout
            },
            # Main application log file
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": str(app_log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            # Error log file
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": str(error_log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            # WhatsApp specific log file
            "whatsapp_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": str(whatsapp_log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            # Database operations log file
            "database_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": str(database_log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            # API requests log file
            "api_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": str(api_log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            # Root logger
            "": {
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False
            },
            # Application logger
            "app": {
                "level": "DEBUG",
                "handlers": ["console", "app_file"],
                "propagate": False
            },
            # WhatsApp service logger
            "app.services.whatsapp_service": {
                "level": "DEBUG",
                "handlers": ["console", "whatsapp_file"],
                "propagate": False
            },
            # Message service logger
            "app.services.message_service": {
                "level": "DEBUG",
                "handlers": ["console", "app_file"],
                "propagate": False
            },
            # API logger
            "app.api": {
                "level": "DEBUG",
                "handlers": ["console", "api_file"],
                "propagate": False
            },
            # Database logger
            "app.database": {
                "level": "DEBUG",
                "handlers": ["database_file"],
                "propagate": False
            },
            # Background tasks logger
            "app.tasks": {
                "level": "DEBUG",
                "handlers": ["console", "app_file"],
                "propagate": False
            },
            # FastAPI logger
            "fastapi": {
                "level": "INFO",
                "handlers": ["console", "api_file"],
                "propagate": False
            },
            # Uvicorn logger
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False
            },
            # SQLAlchemy logger
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["database_file"],
                "propagate": False
            },
            # Celery logger
            "celery": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False
            },
            # HTTP requests logger
            "httpx": {
                "level": "INFO",
                "handlers": ["console", "whatsapp_file"],
                "propagate": False
            }
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Get root logger
    logger = logging.getLogger("app")
    logger.info("Logging system initialized successfully")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Custom log decorator for function calls
def log_function_call(logger: logging.Logger = None):
    """
    Decorator to log function calls with parameters and return values.
    
    Args:
        logger: Logger instance (optional)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if logger is None:
                func_logger = logging.getLogger(func.__module__)
            else:
                func_logger = logger
            
            func_logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            
            try:
                result = func(*args, **kwargs)
                func_logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                func_logger.error(f"{func.__name__} failed with error: {str(e)}")
                raise
        
        return wrapper
    return decorator


# Performance logging decorator
def log_performance(logger: logging.Logger = None):
    """
    Decorator to log function execution time.
    
    Args:
        logger: Logger instance (optional)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if logger is None:
                func_logger = logging.getLogger(func.__module__)
            else:
                func_logger = logger
            
            start_time = datetime.now()
            func_logger.debug(f"Starting {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                func_logger.info(f"{func.__name__} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                func_logger.error(f"{func.__name__} failed after {execution_time:.3f}s with error: {str(e)}")
                raise
        
        return wrapper
    return decorator
