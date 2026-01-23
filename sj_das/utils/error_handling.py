"""
Error Handling Utilities for SJ-DAS
Provides decorators and helpers for consistent error handling
"""
import functools
import logging
from typing import Any, Callable

from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger("SJ_DAS.ErrorHandling")


def handle_errors(user_message: str = "An error occurred",
                  log_error: bool = True,
                  show_dialog: bool = True):
    """
    Decorator for consistent error handling across the application.

    Args:
        user_message: User-friendly error message to display
        log_error: Whether to log the error
        show_dialog: Whether to show error dialog to user

    Usage:
        @handle_errors("Failed to load AI model")
        def load_model(self):
            # ... code that might fail
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                error_msg = f"File not found: {e}"
                if log_error:
                    logger.error(f"{func.__name__}: {error_msg}")
                if show_dialog:
                    show_error_message(
                        "File Not Found",
                        f"{user_message}\n\nThe requested file could not be found."
                    )
                return None
            except PermissionError as e:
                error_msg = f"Permission denied: {e}"
                if log_error:
                    logger.error(f"{func.__name__}: {error_msg}")
                if show_dialog:
                    show_error_message(
                        "Permission Denied",
                        f"{user_message}\n\nPlease check file permissions."
                    )
                return None
            except Exception as e:
                error_msg = f"Unexpected error: {type(e).__name__}: {e}"
                if log_error:
                    logger.error(
                        f"{func.__name__}: {error_msg}",
                        exc_info=True)
                if show_dialog:
                    show_error_message(
                        "Error",
                        f"{user_message}\n\nDetails: {str(e)}"
                    )
                return None
        return wrapper
    return decorator


def handle_ai_errors(func: Callable) -> Callable:
    """
    Specialized decorator for AI feature error handling.
    Provides user-friendly messages for common AI-related errors.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            logger.warning(f"{func.__name__}: AI model not found")
            show_info_message(
                "AI Model Not Available",
                "This feature requires an AI model to be downloaded.\n\n"
                "Please check Settings > AI Models to download the required model."
            )
            return None
        except ImportError as e:
            logger.error(f"{func.__name__}: Missing AI dependency: {e}")
            show_error_message(
                "Missing Dependency",
                "This AI feature requires additional dependencies.\n\n"
                "Please check the installation guide."
            )
            return None
        except RuntimeError as e:
            if "CUDA" in str(e) or "GPU" in str(e):
                logger.warning(
                    f"{func.__name__}: GPU not available, falling back to CPU")
                show_info_message(
                    "GPU Not Available",
                    "GPU acceleration is not available. Using CPU instead.\n\n"
                    "This may be slower but will still work."
                )
                # Retry with CPU
                return None
            else:
                logger.error(f"{func.__name__}: {e}", exc_info=True)
                show_error_message(
                    "AI Error", f"AI processing failed: {str(e)}")
                return None
        except Exception as e:
            logger.error(
                f"{func.__name__}: Unexpected AI error: {e}",
                exc_info=True)
            show_error_message(
                "AI Processing Error",
                f"An unexpected error occurred during AI processing.\n\nDetails: {str(e)}"
            )
            return None
    return wrapper


def show_error_message(title: str, message: str):
    """Show error message dialog to user."""
    try:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except BaseException:
        # Fallback if Qt dialog fails
        logger.error(f"{title}: {message}")


def show_info_message(title: str, message: str):
    """Show informational message dialog to user."""
    try:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except BaseException:
        # Fallback if Qt dialog fails
        logger.info(f"{title}: {message}")


def show_warning_message(title: str, message: str):
    """Show warning message dialog to user."""
    try:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except BaseException:
        # Fallback if Qt dialog fails
        logger.warning(f"{title}: {message}")
