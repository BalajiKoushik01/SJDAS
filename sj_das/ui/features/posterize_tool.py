import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QVBoxLayout)


class PosterizeTool:
    """
    Module for Posterization (Bit-depth reduction).
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = PosterizeDialog(self.editor)
        if dialog.exec():
            levels = dialog.get_levels()
            self._apply_posterize(levels)

    def _apply_posterize(self, levels):
        img = self._get_cv_img()

        # Calculate divisor
        # 256 / levels
        # E.g. levels = 4 -> div = 64
        # val = (val // 64) * 64

        div = 256 / levels

        # Vectorized
        # img is uint8.
        # We need float floor division or int division

        processed = np.floor(img / div) * div
        processed = processed.astype(np.uint8)

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


class PosterizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Posterize")
        self.resize(300, 100)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Levels (2-64)"))
        self.sl = QSlider(Qt.Orientation.Horizontal)
        self.sl.setRange(2, 64)
        self.sl.setValue(4)
        layout.addWidget(self.sl)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_levels(self):
        return self.sl.value()
