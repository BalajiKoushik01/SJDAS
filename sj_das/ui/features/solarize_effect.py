import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QVBoxLayout)


class SolarizeEffect:
    """
    Module for Solarize Effect (Invert above threshold).
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = SolarizeDialog(self.editor)
        if dialog.exec():
            thresh = dialog.get_threshold()
            self._apply_solarize(thresh)

    def _apply_solarize(self, threshold):
        img = self._get_cv_img()

        # Logic: If pixel < threshold: pixel
        #        Else: 255 - pixel

        # Vectorized implementation using LUT
        lut = np.arange(256, dtype=np.uint8)
        # Invert upper range
        lut[threshold:] = 255 - lut[threshold:]

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


class SolarizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Solarize")
        self.resize(300, 100)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Threshold (The Sabatier Point)"))
        self.sl = QSlider(Qt.Orientation.Horizontal)
        self.sl.setRange(0, 255)
        self.sl.setValue(128)
        layout.addWidget(self.sl)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_threshold(self):
        return self.sl.value()
