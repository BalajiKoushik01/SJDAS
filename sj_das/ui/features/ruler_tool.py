import math

import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class RulerTool:
    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        img_cv = self._get_cv_img()
        dialog = RulerDialog(img_cv, self.editor)
        dialog.exec()

    def _get_cv_img(self):
        qimg = self.editor.get_image()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)


class RulerCanvas(QLabel):
    def __init__(self, img_q, parent=None):
        super().__init__(parent)
        self.original_pixmap = QPixmap.fromImage(img_q)
        w, h = self.original_pixmap.width(), self.original_pixmap.height()

        # Scale for display
        scale_w = 800 / w if w > 800 else 1.0
        scale_h = 600 / h if h > 600 else 1.0
        self.scale = min(scale_w, scale_h)
        if self.scale < 1.0:
            self.display_pixmap = self.original_pixmap.scaled(
                int(w * self.scale), int(h * self.scale), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.display_pixmap = self.original_pixmap

        self.setPixmap(self.display_pixmap)

        self.start_pt = None
        self.end_pt = None
        self.is_dragging = False

    def mousePressEvent(self, event):
        self.start_pt = event.pos()
        self.end_pt = event.pos()
        self.is_dragging = True
        self.update()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.end_pt = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        self.end_pt = event.pos()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.start_pt or not self.end_pt:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Line
        pen = QPen(Qt.GlobalColor.yellow, 2)
        painter.setPen(pen)
        painter.drawLine(self.start_pt, self.end_pt)

        # Calculations
        real_scale = 1.0 / self.scale if self.scale > 0 else 1.0

        dx = (self.end_pt.x() - self.start_pt.x()) * real_scale
        dy = (self.end_pt.y() - self.start_pt.y()) * real_scale
        dist = math.sqrt(dx * dx + dy * dy)
        angle = math.degrees(math.atan2(dy, dx))

        # Draw Text Background
        info = f"Len: {dist:.1f} px | Ang: {angle:.1f}°"

        mid_x = (self.start_pt.x() + self.end_pt.x()) / 2
        mid_y = (self.start_pt.y() + self.end_pt.y()) / 2

        painter.setBrush(QColor(0, 0, 0, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(int(mid_x), int(mid_y - 20), 160, 25)

        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(int(mid_x + 5), int(mid_y - 3), info)


class RulerDialog(QDialog):
    def __init__(self, cv_img, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Measurement Tool")

        # Convert CV to QImage for display
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bpl = ch * w
        qimg = QImage(rgb.data, w, h, bpl, QImage.Format.Format_RGB888)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Click and drag to measure:"))

        self.canvas = RulerCanvas(qimg)
        layout.addWidget(self.canvas)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
