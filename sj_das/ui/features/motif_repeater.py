import cv2
import numpy as np
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                             QSpinBox, QVBoxLayout)


class MotifRepeater:
    """
    Module for Saree Motif Repetition (Butta Generator).
    Supports Grid, Brick, and Half-Drop repeates.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        img = self._get_cv_img()
        h, w = img.shape[:2]

        dialog = RepeatDialog(w, h, self.editor)
        if dialog.exec():
            target_w, target_h, mode, spacing_x, spacing_y = dialog.get_params()
            self._apply_repeat(target_w, target_h, mode, spacing_x, spacing_y)

    def _apply_repeat(self, tw, th, mode, sx, sy):
        motif = self._get_cv_img()
        mh, mw = motif.shape[:2]

        # Create clear canvas (or colored?) - Let's do transparent/white?
        # Standard Textile: White canvas base
        canvas = np.ones((th, tw, 3), dtype=np.uint8) * 255

        # Calculate repetitions needed
        # We start drawing from top-left, maybe slightly off-canvas to handle
        # brick/drop

        cols = int(tw / (mw + sx)) + 2
        rows = int(th / (mh + sy)) + 2

        for r in range(rows):
            for c in range(cols):
                # Calculate X, Y
                x = c * (mw + sx)
                y = r * (mh + sy)

                # Apply Shifts
                if mode == "Brick (Row Shift)":
                    if r % 2 == 1:
                        x += (mw + sx) // 2
                elif mode == "Half-Drop (Column Shift)" and c % 2 == 1:
                    y += (mh + sy) // 2

                # Paste if within bounds
                # Slicing logic

                # Intersection logic
                x1 = x
                y1 = y
                x2 = x + mw
                y2 = y + mh

                # Canvas bounds
                cx1 = max(0, x1)
                cy1 = max(0, y1)
                cx2 = min(tw, x2)
                cy2 = min(th, y2)

                # Motif bounds
                mx1 = cx1 - x1
                my1 = cy1 - y1
                mx2 = mx1 + (cx2 - cx1)
                my2 = my1 + (cy2 - cy1)

                if cx2 > cx1 and cy2 > cy1:
                    # Overlay (Simple copy for opaque, or alpha blend?)
                    # Assuming opaque motif for now
                    canvas[cy1:cy2, cx1:cx2] = motif[my1:my2, mx1:mx2]

        self._update_editor(canvas)

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


class RepeatDialog(QDialog):
    def __init__(self, mw, mh, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Motif Repeater")
        self.resize(300, 250)

        # Defaults for bigger canvas
        self.def_w = mw * 4
        self.def_h = mh * 4

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.spin_w = QSpinBox()
        self.spin_w.setRange(100, 10000)
        self.spin_w.setValue(self.def_w)
        form.addRow("Canvas Width:", self.spin_w)

        self.spin_h = QSpinBox()
        self.spin_h.setRange(100, 10000)
        self.spin_h.setValue(self.def_h)
        form.addRow("Canvas Height:", self.spin_h)

        self.cmb_mode = QComboBox()
        self.cmb_mode.addItems(
            ["Grid (Straight)", "Brick (Row Shift)", "Half-Drop (Column Shift)"])
        form.addRow("Repeat Pattern:", self.cmb_mode)

        self.spin_sx = QSpinBox()
        self.spin_sx.setRange(0, 500)
        self.spin_sx.setValue(0)
        form.addRow("Spacing X:", self.spin_sx)

        self.spin_sy = QSpinBox()
        self.spin_sy.setRange(0, 500)
        self.spin_sy.setValue(0)
        form.addRow("Spacing Y:", self.spin_sy)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_params(self):
        return self.spin_w.value(), self.spin_h.value(
        ), self.cmb_mode.currentText(), self.spin_sx.value(), self.spin_sy.value()
