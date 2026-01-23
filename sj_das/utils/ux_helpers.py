"""
UX Enhancement Utilities for SJ-DAS
Provides loading indicators, progress bars, and user feedback
"""
from typing import Callable, Optional

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QToolTip

from sj_das.utils.enhanced_logger import get_logger

logger = get_logger(__name__)


class LoadingIndicator(QProgressDialog):
    """
    Loading indicator for long operations.

    Features:
    - Customizable message
    - Cancellable operations
    - Auto-hide on completion
    """

    def __init__(self, message: str = "Processing...", parent=None):
        """
        Initialize loading indicator.

        Args:
            message: Message to display
            parent: Parent widget
        """
        super().__init__(message, "Cancel", 0, 0, parent)
        self.setWindowTitle("Please Wait")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumDuration(500)  # Only show if operation takes >500ms
        self.setAutoClose(True)
        self.setAutoReset(True)

        logger.debug(f"LoadingIndicator created: {message}")

    def update_message(self, message: str):
        """Update the loading message."""
        self.setLabelText(message)


class ProgressTracker(QObject):
    """
    Progress tracker for long-running operations.

    Features:
    - Progress updates
    - Estimated time remaining
    - Cancellation support
    """

    progress_updated = pyqtSignal(int, str)  # (percentage, message)

    def __init__(self, total_steps: int, operation_name: str = "Operation"):
        """
        Initialize progress tracker.

        Args:
            total_steps: Total number of steps
            operation_name: Name of the operation
        """
        super().__init__()
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = operation_name
        self.cancelled = False

        logger.info(
            f"ProgressTracker initialized: {operation_name} ({total_steps} steps)")

    def update(self, step: int, message: str = ""):
        """
        Update progress.

        Args:
            step: Current step number
            message: Optional status message
        """
        self.current_step = step
        percentage = int((step / self.total_steps) * 100)

        if not message:
            message = f"{self.operation_name}: Step {step}/{self.total_steps}"

        self.progress_updated.emit(percentage, message)
        logger.debug(f"Progress: {percentage}% - {message}")

    def increment(self, message: str = ""):
        """Increment progress by one step."""
        self.update(self.current_step + 1, message)

    def cancel(self):
        """Cancel the operation."""
        self.cancelled = True
        logger.info(f"Operation cancelled: {self.operation_name}")


class TooltipManager:
    """
    Manages tooltips for UI elements.

    Features:
    - Rich text tooltips
    - Keyboard shortcut hints
    - Contextual help
    """

    @staticmethod
    def set_tooltip(widget, text: str, shortcut: Optional[str] = None):
        """
        Set tooltip for a widget.

        Args:
            widget: Widget to add tooltip to
            text: Tooltip text
            shortcut: Optional keyboard shortcut
        """
        if shortcut:
            tooltip = f"{text}\n<i>Shortcut: {shortcut}</i>"
        else:
            tooltip = text

        widget.setToolTip(tooltip)
        logger.debug(f"Tooltip set: {text[:50]}...")

    @staticmethod
    def show_tooltip(text: str, duration: int = 3000):
        """
        Show a temporary tooltip at cursor position.

        Args:
            text: Tooltip text
            duration: Duration in milliseconds
        """
        QToolTip.showText(QCursor.pos(), text)
        QTimer.singleShot(duration, QToolTip.hideText)


class AutoSaveManager(QObject):
    """
    Manages auto-save functionality.

    Features:
    - Periodic auto-save
    - Configurable interval
    - Save on idle
    """

    auto_save_triggered = pyqtSignal()

    def __init__(self, interval_minutes: int = 5):
        """
        Initialize auto-save manager.

        Args:
            interval_minutes: Auto-save interval in minutes
        """
        super().__init__()
        self.interval = interval_minutes * 60 * 1000  # Convert to milliseconds
        self.timer = QTimer()
        self.timer.timeout.connect(self._trigger_save)
        self.enabled = False

        logger.info(
            f"AutoSaveManager initialized (interval: {interval_minutes} min)")

    def start(self):
        """Start auto-save timer."""
        self.timer.start(self.interval)
        self.enabled = True
        logger.info("Auto-save started")

    def stop(self):
        """Stop auto-save timer."""
        self.timer.stop()
        self.enabled = False
        logger.info("Auto-save stopped")

    def _trigger_save(self):
        """Trigger auto-save."""
        logger.info("Auto-save triggered")
        self.auto_save_triggered.emit()

    def reset_timer(self):
        """Reset the auto-save timer."""
        if self.enabled:
            self.timer.stop()
            self.timer.start(self.interval)


class NotificationManager:
    """
    Manages user notifications.

    Features:
    - Success notifications
    - Warning notifications
    - Error notifications
    """

    @staticmethod
    def show_success(message: str, title: str = "Success", parent=None):
        """Show success notification."""
        QMessageBox.information(parent, title, message)
        logger.info(f"Success notification: {message}")

    @staticmethod
    def show_warning(message: str, title: str = "Warning", parent=None):
        """Show warning notification."""
        QMessageBox.warning(parent, title, message)
        logger.warning(f"Warning notification: {message}")

    @staticmethod
    def show_error(message: str, title: str = "Error", parent=None):
        """Show error notification."""
        QMessageBox.critical(parent, title, message)
        logger.error(f"Error notification: {message}")

    @staticmethod
    def ask_confirmation(
            message: str, title: str = "Confirm", parent=None) -> bool:
        """
        Ask for user confirmation.

        Returns:
            True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            parent, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes


# Decorator for long operations
def with_loading_indicator(message: str = "Processing..."):
    """
    Decorator to show loading indicator during operation.

    Usage:
        @with_loading_indicator("Quantizing image...")
        def quantize_image(self, image):
            # ... long operation
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Create loading indicator
            indicator = LoadingIndicator(
                message, getattr(self, 'parent', None))
            indicator.show()

            try:
                # Execute operation
                result = func(self, *args, **kwargs)
                return result
            finally:
                # Hide indicator
                indicator.close()

        return wrapper
    return decorator


# Global instances
_auto_save_manager: Optional[AutoSaveManager] = None


def get_auto_save_manager(interval_minutes: int = 5) -> AutoSaveManager:
    """
    Get global auto-save manager.

    Args:
        interval_minutes: Auto-save interval (only used on first call)

    Returns:
        Global AutoSaveManager instance
    """
    global _auto_save_manager
    if _auto_save_manager is None:
        _auto_save_manager = AutoSaveManager(interval_minutes)
    return _auto_save_manager
