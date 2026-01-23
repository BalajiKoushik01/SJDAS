import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                             QLabel, QSlider, QVBoxLayout)


class ThresholdTool:
    """
    Module for Thresholding (Binarization).
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = ThresholdDialog(self.editor)
        if dialog.exec():
            val, mode_str, keep_color = dialog.get_params()
            self._apply_threshold(val, mode_str, keep_color)

    def _apply_threshold(self, val, mode_str, keep_color):
        img = self._get_cv_img()

        # Map mode
        mode = cv2.THRESH_BINARY
        if mode_str == "Binary Inverted":
            mode = cv2.THRESH_BINARY_INV
        elif mode_str == "Truncate":
            mode = cv2.THRESH_TRUNC
        elif mode_str == "To Zero":
            mode = cv2.THRESH_TOZERO

        if keep_color:
            # Apply to each channel independently? Or intensity?
            # Standard "Threshold" usually converts to B&W
            # If keep_color, let's threshold intensity but keep Hue?
            # Or simplified: Apply to R, G, B separately.
            _, res = cv2.threshold(img, val, 255, mode)
        else:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, res_gray = cv2.threshold(gray, val, 255, mode)
            res = cv2.cvtColor(res_gray, cv2.COLOR_GRAY2BGR)

        self._update_editor(res)

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


class ThresholdDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Threshold")
        self.resize(300, 150)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Threshold Level (0-255)"))
        self.sl = QSlider(Qt.Orientation.Horizontal)
        self.sl.setRange(0, 255)
        self.sl.setValue(128)
        layout.addWidget(self.sl)

        layout.addWidget(QLabel("Mode"))
        self.cmb = QComboBox()
        self.cmb.addItems(["Binary", "Binary Inverted", "Truncate", "To Zero"])
        layout.addWidget(self.cmb)

        self.chk_color = QCheckBox("Apply Per-Channel (Color)")
        self.chk_color.setToolTip(
            "If checked, thresholds R, G, B separately. If unchecked, converts to Grayscale.")
        layout.addWidget(self.chk_color)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_params(self):
        return self.sl.value(), self.cmb.currentText(), self.chk_color.isChecked()
