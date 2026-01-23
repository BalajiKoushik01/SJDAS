import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QVBoxLayout)


class HalftoneGen:
    """
    Module for Halftone Effect (Dot Pattern).
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = HalftoneDialog(self.editor)
        if dialog.exec():
            size = dialog.get_size()
            self._apply_halftone(size)

    def _apply_halftone(self, size):
        img = self._get_cv_img()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Canvas for output
        output = np.ones((h, w, 3), dtype=np.uint8) * 255  # White bg

        # Grid loop
        # size is the cell size
        for y in range(0, h, size):
            for x in range(0, w, size):
                # Get average intensity of cell
                cell = gray[y:y + size, x:x + size]
                if cell.size == 0:
                    continue

                avg = np.mean(cell)
                # Invert: Darker = Bigger dot
                # Radius max = size/2
                # intensity 0 (black) -> radius size/2
                # intensity 255 (white) -> radius 0
                radius = int((1.0 - (avg / 255.0)) * (size / 2))

                center = (x + size // 2, y + size // 2)
                if radius > 0:
                    cv2.circle(output, center, radius, (0, 0, 0), -1)

        self._update_editor(output)

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


class HalftoneDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Halftone Effect")
        self.resize(300, 100)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Dot Size (Grid)"))
        self.sl = QSlider(Qt.Orientation.Horizontal)
        self.sl.setRange(4, 50)
        self.sl.setValue(10)
        layout.addWidget(self.sl)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_size(self):
        return self.sl.value()
