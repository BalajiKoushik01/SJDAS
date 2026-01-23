"""
Drag-and-drop support for SJ-DAS.

Enables dragging files, colors, and other elements into the application
for quick import and manipulation.
"""

import logging
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QWidget

logger = logging.getLogger("SJ_DAS.DragDropMixin")


class DragDropMixin:
    """
    Mixin class to add drag-and-drop functionality to widgets.

    Features:
        - File import via drag-drop
        - Color swatch dragging
        - Layer reordering
        - Visual drop indicators
    """

    # Signals (must be defined in the actual widget class)
    # file_dropped = pyqtSignal(str)  # Emits file path
    # color_dropped = pyqtSignal(object)  # Emits QColor

    def enable_file_drop(self):
        """Enable file drag-and-drop."""
        self.setAcceptDrops(True)
        logger.debug(f"Enabled file drop for {self.__class__.__name__}")

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            # Check if any URLs are image files
            urls = event.mimeData().urls()
            for url in urls:
                path = Path(url.toLocalFile())
                if path.suffix.lower() in [
                        '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                    event.acceptProposedAction()
                    self._show_drop_indicator(True)
                    return

        if event.mimeData().hasColor():
            event.acceptProposedAction()
            self._show_drop_indicator(True)
            return

        event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        self._show_drop_indicator(False)

    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        self._show_drop_indicator(False)

        # Handle file drops
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                path = Path(file_path)

                if path.suffix.lower() in [
                        '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                    logger.info(f"File dropped: {file_path}")
                    if hasattr(self, 'file_dropped'):
                        self.file_dropped.emit(file_path)
                    event.acceptProposedAction()
                    return

        # Handle color drops
        if event.mimeData().hasColor():
            color = event.mimeData().colorData()
            logger.info(f"Color dropped: {color}")
            if hasattr(self, 'color_dropped'):
                self.color_dropped.emit(color)
            event.acceptProposedAction()
            return

        event.ignore()

    def _show_drop_indicator(self, show: bool):
        """Show/hide visual drop indicator."""
        if show:
            # Add visual feedback (border highlight)
            if hasattr(self, 'setStyleSheet'):
                current_style = self.styleSheet()
                if 'drop-indicator' not in current_style:
                    self.setProperty('drop-active', True)
                    self.style().unpolish(self)
                    self.style().polish(self)
        else:
            if hasattr(self, 'setStyleSheet'):
                self.setProperty('drop-active', False)
                self.style().unpolish(self)
                self.style().polish(self)


class DropZoneWidget(QWidget):
    """
    Dedicated drop zone widget for file import.

    Shows a prominent drop area when no image is loaded.
    """

    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setup_ui()

    def setup_ui(self):
        """Setup drop zone UI."""
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            DropZoneWidget {
                background-color: #1E293B;
                border: 3px dashed #475569;
                border-radius: 12px;
            }
            DropZoneWidget[drop-active="true"] {
                border-color: #6366F1;
                background-color: #334155;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                path = Path(url.toLocalFile())
                if path.suffix.lower() in [
                        '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                    event.acceptProposedAction()
                    self.setProperty('drop-active', True)
                    self.style().unpolish(self)
                    self.style().polish(self)
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self.setProperty('drop-active', False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        """Handle drop."""
        self.setProperty('drop-active', False)
        self.style().unpolish(self)
        self.style().polish(self)

        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                path = Path(file_path)

                if path.suffix.lower() in [
                        '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                    logger.info(f"File dropped on drop zone: {file_path}")
                    self.file_dropped.emit(file_path)
                    event.acceptProposedAction()
                    return

        event.ignore()
