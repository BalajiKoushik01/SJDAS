import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = "sj_das") -> logging.Logger:
    """
    Configure industry-standard logging with rotation and console output.
    """
    logger = logging.getLogger(name)

    # Singleton pattern check
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. File Handler (Rotating)
    # Ensure log directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Global instance for easy import
log = setup_logger()
