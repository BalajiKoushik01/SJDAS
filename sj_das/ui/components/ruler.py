"""
Canvas Ruler Widget
Professional rulers for canvas like Photoshop/Figma
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class Ruler(QWidget):
    """Professional ruler widget"""

    HORIZONTAL = Qt.Orientation.Horizontal
    VERTICAL = Qt.Orientation.Vertical

    def __init__(self, orientation=HORIZONTAL, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.zoom = 1.0
        self.offset = 0

        # Set size
        if orientation == self.HORIZONTAL:
            self.setFixedHeight(25)
        else:
            self.setFixedWidth(25)

        # Colors
        self.bg_color = QColor("#252233")
        self.line_color = QColor("#3730A3")
        self.text_color = QColor("#94A3B8")
        self.major_line_color = QColor("#6366F1")

    def paintEvent(self, event):
        """Paint the ruler"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), self.bg_color)

        # Draw ruler markings
        if self.orientation == self.HORIZONTAL:
            self.draw_horizontal_ruler(painter)
        else:
            self.draw_vertical_ruler(painter)

    def draw_horizontal_ruler(self, painter):
        """Draw horizontal ruler"""
        width = self.width()
        height = self.height()

        # Font for numbers
        font = QFont("Inter", 9)
        painter.setFont(font)

        # Draw markings every 10 pixels (scaled)
        step = 50  # Base step in pixels
        scaled_step = step * self.zoom

        # Major marks every 100 pixels
        major_step = 100
        major_step * self.zoom

        x = self.offset
        counter = 0

        while x < width:
            if counter % 2 == 0:  # Major mark
                painter.setPen(QPen(self.major_line_color, 1))
                painter.drawLine(int(x), height - 10, int(x), height)

                # Draw number
                painter.setPen(self.text_color)
                painter.drawText(int(x) + 2, height - 12,
                                 str(int(counter * major_step)))
            else:  # Minor mark
                painter.setPen(QPen(self.line_color, 1))
                painter.drawLine(int(x), height - 6, int(x), height)

            x += scaled_step
            counter += 1

    def draw_vertical_ruler(self, painter):
        """Draw vertical ruler"""
        width = self.width()
        height = self.height()

        # Font for numbers
        font = QFont("Inter", 9)
        painter.setFont(font)

        # Draw markings every 50 pixels (scaled)
        step = 50  # Base step in pixels
        scaled_step = step * self.zoom

        # Major marks every 100 pixels
        major_step = 100
        major_step * self.zoom

        y = self.offset
        counter = 0

        while y < height:
            if counter % 2 == 0:  # Major mark
                painter.setPen(QPen(self.major_line_color, 1))
                painter.drawLine(width - 10, int(y), width, int(y))

                # Draw number (rotated)
                painter.save()
                painter.setPen(self.text_color)
                painter.translate(width - 12, int(y) - 2)
                painter.rotate(-90)
                painter.drawText(0, 0, str(int(counter * major_step)))
                painter.restore()
            else:  # Minor mark
                painter.setPen(QPen(self.line_color, 1))
                painter.drawLine(width - 6, int(y), width, int(y))

            y += scaled_step
            counter += 1

    def set_zoom(self, zoom):
        """Update zoom level"""
        self.zoom = zoom
        self.update()

    def set_offset(self, offset):
        """Update scroll offset"""
        self.offset = offset
        self.update()
