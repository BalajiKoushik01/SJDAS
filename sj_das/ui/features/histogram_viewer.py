import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPainter
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget


class HistogramViewer:
    """
    Module for Real-Time Histogram Visualization.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        """Shows histogram dialog"""
        img = self._get_cv_img()
        dialog = HistogramDialog(img, self.editor)
        dialog.exec()

    def _get_cv_img(self):
        qimg = self.editor.get_image()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)


class HistogramWidget(QWidget):
    def __init__(self, img):
        super().__init__()
        self.img = img
        self.setMinimumSize(300, 200)
        self.calc_hist()

    def calc_hist(self):
        # Calculate histograms
        self.hist_b = cv2.calcHist([self.img], [0], None, [256], [0, 256])
        self.hist_g = cv2.calcHist([self.img], [1], None, [256], [0, 256])
        self.hist_r = cv2.calcHist([self.img], [2], None, [256], [0, 256])

        # Normalize
        cv2.normalize(self.hist_b, self.hist_b, 0, 180, cv2.NORM_MINMAX)
        cv2.normalize(self.hist_g, self.hist_g, 0, 180, cv2.NORM_MINMAX)
        cv2.normalize(self.hist_r, self.hist_r, 0, 180, cv2.NORM_MINMAX)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(40, 40, 40))

        w = self.width()
        h = self.height()
        bin_w = w / 256

        # Draw Channels
        self._draw_channel(
            painter, self.hist_r, QColor(
                255, 50, 50, 150), bin_w, h)
        self._draw_channel(
            painter, self.hist_g, QColor(
                50, 255, 50, 150), bin_w, h)
        self._draw_channel(
            painter, self.hist_b, QColor(
                50, 50, 255, 150), bin_w, h)

    def _draw_channel(self, painter, hist, color, bin_w, h):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))

        for i in range(256):
            val = hist[i][0]
            # Height is from bottom
            painter.drawRect(int(i * bin_w), int(h - val),
                             int(bin_w) + 1, int(val))


class HistogramDialog(QDialog):
    def __init__(self, img, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pro Histogram")
        self.resize(320, 240)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("RGB Channels Distribution"))
        self.hist_widget = HistogramWidget(img)
        layout.addWidget(self.hist_widget)
