import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QVBoxLayout)


class NoiseReducer:
    """
    Module for Advanced Noise Reduction (Denoising).
    Uses Non-Local Means Denoising.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        """Shows denoising dialog"""
        dialog = NoiseDialog(self.editor)
        if dialog.exec():
            strength = dialog.get_strength()
            self._apply_denoise(strength)

    def _apply_denoise(self, strength):
        img = self._get_cv_img()

        # Fast Non-Local Means Denoising
        # h = strength (filter strength)
        # hColor = same as h usually
        # templateWindowSize = 7 (default)
        # searchWindowSize = 21 (default)
        processed = cv2.fastNlMeansDenoisingColored(
            img, None, strength, strength, 7, 21)

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


class NoiseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Noise Reduction (Smart Denoise)")
        self.resize(300, 100)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Denoise Strength (Smoother <-> Detail)"))
        self.sl_s = QSlider(Qt.Orientation.Horizontal)
        self.sl_s.setRange(1, 50)
        self.sl_s.setValue(10)
        layout.addWidget(self.sl_s)

        self.lbl_val = QLabel("10")
        layout.addWidget(self.lbl_val)
        self.sl_s.valueChanged.connect(lambda v: self.lbl_val.setText(str(v)))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_strength(self):
        return self.sl_s.value()
