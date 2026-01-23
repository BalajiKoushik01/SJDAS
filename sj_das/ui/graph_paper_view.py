"""Graph Paper View Mode for Jacquard Design.

Traditional jacquard graph paper representation where each pixel is a distinct square.
"""

import numpy as np
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QSpinBox,
                             QVBoxLayout, QWidget)


class GraphPaperView(QWidget):
    """
    Jacquard-style graph paper view.

    Features:
    - Each pixel shown as distinct square
    - Grid always visible
    - Zoom to see individual squares clearly
    - Optional: Show weave symbols in squares
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_data = None
        self.cell_size = 20  # Size of each square in pixels
        self.show_grid = True
        self.show_coordinates = True
        self.grid_color = QColor(150, 150, 150)
        self.background_color = QColor(255, 255, 255)

        self._init_ui()

    def _init_ui(self):
        """Initialize UI controls."""
        layout = QVBoxLayout(self)

        # Controls
        controls = QHBoxLayout()

        # Cell size control
        controls.addWidget(QLabel("Square Size:"))
        self.spin_cell_size = QSpinBox()
        self.spin_cell_size.setRange(5, 50)
        self.spin_cell_size.setValue(self.cell_size)
        self.spin_cell_size.setSuffix(" px")
        self.spin_cell_size.valueChanged.connect(self._on_cell_size_changed)
        controls.addWidget(self.spin_cell_size)

        controls.addSpacing(20)

        # Grid toggle
        self.chk_grid = QCheckBox("Show Grid")
        self.chk_grid.setChecked(True)
        self.chk_grid.stateChanged.connect(self._on_grid_toggled)
        controls.addWidget(self.chk_grid)

        # Coordinates toggle
        self.chk_coords = QCheckBox("Show Coordinates")
        self.chk_coords.setChecked(True)
        self.chk_coords.stateChanged.connect(self.update)
        controls.addWidget(self.chk_coords)

        controls.addStretch()

        layout.addLayout(controls)

    def set_image_data(self, image: np.ndarray):
        """
        Set image data to display as graph.

        Args:
            image: numpy array (H, W, 3) or (H, W)
        """
        self.image_data = image
        self.update()

    def paintEvent(self, event):
        """Draw graph paper view."""
        if self.image_data is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            False)  # Crisp pixels

        # Fill background
        painter.fillRect(self.rect(), self.background_color)

        # Get image dimensions
        if len(self.image_data.shape) == 3:
            h, w, _ = self.image_data.shape
        else:
            h, w = self.image_data.shape

        # Draw cells
        for y in range(h):
            for x in range(w):
                # Get pixel color
                if len(self.image_data.shape) == 3:
                    b, g, r = self.image_data[y, x]
                    color = QColor(r, g, b)
                else:
                    val = self.image_data[y, x]
                    color = QColor(val, val, val)

                # Draw cell
                cell_rect = QRectF(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

                painter.fillRect(cell_rect, color)

        # Draw grid
        if self.show_grid:
            pen = QPen(self.grid_color)
            pen.setWidth(1)
            painter.setPen(pen)

            # Vertical lines (hooks)
            for x in range(w + 1):
                x_pos = x * self.cell_size
                painter.drawLine(x_pos, 0, x_pos, h * self.cell_size)

            # Horizontal lines (picks)
            for y in range(h + 1):
                y_pos = y * self.cell_size
                painter.drawLine(0, y_pos, w * self.cell_size, y_pos)

        # Draw coordinates
        if self.show_coordinates and self.chk_coords.isChecked():
            painter.setPen(QColor(0, 0, 0))
            font = painter.font()
            font.setPixelSize(max(8, self.cell_size // 3))
            painter.setFont(font)

            # Draw hook numbers (top)
            for x in range(0, w, max(1, 50 // self.cell_size)):
                painter.drawText(
                    x * self.cell_size + 2,
                    -2,
                    f"{x}"
                )

            # Draw pick numbers (left)
            for y in range(0, h, max(1, 50 // self.cell_size)):
                painter.drawText(
                    2,
                    y * self.cell_size + font.pixelSize(),
                    f"{y}"
                )

    def _on_cell_size_changed(self, value):
        """Handle cell size change."""
        self.cell_size = value
        self.update()

    def _on_grid_toggled(self, state):
        """Handle grid toggle."""
        self.show_grid = (state == Qt.CheckState.Checked.value)
        self.update()

    def sizeHint(self):
        """Suggest size based on image."""
        if self.image_data is None:
            return super().sizeHint()

        if len(self.image_data.shape) == 3:
            h, w, _ = self.image_data.shape
        else:
            h, w = self.image_data.shape

        from PyQt6.QtCore import QSize
        return QSize(w * self.cell_size, h * self.cell_size)
