import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QLabel,
                             QSlider, QVBoxLayout)


class FilmGrain:
    """
    Module for Film Grain (Texture).
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = GrainDialog(self.editor)
        if dialog.exec():
            # Apply
            strength = dialog.get_strength()
            color = dialog.is_color()
            self._apply_grain(strength, color)

    def _apply_grain(self, strength, color):
        img = self._get_cv_img()
        h, w, c = img.shape

        # Generate Noise
        mean = 0
        sigma = strength  # Standard deviation

        if color:
            noise = np.zeros((h, w, 3), np.int16)
            cv2.randn(noise, (mean, mean, mean), (sigma, sigma, sigma))
        else:
            noise_1ch = np.zeros((h, w), np.int16)
            cv2.randn(noise_1ch, mean, sigma)
            noise = np.dstack([noise_1ch] * 3)

        # Add Noise
        # Convert img to int16 to avoid overflow during addition
        img16 = img.astype(np.int16)

        # Add
        noisy = img16 + noise

        # Clip back to 0-255
        processed = np.clip(noisy, 0, 255).astype(np.uint8)

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


class GrainDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Film Grain")
        self.resize(300, 150)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Grain Intensity (Sigma)"))
        self.sl = QSlider(Qt.Orientation.Horizontal)
        self.sl.setRange(0, 100)
        self.sl.setValue(25)
        layout.addWidget(self.sl)

        self.chk_color = QCheckBox("Chromatic Noise (Color Grain)")
        self.chk_color.setChecked(False)
        layout.addWidget(self.chk_color)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_strength(self):
        return self.sl.value()

    def is_color(self):
        return self.chk_color.isChecked()
