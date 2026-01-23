import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QVBoxLayout)


class PixelateEffect:
    """
    Module for Pixelate (Mosaic) Effect.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = PixelateDialog(self.editor)
        if dialog.exec():
            size = dialog.get_size()
            self._apply_pixelate(size)

    def _apply_pixelate(self, size):
        # Size = block size.
        img = self._get_cv_img()
        h, w = img.shape[:2]

        # 1. Downscale
        # New dims
        nw = max(1, w // size)
        nh = max(1, h // size)

        # Use Linear for average color downsampling
        small = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)

        # 2. Upscale Nearest
        pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

        self._update_editor(pixelated)

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


class PixelateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pixelate / Mosaic")
        self.resize(300, 100)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Block Size (Pixels)"))
        self.sl = QSlider(Qt.Orientation.Horizontal)
        self.sl.setRange(2, 64)
        self.sl.setValue(10)
        layout.addWidget(self.sl)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_size(self):
        return self.sl.value()
