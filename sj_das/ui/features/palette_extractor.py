import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QDialog, QGridLayout, QLabel,
                             QPushButton, QVBoxLayout)


class PaletteExtractor:
    """
    Module for Extracting Dominant Colors.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        img_cv = self._get_cv_img()
        # Analyze
        colors = self._extract_colors(img_cv, k=8)

        dialog = PaletteDialog(colors)
        dialog.exec()

    def _extract_colors(self, img, k=8):
        # Flatten
        pixels = np.float32(img.reshape(-1, 3))
        # K-Means
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(
            pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Convert to int
        centers = np.uint8(centers)  # BGR
        return centers

    def _get_cv_img(self):
        qimg = self.editor.get_image()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)


class PaletteDialog(QDialog):
    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dominant Palette")
        self.resize(300, 200)
        self.colors = colors  # BGR
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Click color to copy Hex:"))

        grid = QGridLayout()

        for i, c in enumerate(self.colors):
            b, g, r = c
            hex_code = f"#{r:02x}{g:02x}{b:02x}".upper()

            btn = QPushButton(hex_code)
            btn.setStyleSheet(
                f"background-color: {hex_code}; color: {'black' if (r+g+b)/3 > 128 else 'white'}; font-weight: bold;")
            btn.setMinimumHeight(40)
            btn.clicked.connect(
                lambda checked,
                h=hex_code: self.copy_to_clipboard(h))

            row = i // 2
            col = i % 2
            grid.addWidget(btn, row, col)

        layout.addLayout(grid)

    def copy_to_clipboard(self, hex_code):
        QApplication.clipboard().setText(hex_code)
        # Maybe show toast?
