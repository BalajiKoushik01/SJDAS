"""
Advanced Grid System for SJ-DAS.

Photoshop-style grid with customizable size, color, and snap-to-grid functionality.
"""

import logging

from PyQt6.QtCore import QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (QCheckBox, QColorDialog, QComboBox, QDialog,
                             QHBoxLayout, QLabel, QPushButton, QSpinBox,
                             QVBoxLayout, QWidget)

logger = logging.getLogger("SJ_DAS.GridSystem")


class GridSettings:
    """Grid configuration settings."""

    def __init__(self):
        self.enabled = False
        self.snap_to_grid = False
        self.grid_size = 32  # pixels
        self.grid_color = QColor(128, 128, 128, 100)  # Semi-transparent gray
        self.grid_style = Qt.PenStyle.DotLine  # Dotted, Dashed, Solid
        self.show_rulers = True
        self.subdivisions = 4  # Minor grid lines


class GridDialog(QDialog):
    """Dialog for configuring grid settings."""

    settings_changed = pyqtSignal(GridSettings)

    def __init__(self, current_settings: GridSettings, parent=None):
        super().__init__(parent)
        self.settings = current_settings
        self.setWindowTitle("Grid Settings")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Enable grid checkbox
        self.enable_checkbox = QCheckBox("Show Grid")
        self.enable_checkbox.setChecked(self.settings.enabled)
        layout.addWidget(self.enable_checkbox)

        # Grid size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Grid Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 256)  # 1px to 256px for maximum flexibility
        self.size_spin.setValue(self.settings.grid_size)
        self.size_spin.setSuffix(" px")
        size_layout.addWidget(self.size_spin)
        layout.addLayout(size_layout)

        # Subdivisions
        subdiv_layout = QHBoxLayout()
        subdiv_layout.addWidget(QLabel("Subdivisions:"))
        self.subdiv_spin = QSpinBox()
        self.subdiv_spin.setRange(0, 16)
        self.subdiv_spin.setValue(self.settings.subdivisions)
        subdiv_layout.addWidget(self.subdiv_spin)
        layout.addLayout(subdiv_layout)

        # Grid style
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Grid Style:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(
            ["Solid Lines", "Dotted Lines", "Dashed Lines"])
        style_layout.addWidget(self.style_combo)
        layout.addLayout(style_layout)

        # Grid color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Grid Color:"))
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        layout.addLayout(color_layout)

        # Snap to grid
        self.snap_checkbox = QCheckBox("Snap to Grid")
        self.snap_checkbox.setChecked(self.settings.snap_to_grid)
        layout.addWidget(self.snap_checkbox)

        # Show rulers
        self.rulers_checkbox = QCheckBox("Show Rulers")
        self.rulers_checkbox.setChecked(self.settings.show_rulers)
        layout.addWidget(self.rulers_checkbox)

        # Preset buttons
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Presets:"))

        btn_1 = QPushButton("1px")
        btn_1.clicked.connect(lambda: self.size_spin.setValue(1))
        preset_layout.addWidget(btn_1)

        btn_2 = QPushButton("2px")
        btn_2.clicked.connect(lambda: self.size_spin.setValue(2))
        preset_layout.addWidget(btn_2)

        btn_8 = QPushButton("8px")
        btn_8.clicked.connect(lambda: self.size_spin.setValue(8))
        preset_layout.addWidget(btn_8)

        btn_16 = QPushButton("16px")
        btn_16.clicked.connect(lambda: self.size_spin.setValue(16))
        preset_layout.addWidget(btn_16)

        btn_32 = QPushButton("32px")
        btn_32.clicked.connect(lambda: self.size_spin.setValue(32))
        preset_layout.addWidget(btn_32)

        btn_64 = QPushButton("64px")
        btn_64.clicked.connect(lambda: self.size_spin.setValue(64))
        preset_layout.addWidget(btn_64)

        layout.addLayout(preset_layout)

        # OK/Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self.settings.grid_color, self)
        if color.isValid():
            self.settings.grid_color = color
            self.color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

    def accept(self):
        """Apply settings and close."""
        self.settings.enabled = self.enable_checkbox.isChecked()
        self.settings.grid_size = self.size_spin.value()
        self.settings.subdivisions = self.subdiv_spin.value()
        self.settings.snap_to_grid = self.snap_checkbox.isChecked()
        self.settings.show_rulers = self.rulers_checkbox.isChecked()

        # Map style combo to Qt pen style
        style_map = {
            0: Qt.PenStyle.SolidLine,
            1: Qt.PenStyle.DotLine,
            2: Qt.PenStyle.DashLine
        }
        self.settings.grid_style = style_map[self.style_combo.currentIndex()]

        self.settings_changed.emit(self.settings)
        super().accept()


