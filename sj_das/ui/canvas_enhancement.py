"""
Canvas Enhancement Module - Global Standard Implementation
Provides zoom controls, smooth rendering, rulers, and grid overlay
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPen
from PyQt6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QPushButton,
                             QSlider, QSpinBox, QWidget)


class ZoomControl(QWidget):
    """Professional zoom control widget with slider and presets."""

    zoom_changed = pyqtSignal(float)  # Emits zoom level (1.0 = 100%)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)

        # Zoom out button
        btn_zoom_out = QPushButton("−")
        btn_zoom_out.setFixedSize(24, 24)
        btn_zoom_out.clicked.connect(self.zoom_out)
        layout.addWidget(btn_zoom_out)

        # Zoom slider (10% to 500%)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(10)
        self.slider.setMaximum(500)
        self.slider.setValue(100)
        self.slider.setFixedWidth(150)
        self.slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.slider)

        # Zoom in button
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setFixedSize(24, 24)
        btn_zoom_in.clicked.connect(self.zoom_in)
        layout.addWidget(btn_zoom_in)

        # Zoom percentage display
        self.label = QLabel("100%")
        self.label.setMinimumWidth(50)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Preset buttons
        btn_fit = QPushButton("Fit")
        btn_fit.setToolTip("Fit to window")
        btn_fit.clicked.connect(self.fit_to_window)
        layout.addWidget(btn_fit)

        btn_actual = QPushButton("100%")
        btn_actual.setToolTip("Actual size")
        btn_actual.clicked.connect(self.actual_size)
        layout.addWidget(btn_actual)

        layout.addStretch()

    def on_slider_changed(self, value):
        self.label.setText(f"{value}%")
        self.zoom_changed.emit(value / 100.0)

    def zoom_in(self):
        current = self.slider.value()
        self.slider.setValue(min(500, current + 25))

    def zoom_out(self):
        current = self.slider.value()
        self.slider.setValue(max(10, current - 25))

    def fit_to_window(self):
        # This will be connected to canvas method
        pass

    def actual_size(self):
        self.slider.setValue(100)

    def set_zoom(self, zoom_level):
        """Set zoom level programmatically (1.0 = 100%)."""
        self.slider.setValue(int(zoom_level * 100))


class GridSettings(QWidget):
    """Grid and ruler settings widget."""

    grid_changed = pyqtSignal(bool, int, QColor)  # enabled, spacing, color
    rulers_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Rulers checkbox
        self.chk_rulers = QCheckBox("Rulers")
        self.chk_rulers.setChecked(True)
        self.chk_rulers.toggled.connect(self.on_rulers_changed)
        layout.addWidget(self.chk_rulers)

        # Grid checkbox
        self.chk_grid = QCheckBox("Grid")
        self.chk_grid.toggled.connect(self.on_grid_changed)
        layout.addWidget(self.chk_grid)

        # Grid spacing
        layout.addWidget(QLabel("Spacing:"))
        self.spin_spacing = QSpinBox()
        self.spin_spacing.setRange(5, 100)
        self.spin_spacing.setValue(20)
        self.spin_spacing.setSuffix(" px")
        self.spin_spacing.valueChanged.connect(self.on_grid_changed)
        layout.addWidget(self.spin_spacing)

        layout.addStretch()

    def on_rulers_changed(self, enabled):
        self.rulers_changed.emit(enabled)

    def on_grid_changed(self):
        enabled = self.chk_grid.isChecked()
        spacing = self.spin_spacing.value()
        color = QColor(100, 100, 100, 50)
        self.grid_changed.emit(enabled, spacing, color)


class CanvasRenderer:
    """Professional canvas rendering with checkerboard and smooth scaling."""

    @staticmethod
    def draw_checkerboard(painter, rect, cell_size=10):
        """Draw transparency checkerboard background."""
        painter.save()

        # Colors
        light = QColor(255, 255, 255)
        dark = QColor(204, 204, 204)

        x_start = int(rect.x() / cell_size) * cell_size
        y_start = int(rect.y() / cell_size) * cell_size

        for y in range(y_start, int(rect.bottom()) + cell_size, cell_size):
            for x in range(x_start, int(rect.right()) + cell_size, cell_size):
                # Checkerboard pattern
                is_dark = ((x // cell_size) + (y // cell_size)) % 2 == 0
                painter.fillRect(x, y, cell_size, cell_size,
                                 dark if is_dark else light)

        painter.restore()

    @staticmethod
    def draw_grid(painter, rect, spacing, color):
        """Draw grid overlay."""
        painter.save()

        pen = QPen(color)
        pen.setWidth(1)
        painter.setPen(pen)

        # Vertical lines
        x = int(rect.x() / spacing) * spacing
        while x <= rect.right():
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += spacing

        # Horizontal lines
        y = int(rect.y() / spacing) * spacing
        while y <= rect.bottom():
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += spacing

        painter.restore()

    @staticmethod
    def draw_rulers(painter, view_rect, ruler_size=20, zoom=1.0):
        """Draw horizontal and vertical rulers."""
        painter.save()

        # Ruler background
        ruler_bg = QColor(240, 240, 240)
        painter.fillRect(0, 0, int(view_rect.width()),
                         ruler_size, ruler_bg)  # Top
        painter.fillRect(
            0, 0, ruler_size, int(
                view_rect.height()), ruler_bg)  # Left

        # Ruler markings
        pen = QPen(QColor(100, 100, 100))
        painter.setPen(pen)
        font = QFont("Arial", 8)
        painter.setFont(font)

        # Determine tick spacing based on zoom
        base_spacing = 100  # pixels in image
        tick_spacing = base_spacing * zoom

        # Horizontal ruler
        x = ruler_size
        i = 0
        while x < view_rect.width():
            # Major tick
            painter.drawLine(int(x), ruler_size - 5, int(x), ruler_size)
            painter.drawText(int(x + 2), ruler_size - 7, str(i * base_spacing))

            # Minor ticks
            for j in range(1, 10):
                minor_x = x + (tick_spacing / 10 * j)
                if minor_x < view_rect.width():
                    tick_height = 3 if j == 5 else 2
                    painter.drawLine(
                        int(minor_x),
                        ruler_size -
                        tick_height,
                        int(minor_x),
                        ruler_size)

            x += tick_spacing
            i += 1

        # Vertical ruler
        y = ruler_size
        i = 0
        while y < view_rect.height():
            # Major tick
            painter.drawLine(ruler_size - 5, int(y), ruler_size, int(y))
            painter.save()
            painter.translate(5, int(y - 2))
            painter.rotate(-90)
            painter.drawText(0, 0, str(i * base_spacing))
            painter.restore()

            # Minor ticks
            for j in range(1, 10):
                minor_y = y + (tick_spacing / 10 * j)
                if minor_y < view_rect.height():
                    tick_height = 3 if j == 5 else 2
                    painter.drawLine(
                        ruler_size -
                        tick_height,
                        int(minor_y),
                        ruler_size,
                        int(minor_y))

            y += tick_spacing
            i += 1

        # Corner square
        painter.fillRect(0, 0, ruler_size, ruler_size, ruler_bg)

        painter.restore()
