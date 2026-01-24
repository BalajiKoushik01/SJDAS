"""
Advanced status bar with progress tracking and contextual information.

Provides a professional status bar similar to Adobe Creative Suite,
with tool info, progress indicators, and clickable status elements.
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QMenu, QProgressBar,
                             QPushButton, QStatusBar, QWidget)

logger = logging.getLogger("SJ_DAS.AdvancedStatusBar")


class ClickableLabel(QLabel):
    """Label that emits clicked signal."""
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class AdvancedStatusBar(QStatusBar):
    """
    Professional status bar with multiple sections and progress tracking.

    Features:
        - Tool information display
        - Selection and canvas info
        - Progress bar for long operations
        - Clickable zoom control
        - Memory usage indicator
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_operation = None

    def setup_ui(self):
        """Setup status bar sections."""
        # Left section: Tool info (compact)
        self.tool_icon_label = QLabel()
        self.tool_name_label = QLabel("Ready")
        self.tool_name_label.setStyleSheet(
            "color: #E2E8F0; font-weight: 500; font-size: 12px;")

        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(6, 0, 6, 0)  # Reduced from 8
        left_layout.setSpacing(6)  # Reduced from 8
        left_layout.addWidget(self.tool_icon_label)
        left_layout.addWidget(self.tool_name_label)
        left_layout.addStretch()

        self.addWidget(left_widget, 1)

        # Center section: Progress bar (hidden by default)
        self.progress_widget = QWidget()
        progress_layout = QHBoxLayout(self.progress_widget)
        progress_layout.setContentsMargins(4, 0, 4, 0)
        progress_layout.setSpacing(8)

        self.progress_label = QLabel()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(180)  # Reduced from 200
        self.progress_bar.setMaximumHeight(18)  # Compact height
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #475569;
                border-radius: 3px;
                background-color: #1E293B;
                text-align: center;
                color: #E2E8F0;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background-color: #6366F1;
                border-radius: 2px;
            }
        """)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMaximumWidth(60)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 2px 8px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.cancel_button)

        self.progress_widget.setVisible(False)
        self.addPermanentWidget(self.progress_widget)

        # Right section: Canvas info (compact)
        self.selection_label = QLabel()
        self.selection_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self.addPermanentWidget(self.selection_label)

        self.canvas_label = QLabel("Canvas: 1000×1000")
        self.canvas_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self.addPermanentWidget(self.canvas_label)

        # Clickable zoom control (compact)
        self.zoom_label = ClickableLabel("100%")
        self.zoom_label.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                padding: 1px 6px;
                border-radius: 3px;
                font-size: 11px;
            }
            QLabel:hover {
                background-color: #334155;
            }
        """)
        self.zoom_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.zoom_label.clicked.connect(self.show_zoom_menu)
        self.addPermanentWidget(self.zoom_label)

        # Memory indicator (compact)
        self.memory_label = QLabel("RAM: 150MB")
        self.memory_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self.addPermanentWidget(self.memory_label)

        # Make status bar more compact and floating style
        self.setMaximumHeight(36)
        
        # Transparent background for floating effect (handled by MainWindow containerusually, 
        # but here we style the content widgets to look like pills)
        self.setStyleSheet("QStatusBar { background: transparent; border: none; }")

        # Style individual sections as capsules if needed, or keeping it clean flat
        self.tool_name_label.setStyleSheet("""
            background-color: #334155; 
            color: #F8FAFC; 
            padding: 4px 12px; 
            border-radius: 12px;
            font-weight: 600;
            font-size: 11px;
        """)

    def set_tool_info(self, tool_name: str, icon=None):
        """Update tool information display."""
        self.tool_name_label.setText(tool_name)
        if icon:
            # Set icon if provided
            pass

    def set_selection_info(self, width: int = 0,
                           height: int = 0, x: int = 0, y: int = 0):
        """Update selection information."""
        if width > 0 and height > 0:
            self.selection_label.setText(
                f"Selection: {width}×{height} at ({x}, {y})")
            self.selection_label.setVisible(True)
        else:
            self.selection_label.setVisible(False)

    def set_canvas_info(self, width: int, height: int):
        """Update canvas dimensions display."""
        self.canvas_label.setText(f"Canvas: {width}×{height}")

    def set_zoom_level(self, zoom: float):
        """Update zoom level display."""
        self.zoom_label.setText(f"{int(zoom * 100)}%")

    def show_zoom_menu(self):
        """Show zoom preset menu."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E293B;
                color: #E2E8F0;
                border: 1px solid #475569;
            }
            QMenu::item:selected {
                background-color: #334155;
            }
        """)

        zoom_levels = [
            ("Fit to Window", "Ctrl+0", 0),
            ("100%", "Ctrl+1", 1.0),
            ("200%", "", 2.0),
            ("400%", "", 4.0),
            ("---", "", None),
            ("50%", "", 0.5),
            ("25%", "", 0.25),
        ]

        for label, shortcut, zoom in zoom_levels:
            if label == "---":
                menu.addSeparator()
            else:
                action = menu.addAction(
                    f"{label}  {shortcut}" if shortcut else label)
                if zoom is not None:
                    action.triggered.connect(
                        lambda checked, z=zoom: self.zoom_requested(z))

        menu.exec(QCursor.pos())

    def zoom_requested(self, zoom_level: float):
        """Emit zoom request (to be connected by parent)."""
        logger.info(f"Zoom requested: {zoom_level}")
        # Parent should connect to this

    def start_progress(self, operation_name: str,
                       maximum: int = 100, cancellable: bool = True):
        """
        Start showing progress for a long operation.

        Args:
            operation_name: Name of the operation
            maximum: Maximum progress value
            cancellable: Whether operation can be cancelled
        """
        self.current_operation = operation_name
        self.progress_label.setText(operation_name)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(0)
        self.cancel_button.setVisible(cancellable)
        self.progress_widget.setVisible(True)
        logger.info(f"Started progress: {operation_name}")

    def update_progress(self, value: int, status_text: str = ""):
        """Update progress bar value and optional status text."""
        self.progress_bar.setValue(value)
        if status_text:
            self.progress_label.setText(
                f"{self.current_operation}: {status_text}")

    def finish_progress(self, success: bool = True, message: str = ""):
        """
        Finish progress operation.

        Args:
            success: Whether operation succeeded
            message: Optional completion message
        """
        self.progress_widget.setVisible(False)
        if message:
            self.showMessage(message, 3000)
        elif success:
            self.showMessage(f"{self.current_operation} completed", 2000)
        else:
            self.showMessage(f"{self.current_operation} failed", 3000)

        self.current_operation = None
        logger.info(f"Finished progress: {message or 'completed'}")

    def update_memory_usage(self, mb: int):
        """Update memory usage display."""
        color = "#94A3B8"  # Normal
        if mb > 1000:
            color = "#F59E0B"  # Warning (>1GB)
        if mb > 2000:
            color = "#EF4444"  # Critical (>2GB)

        self.memory_label.setText(f"RAM: {mb}MB")
        self.memory_label.setStyleSheet(f"color: {color};")