class GridOverlay(QWidget):
    """Grid overlay widget for canvas."""

    def __init__(self, settings: GridSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        """Draw grid overlay."""
        if not self.settings.enabled:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw major grid lines
        pen = QPen(self.settings.grid_color, 1, self.settings.grid_style)
        painter.setPen(pen)

        width = self.width()
        height = self.height()
        grid_size = self.settings.grid_size

        # Vertical lines
        x = 0
        while x < width:
            painter.drawLine(x, 0, x, height)
            x += grid_size

        # Horizontal lines
        y = 0
        while y < height:
            painter.drawLine(0, y, width, y)
            y += grid_size

        # Draw subdivisions if enabled
        if self.settings.subdivisions > 0:
            subdiv_size = grid_size / self.settings.subdivisions
            subdiv_color = QColor(self.settings.grid_color)
            subdiv_color.setAlpha(50)  # More transparent
            pen.setColor(subdiv_color)
            painter.setPen(pen)

            # Vertical subdivision lines
            x = subdiv_size
            while x < width:
                if x % grid_size != 0:  # Don't redraw major lines
                    painter.drawLine(int(x), 0, int(x), height)
                x += subdiv_size

            # Horizontal subdivision lines
            y = subdiv_size
            while y < height:
                if y % grid_size != 0:
                    painter.drawLine(0, int(y), width, int(y))
                y += subdiv_size

    def update_settings(self, settings: GridSettings):
        """Update grid settings and redraw."""
        self.settings = settings
        self.update()


class SnapToGrid:
    """Snap-to-grid functionality."""

    def __init__(self, settings: GridSettings):
        self.settings = settings

    def snap_point(self, x: int, y: int) -> tuple[int, int]:
        """
        Snap point to nearest grid intersection.

        Args:
            x, y: Original coordinates

        Returns:
            Snapped (x, y) coordinates
        """
        if not self.settings.snap_to_grid:
            return x, y

        grid_size = self.settings.grid_size

        snapped_x = round(x / grid_size) * grid_size
        snapped_y = round(y / grid_size) * grid_size

        return snapped_x, snapped_y

    def snap_rect(self, rect: QRect) -> QRect:
        """
        Snap rectangle to grid.

        Args:
            rect: Original rectangle

        Returns:
            Snapped rectangle
        """
        if not self.settings.snap_to_grid:
            return rect

        x1, y1 = self.snap_point(rect.x(), rect.y())
        x2, y2 = self.snap_point(rect.right(), rect.bottom())

        return QRect(x1, y1, x2 - x1, y2 - y1)


# Integration example
class GridManager:
    """Manages grid system for editor."""

    def __init__(self, editor_widget):
        self.editor = editor_widget
        self.settings = GridSettings()
        self.overlay = GridOverlay(self.settings, editor_widget)
        self.snap = SnapToGrid(self.settings)

        # Position overlay
        self.overlay.setGeometry(editor_widget.rect())
        self.overlay.show()

    def show_settings_dialog(self):
        """Show grid settings dialog."""
        dialog = GridDialog(self.settings, self.editor)
        dialog.settings_changed.connect(self.update_settings)
        dialog.exec()

    def update_settings(self, settings: GridSettings):
        """Update grid settings."""
        self.settings = settings
        self.overlay.update_settings(settings)
        self.snap.settings = settings
        logger.info(
            f"Grid updated: size={settings.grid_size}px, snap={settings.snap_to_grid}")

    def toggle_grid(self):
        """Toggle grid visibility."""
        self.settings.enabled = not self.settings.enabled
        self.overlay.update()

    def toggle_snap(self):
        """Toggle snap to grid."""
        self.settings.snap_to_grid = not self.settings.snap_to_grid
        logger.info(f"Snap to grid: {self.settings.snap_to_grid}")
