import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QVBoxLayout)


class CurvesTool:
    """
    Module for Non-Linear Brightness Mapping (Curves).
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = CurvesDialog(self.editor)
        if dialog.exec():
            lut = dialog.get_lut()
            self._apply_lut(lut)

    def _apply_lut(self, lut):
        img = self._get_cv_img()

        # Apply LUT (Look Up Table)
        # CV2 LUT works on 8-bit images
        processed = cv2.LUT(img, lut)

        self._update_editor(processed)

    def _get_cv_img(self):
        qimg = self.editor.get_image()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

    def _update_editor(self, cv_img):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bpl = ch * w
        qimg = QImage(rgb.data, w, h, bpl, QImage.Format.Format_RGB888).copy()
        self.editor.set_image(qimg)
        self.editor.mask_updated.emit()


class CurvesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Curves (Brightness Mapping)")
        self.resize(300, 200)

        # Default points: (Input, Output)
        # We control Output Y for fixed Input X positions
        # X: 0, 64, 128, 192, 255
        # Y defaults to same
        self.points = [0, 64, 128, 192, 255]

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Shadows (Input 64)"))
        self.sl_s = self._make_slider(64)
        layout.addWidget(self.sl_s)

        layout.addWidget(QLabel("Midtones (Input 128)"))
        self.sl_m = self._make_slider(128)
        layout.addWidget(self.sl_m)

        layout.addWidget(QLabel("Highlights (Input 192)"))
        self.sl_h = self._make_slider(192)
        layout.addWidget(self.sl_h)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _make_slider(self, val):
        sl = QSlider(Qt.Orientation.Horizontal)
        sl.setRange(0, 255)
        sl.setValue(val)
        return sl

    def get_lut(self):
        # Create LUT from simple piecewise linear interpolation of 5 points
        # (0,0), (64, s), (128, m), (192, h), (255, 255)

        y_points = [
            0,
            self.sl_s.value(),
            self.sl_m.value(),
            self.sl_h.value(),
            255]
        x_points = [0, 64, 128, 192, 255]

        # Interpolate 0-255
        lut = np.interp(np.arange(256), x_points, y_points).astype(np.uint8)
        return lut
