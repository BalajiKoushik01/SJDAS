
import functools
import logging
import traceback
from collections.abc import Callable
from typing import Any

from PyQt6.QtWidgets import QApplication, QMessageBox

logger = logging.getLogger("SJ_DAS.Infrastructure")


def safe_slot(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for PyQt Slots to catch unhandled exceptions gracefully.
    Prevents the entire application from crashing due to a single button click error.

    Usage:
        @safe_slot
        def on_button_clicked(self):
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 1. Log the full traceback
            tb_str = traceback.format_exc()
            logger.error(f"UI Error in {func.__name__}: {e}\n{tb_str}")

            # 2. Notify the User (if GUI is active)
            if QApplication.instance():
                # Extract class name if possible (args[0] is usually self)
                parent = args[0] if args and hasattr(args[0], 'show') else None

                msg = QMessageBox(parent)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Feature Error")
                msg.setText(f"An error occurred in '{func.__name__}'.")
                msg.setInformativeText(
                    "The application remains stable, but this action could not complete.")
                msg.setDetailedText(tb_str)
                msg.exec()
            return None
    return wrapper


def log_lifecycle(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to log entry/exit of complex methods."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Entering {func.__name__}")
        res = func(*args, **kwargs)
        logger.debug(f"Exiting {func.__name__}")
        return res
    return wrapper
