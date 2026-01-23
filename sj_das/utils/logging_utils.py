"""
Enhanced logging utilities for SJ-DAS.

Provides structured logging with context, performance tracking,
and better debugging capabilities.
"""

import functools
import logging
import time
from collections.abc import Callable
from contextlib import contextmanager


class StructuredLogger:
    """
    Enhanced logger with structured context and performance tracking.

    Features:
        - Structured logging with context
        - Performance timing
        - Operation tracking
        - Error context capture
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._context = {}

    def with_context(self, **kwargs) -> 'StructuredLogger':
        """
        Add context to logger.

        Usage:
            logger.with_context(user_id=123, operation="import").info("Started")
        """
        new_logger = StructuredLogger(self.logger.name)
        new_logger._context = {**self._context, **kwargs}
        return new_logger

    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if self._context:
            context_str = " | ".join(
                f"{k}={v}" for k, v in self._context.items())
            return f"{message} [{context_str}]"
        return message

    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.logger.debug(self._format_message(message), extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.logger.info(self._format_message(message), extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.logger.warning(self._format_message(message), extra=kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message with context."""
        self.logger.error(
            self._format_message(message),
            exc_info=exc_info,
            extra=kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical message with context."""
        self.logger.critical(
            self._format_message(message),
            exc_info=exc_info,
            extra=kwargs)

    @contextmanager
    def operation(self, operation_name: str, **context):
        """
        Context manager for tracking operations with timing.

        Usage:
            with logger.operation("image_import", file_size=1024):
                # Do work
                pass
        """
        start_time = time.time()
        op_logger = self.with_context(operation=operation_name, **context)
        op_logger.info(f"Started: {operation_name}")

        try:
            yield op_logger
        except Exception:
            elapsed = time.time() - start_time
            op_logger.error(
                f"Failed: {operation_name} after {elapsed:.2f}s",
                exc_info=True
            )
            raise
        else:
            elapsed = time.time() - start_time
            op_logger.info(f"Completed: {operation_name} in {elapsed:.2f}s")


def log_performance(func: Callable) -> Callable:
    """
    Decorator to log function performance.

    Usage:
        @log_performance
        def expensive_operation():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time

            if elapsed > 1.0:  # Log slow operations
                logger.warning(
                    f"{func.__name__} took {elapsed:.2f}s (slow operation)"
                )
            else:
                logger.debug(f"{func.__name__} completed in {elapsed:.2f}s")

            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {elapsed:.2f}s: {e}",
                exc_info=True
            )
            raise

    return wrapper


def log_method_calls(cls):
    """
    Class decorator to log all method calls.

    Usage:
        @log_method_calls
        class MyClass:
            pass
    """
    logger = logging.getLogger(cls.__module__)

    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            setattr(cls, attr_name, _wrap_method(attr, logger))

    return cls


def _wrap_method(method: Callable, logger: logging.Logger) -> Callable:
    """Wrap method with logging."""
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {method.__name__}")
        try:
            result = method(*args, **kwargs)
            logger.debug(f"Completed {method.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {method.__name__}: {e}", exc_info=True)
            raise

    return wrapper


class PerformanceMonitor:
    """
    Monitor and log performance metrics.

    Features:
        - Operation timing
        - Memory usage tracking
        - Performance statistics
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Performance.{name}")
        self.timings = []

    def record_timing(self, operation: str, duration: float):
        """Record operation timing."""
        self.timings.append((operation, duration))

        if duration > 1.0:
            self.logger.warning(
                f"Slow operation: {operation} took {duration:.2f}s"
            )
        else:
            self.logger.debug(
                f"Operation: {operation} completed in {duration:.2f}s"
            )

    def get_statistics(self) -> dict:
        """Get performance statistics."""
        if not self.timings:
            return {}

        durations = [d for _, d in self.timings]
        return {
            'count': len(durations),
            'total': sum(durations),
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations)
        }

    def log_statistics(self):
        """Log performance statistics."""
        stats = self.get_statistics()
        if stats:
            self.logger.info(
                f"Performance stats: {stats['count']} operations, "
                f"avg={stats['avg']:.2f}s, max={stats['max']:.2f}s"
            )
