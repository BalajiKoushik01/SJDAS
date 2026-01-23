"""
Utility Decorators for SJ-DAS
Provides retry logic, error handling, and validation decorators
"""
import functools
import time
from typing import Callable, Tuple, Type

from sj_das.utils.enhanced_logger import get_logger
from sj_das.utils.exceptions import SJDASException

logger = get_logger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts})",
                            context={"error": str(e), "delay": current_delay}
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts",
                            context={"error": str(e)},
                            exc_info=True
                        )

            raise last_exception
        return wrapper
    return decorator


def handle_errors(default_return=None, log_error: bool = True):
    """
    Decorator to catch and handle errors gracefully.

    Args:
        default_return: Value to return if error occurs
        log_error: Whether to log the error
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(
                        f"Error in {func.__name__}",
                        context={"error": str(e)},
                        exc_info=True
                    )
                return default_return
        return wrapper
    return decorator


def validate_input(**validators):
    """
    Decorator to validate function inputs.

    Example:
        @validate_input(image=lambda x: x is not None, scale=lambda x: x > 0)
        def upscale(image, scale):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Invalid value for parameter '{param_name}': {value}"
                        )

            return func(*args, **kwargs)
        return wrapper
    return decorator


def deprecated(reason: str):
    """
    Decorator to mark functions as deprecated.

    Args:
        reason: Explanation of why function is deprecated and what to use instead
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.warning(
                f"{func.__name__} is deprecated",
                context={"reason": reason}
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def singleton(cls):
    """
    Decorator to make a class a singleton.
    """
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
