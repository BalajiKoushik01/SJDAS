import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QLabel,
                             QSlider, QVBoxLayout)


class EmbossEffect:
    """
    Module for Emboss / Relief Effect.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = EmbossDialog(self.editor)
        if dialog.exec():
            strength, gray = dialog.get_params()
            self._apply_emboss(strength, gray)

    def _apply_emboss(self, strength, gray_bg):
        img = self._get_cv_img()

        # Emboss Kernel
        # A simple directional convolution
        # Strength multiplier
        s = strength

        kernel = np.array([
            [-s, -s, 0],
            [-s, 1, s],
            [0, s, s]
        ])

        # Apply filter
        # depth=-1 maintains source depth (uint8), but embossing can go negative.
        # We need float to capture negative values, then offset.

        res = cv2.filter2D(img, cv2.CV_16S, kernel)

        if gray_bg:
            # Add neutral gray offset
            res = res + 128
        else:
            # Just add original image?
            # Standard "Artistic Emboss" usually is on gray.
            # "Relief" adds to original.
            # Keep direct result (dark on one side, light on other) for Relief
            # style
            pass
            # Actually, standard embossing usually adds 128 to shift 0 to
            # mid-gray
            res = res + 128

        processed = np.clip(res, 0, 255).astype(np.uint8)

        if gray_bg and len(processed.shape) == 3:
            # Convert to grayscale result if "Gray" requested
            # But embossing on color channels produces strange color shifts.
            # Better to process luminance and merge?
            # For simplicity now: standard convolution on RGB
            pass

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


class EmbossDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Emboss / Relief")
        self.resize(300, 150)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Depth Strength"))
        self.sl = QSlider(Qt.Orientation.Horizontal)
        self.sl.setRange(1, 5)
        self.sl.setValue(1)
        layout.addWidget(self.sl)

        self.chk_gray = QCheckBox("Neutral Gray Background (Standard)")
        self.chk_gray.setChecked(True)
        layout.addWidget(self.chk_gray)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_params(self):
        return self.sl.value(), self.chk_gray.isChecked()
