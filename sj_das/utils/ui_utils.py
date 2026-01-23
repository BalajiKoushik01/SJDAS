"""
UI utility functions for SJ-DAS.

Provides common UI patterns and helpers to reduce code duplication
and ensure consistent user experience across the application.
"""

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QWidget
from qfluentwidgets import InfoBar, InfoBarPosition


def show_error(
    parent: QWidget,
    title: str,
    message: str,
    duration: int = 3000,
    position: InfoBarPosition = InfoBarPosition.TOP
) -> None:
    """
    Show error notification.

    Args:
        parent: Parent widget
        title: Error title
        message: Error message
        duration: Display duration in milliseconds
        position: Position on screen
    """
    InfoBar.error(
        title=title,
        content=message,
        parent=parent,
        duration=duration,
        position=position
    )


def show_success(
    parent: QWidget,
    title: str,
    message: str,
    duration: int = 2000,
    position: InfoBarPosition = InfoBarPosition.TOP
) -> None:
    """
    Show success notification.

    Args:
        parent: Parent widget
        title: Success title
        message: Success message
        duration: Display duration in milliseconds
        position: Position on screen
    """
    InfoBar.success(
        title=title,
        content=message,
        parent=parent,
        duration=duration,
        position=position
    )


def show_warning(
    parent: QWidget,
    title: str,
    message: str,
    duration: int = 3000,
    position: InfoBarPosition = InfoBarPosition.TOP
) -> None:
    """
    Show warning notification.

    Args:
        parent: Parent widget
        title: Warning title
        message: Warning message
        duration: Display duration in milliseconds
        position: Position on screen
    """
    InfoBar.warning(
        title=title,
        content=message,
        parent=parent,
        duration=duration,
        position=position
    )


def show_info(
    parent: QWidget,
    title: str,
    message: str,
    duration: int = 2000,
    position: InfoBarPosition = InfoBarPosition.TOP
) -> None:
    """
    Show info notification.

    Args:
        parent: Parent widget
        title: Info title
        message: Info message
        duration: Display duration in milliseconds
        position: Position on screen
    """
    InfoBar.info(
        title=title,
        content=message,
        parent=parent,
        duration=duration,
        position=position
    )


def show_progress(
    parent: QWidget,
    title: str,
    max_value: int,
    cancel_button_text: Optional[str] = None
) -> QProgressDialog:
    """
    Create and show progress dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        max_value: Maximum progress value
        cancel_button_text: Cancel button text (None to hide)

    Returns:
        QProgressDialog instance
    """
    progress = QProgressDialog(title, cancel_button_text, 0, max_value, parent)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.setMinimumDuration(0)
    progress.show()
    return progress


def confirm_action(
    parent: QWidget,
    title: str,
    message: str,
    default_yes: bool = False
) -> bool:
    """
    Show confirmation dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        message: Confirmation message
        default_yes: Whether Yes is the default button

    Returns:
        True if user confirmed, False otherwise
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )

    if default_yes:
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
    else:
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

    result = msg_box.exec()
    return result == QMessageBox.StandardButton.Yes


def show_question(
    parent: QWidget,
    title: str,
    message: str,
    buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
) -> QMessageBox.StandardButton:
    """
    Show question dialog with custom buttons.

    Args:
        parent: Parent widget
        title: Dialog title
        message: Question message
        buttons: Standard buttons to show

    Returns:
        Button that was clicked
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(buttons)

    return msg_box.exec()
