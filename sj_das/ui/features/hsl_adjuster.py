import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QVBoxLayout)


class HSLAdjuster:
    """
    Module for HSL Adjustment (Hue, Saturation, Lightness).
    Standard Color Grading Tool.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = HSLDialog(self.editor)
        if dialog.exec():
            h, s, l = dialog.get_values()
            self._apply_hsl(h, s, l)

    def _apply_hsl(self, h_shift, s_shift, l_shift):
        # Shifts: Hue (-180..180), Sat (-100..100), Light (-100..100)
        img = self._get_cv_img()

        # Convert to HLS (Hue, Lightness, Saturation)
        # H: 0-179, L: 0-255, S: 0-255
        hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
        h_ch, l_ch, s_ch = cv2.split(hls)

        # 1. HUE
        # Wrap around 180
        # Cast to int16 to handle overflow before modulo
        h_new = h_ch.astype(np.int16) + h_shift
        # Handle wrap (modulo logic slightly complex with negatives in python?
        # % handles it)
        h_new = h_new % 180
        h_ch = h_new.astype(np.uint8)

        # 2. SATURATION
        # Additive shift? Or Multiplicative?
        # Photoshop "Saturation" usually adds constant.
        s_new = s_ch.astype(np.int16) + (s_shift * 255 // 100)
        s_ch = np.clip(s_new, 0, 255).astype(np.uint8)

        # 3. LIGHTNESS
        l_new = l_ch.astype(np.int16) + (l_shift * 255 // 100)
        l_ch = np.clip(l_new, 0, 255).astype(np.uint8)

        # Merge
        merged = cv2.merge([h_ch, l_ch, s_ch])
        bgr = cv2.cvtColor(merged, cv2.COLOR_HLS2BGR)

        self._update_editor(bgr)

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


class HSLDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hue / Saturation / Lightness")
        self.resize(300, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Hue Shift (-180° to 180°)"))
        self.sl_h = self._make_slider(-180, 180, 0)
        layout.addWidget(self.sl_h)

        layout.addWidget(QLabel("Saturation (-100 to +100)"))
        self.sl_s = self._make_slider(-100, 100, 0)
        layout.addWidget(self.sl_s)

        layout.addWidget(QLabel("Lightness (-100 to +100)"))
        self.sl_l = self._make_slider(-100, 100, 0)
        layout.addWidget(self.sl_l)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _make_slider(self, min_v, max_v, val):
        sl = QSlider(Qt.Orientation.Horizontal)
        sl.setRange(min_v, max_v)
        sl.setValue(val)
        return sl

    def get_values(self):
        return self.sl_h.value(), self.sl_s.value(), self.sl_l.value()
