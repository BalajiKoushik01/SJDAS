import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QVBoxLayout)


class ColorAdjuster:
    """
    Module for fine-tuning RGB Color Balance.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        """Shows adjustments dialog"""
        dialog = ColorBalanceDialog(self.editor)
        if dialog.exec():
            # Apply changes permanently upon OK
            # (Preview logic handled in dialog or simplistically applied at end)
            vals = dialog.get_values()
            self._apply_balance(vals)

    def _apply_balance(self, vals):
        # vals = (r_shift, g_shift, b_shift)
        img = self._get_cv_img()

        # Split channels
        b, g, r = cv2.split(img)

        # Add offsets (with clipping)
        # Note: CV2 images are uint8, so we need int16 for math to avoid
        # overflow, then clip
        b = np.clip(b.astype(np.int16) + vals[2], 0, 255).astype(np.uint8)
        g = np.clip(g.astype(np.int16) + vals[1], 0, 255).astype(np.uint8)
        r = np.clip(r.astype(np.int16) + vals[0], 0, 255).astype(np.uint8)

        merged = cv2.merge([b, g, r])
        self._update_editor(merged)

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


class ColorBalanceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Color Balance")
        self.resize(300, 200)
        self.values = [0, 0, 0]  # R, G, B
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Red
        layout.addWidget(QLabel("Red"))
        self.sl_r = self._make_slider()
        layout.addWidget(self.sl_r)

        # Green
        layout.addWidget(QLabel("Green"))
        self.sl_g = self._make_slider()
        layout.addWidget(self.sl_g)

        # Blue
        layout.addWidget(QLabel("Blue"))
        self.sl_b = self._make_slider()
        layout.addWidget(self.sl_b)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _make_slider(self):
        sl = QSlider(Qt.Orientation.Horizontal)
        sl.setRange(-100, 100)
        sl.setValue(0)
        return sl

    def get_values(self):
        return (self.sl_r.value(), self.sl_g.value(), self.sl_b.value())
