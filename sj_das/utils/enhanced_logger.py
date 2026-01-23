"""
Enhanced Logging System for SJ-DAS
Provides structured logging with rotation, performance tracking, and multiple outputs
"""
import json
import logging
import logging.handlers
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, "context"):
            log_data["context"] = record.context

        return json.dumps(log_data)


class EnhancedLogger:
    """Enhanced logger with multiple outputs and structured logging."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # Console handler (human-readable)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler with rotation (all logs)
        file_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "sj_das.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_formatter)
        self.logger.addHandler(file_handler)

        # Error file handler (errors only)
        error_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(console_formatter)
        self.logger.addHandler(error_handler)

        # Structured JSON handler
        json_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "structured.jsonl",
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(json_handler)

    def debug(self, message: str, context: Dict[str, Any] = None):
        """Log debug message with optional context."""
        extra = {"context": context} if context else {}
        self.logger.debug(message, extra=extra)

    def info(self, message: str, context: Dict[str, Any] = None):
        """Log info message with optional context."""
        extra = {"context": context} if context else {}
        self.logger.info(message, extra=extra)

    def warning(self, message: str, context: Dict[str, Any] = None):
        """Log warning message with optional context."""
        extra = {"context": context} if context else {}
        self.logger.warning(message, extra=extra)

    def error(self, message: str,
              context: Dict[str, Any] = None, exc_info=None):
        """Log error message with optional context and exception."""
        extra = {"context": context} if context else {}
        self.logger.error(message, extra=extra, exc_info=exc_info)

    def critical(self, message: str,
                 context: Dict[str, Any] = None, exc_info=None):
        """Log critical message with optional context and exception."""
        extra = {"context": context} if context else {}
        self.logger.critical(message, extra=extra, exc_info=exc_info)


# Performance logging decorator
def log_performance(logger: EnhancedLogger):
    """Decorator to log function performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(
                    f"{func.__name__} completed",
                    context={"duration_ms": round(elapsed * 1000, 2)}
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed",
                    context={
                        "duration_ms": round(elapsed * 1000, 2),
                        "error": str(e)
                    },
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


# Global logger instance
def get_logger(name: str) -> EnhancedLogger:
    """Get or create an enhanced logger."""
    return EnhancedLogger(name)
