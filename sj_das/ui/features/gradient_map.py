import cv2
import numpy as np
from PyQt6.QtGui import QColor, QImage
from PyQt6.QtWidgets import (QColorDialog, QDialog, QDialogButtonBox,
                             QHBoxLayout, QLabel, QPushButton, QVBoxLayout)


class GradientMap:
    """
    Module for Gradient Mapping (Recoloring).
    Maps grayscale intensity to a 2-Color Gradient.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = GradientMapDialog(self.editor)
        if dialog.exec():
            c1, c2 = dialog.get_colors()
            self._apply_gradient(c1, c2)

    def _apply_gradient(self, c1, c2):
        img = self._get_cv_img()

        # 1. Convert to Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Generate LUT (256, 1, 3)
        lut = np.zeros((256, 1, 3), dtype=np.uint8)

        r1, g1, b1 = c1.red(), c1.green(), c1.blue()
        r2, g2, b2 = c2.red(), c2.green(), c2.blue()

        for i in range(256):
            t = i / 255.0
            r = int(r1 * (1 - t) + r2 * t)
            g = int(g1 * (1 - t) + g2 * t)
            b = int(b1 * (1 - t) + b2 * t)
            # LUT is BGR in OpenCV
            lut[i, 0] = [b, g, r]

        # 3. Apply LUT
        colorized = cv2.LUT(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), lut)

        self._update_editor(colorized)

    def _get_cv_img(self):
        qimg = self.editor.get_image()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
        # We need RGB for QColor logic, but CV2 uses BGR.
        # standardize on BGR return
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

    def _update_editor(self, cv_img):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bpl = ch * w
        qimg = QImage(rgb.data, w, h, bpl, QImage.Format.Format_RGB888).copy()
        self.editor.set_image(qimg)
        self.editor.mask_updated.emit()


class GradientMapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gradient Map")
        self.resize(300, 150)

        self.c1 = QColor(0, 0, 0)       # Shadows
        self.c2 = QColor(255, 255, 255)  # Highlights

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Color 1
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Shadows Color:"))
        self.btn_c1 = QPushButton()
        self.btn_c1.setStyleSheet(f"background-color: {self.c1.name()}")
        self.btn_c1.clicked.connect(lambda: self.pick_color(1))
        h1.addWidget(self.btn_c1)
        layout.addLayout(h1)

        # Color 2
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Highlights Color:"))
        self.btn_c2 = QPushButton()
        self.btn_c2.setStyleSheet(f"background-color: {self.c2.name()}")
        self.btn_c2.clicked.connect(lambda: self.pick_color(2))
        h2.addWidget(self.btn_c2)
        layout.addLayout(h2)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def pick_color(self, idx):
        c = QColorDialog.getColor()
        if c.isValid():
            if idx == 1:
                self.c1 = c
                self.btn_c1.setStyleSheet(f"background-color: {c.name()}")
            else:
                self.c2 = c
                self.btn_c2.setStyleSheet(f"background-color: {c.name()}")

    def get_colors(self):
        return self.c1, self.c2
