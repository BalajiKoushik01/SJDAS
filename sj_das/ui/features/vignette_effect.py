import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QVBoxLayout)


class VignetteEffect:
    """
    Module for Vignette Effect (Dark corners).
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = VignetteDialog(self.editor)
        if dialog.exec():
            # Apply default strong vignette or slider based?
            # Let's do slider for intensity
            intensity = dialog.get_intensity()
            self._apply_vignette(intensity)

    def _apply_vignette(self, intensity):
        img = self._get_cv_img()
        rows, cols = img.shape[:2]

        # Generating vignette mask using Gaussian kernels
        kernel_x = cv2.getGaussianKernel(
            cols, cols / 2)  # Sigma relative to size
        kernel_y = cv2.getGaussianKernel(rows, rows / 2)
        kernel = kernel_y * kernel_x.T

        # Normalize mask to 0-1
        mask = 255 * kernel / np.linalg.norm(kernel)

        # Intensity scaling
        # Standard mask might be too weak or strong.
        # Let's stretch it based on intensity (0.5 to 1.5 multiplier)
        # But simpler: mask ranges typically 0 (edge) to ~0.00x... wait.
        # gaussian kernel product max is small. We need to normalize max to 1.

        mask = mask / mask.max()

        # If intensity < 100, we brighten corners back.
        # If intensity > 100, we darken more?
        # Let's treating 'intensity' as opacity of the black overlay.
        # Mask: 1 at center, 0 at corners.
        # We want to multiply image by Mask.

        # Adjust mask falloff
        # Power law: mask = mask ^ (1/strength)
        # strength 1 = normal
        # strength > 1 = tighter center

        power = intensity / 50.0  # 10 -> 0.2 (wide), 100 -> 2.0 (tight)
        mask = mask ** power

        # Expand to 3 channels
        mask_3ch = np.dstack([mask] * 3)

        processed = (img * mask_3ch).astype(np.uint8)

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


class VignetteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vignette")
        self.resize(300, 100)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Focus Tightness"))
        self.sl = QSlider(Qt.Orientation.Horizontal)
        self.sl.setRange(10, 150)
        self.sl.setValue(50)
        layout.addWidget(self.sl)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_intensity(self):
        return self.sl.value()
