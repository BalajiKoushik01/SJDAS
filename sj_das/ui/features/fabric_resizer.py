import cv2
import numpy as np
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                             QFormLayout, QSpinBox, QVBoxLayout)


class FabricResizer:
    """
    Module for Precise Fabric Image Resizing.
    Supports Loom-Native (Nearest Neighbor) scaling.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        img = self.editor.get_image()
        w, h = img.width(), img.height()

        dialog = ResizeDialog(w, h, self.editor)
        if dialog.exec():
            nw, nh, algo = dialog.get_params()
            self._apply_resize(nw, nh, algo)

    def _apply_resize(self, w, h, algo_str):
        img_cv = self._get_cv_img()

        # Map algo string to CV2 constant
        interp = cv2.INTER_LINEAR
        if algo_str == "Nearest Neighbor (Hard Edges)":
            interp = cv2.INTER_NEAREST
        elif algo_str == "Bicubic (Smooth)":
            interp = cv2.INTER_CUBIC
        elif algo_str == "Lanczos (High Quality)":
            interp = cv2.INTER_LANCZOS4

        resized = cv2.resize(img_cv, (w, h), interpolation=interp)

        self._update_editor(resized)
        # Note: Editor widget might need to handle size change signal internally
        # But set_image handles it.

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


class ResizeDialog(QDialog):
    def __init__(self, w, h, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resize Fabric")
        self.resize(300, 200)
        self.orig_w = w
        self.orig_h = h
        self.aspect_ratio = w / h if h > 0 else 1.0
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.spin_w = QSpinBox()
        self.spin_w.setRange(1, 10000)
        self.spin_w.setValue(self.orig_w)

        self.spin_h = QSpinBox()
        self.spin_h.setRange(1, 10000)
        self.spin_h.setValue(self.orig_h)

        self.spin_w.valueChanged.connect(self.on_width_change)
        self.spin_h.valueChanged.connect(self.on_height_change)

        form.addRow("Width (px):", self.spin_w)
        form.addRow("Height (px):", self.spin_h)

        self.chk_lock = QCheckBox("Lock Aspect Ratio")
        self.chk_lock.setChecked(True)
        form.addRow(self.chk_lock)

        self.cmb_algo = QComboBox()
        self.cmb_algo.addItems([
            "Nearest Neighbor (Hard Edges)",
            "Bilinear (Standard)",
            "Bicubic (Smooth)",
            "Lanczos (High Quality)"
        ])
        # Default to Nearest for Textile as safety
        self.cmb_algo.setCurrentIndex(0)
        form.addRow("Resample Method:", self.cmb_algo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.updating = False

    def on_width_change(self, val):
        if self.updating or not self.chk_lock.isChecked():
            return
        self.updating = True
        self.spin_h.setValue(int(val / self.aspect_ratio))
        self.updating = False

    def on_height_change(self, val):
        if self.updating or not self.chk_lock.isChecked():
            return
        self.updating = True
        self.spin_w.setValue(int(val * self.aspect_ratio))
        self.updating = False

    def get_params(self):
        return self.spin_w.value(), self.spin_h.value(), self.cmb_algo.currentText()
