import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QLabel,
                             QSlider, QVBoxLayout)


class WeaveSimulator:
    """
    Module for Weave Texture Simulation (Physical Preview).
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = WeaveDialog(self.editor)
        if dialog.exec():
            pattern_name, scale, opacity = dialog.get_params()
            self._apply_weave(pattern_name, scale, opacity)

    def _apply_weave(self, name, scale, opacity):
        img_rgb = self._get_cv_img()  # RGB for blending
        h, w = img_rgb.shape[:2]

        # 1. Generate Pattern Tile
        tile = self._generate_pattern(name)

        # 2. Scale Tile (Texture Zoom)
        # Using Nearest Neighbor to keep structure crisp or Linear for soft?
        # Physical threads are crisp.
        # Scale determines how many pixels per thread.
        # Base tile is usually small (e.g. 4x4).
        # Scale 1 = 1 screen pixel per thread pixel.
        th, tw = tile.shape
        tile_scaled = cv2.resize(
            tile, (tw * scale, th * scale), interpolation=cv2.INTER_NEAREST)

        # 3. Tile across canvas
        # Create full texture mask
        # np.tile is easy
        rows = (h // tile_scaled.shape[0]) + 1
        cols = (w // tile_scaled.shape[1]) + 1

        full_pattern = np.tile(tile_scaled, (rows, cols))
        # Crop to size
        full_pattern = full_pattern[:h, :w]

        # 4. Blend
        # Pattern is 0-255 grayscale.
        # We want to multiply?
        # High value = highlight, Low value = shadow.
        # Thread texture usually adds relief.

        # Convert pattern to 3 ch
        pat_3 = np.dstack([full_pattern] * 3).astype(np.float32) / 255.0

        # Image float
        img_f = img_rgb.astype(np.float32)

        # Blend Logic: Multiply?
        # Or Overlay?
        # Simple simulation: Multiply for shadows.
        # Adjust strength using opacity (0.0 to 1.0)
        # Result = Img * (1 - opacity + pattern * opacity)
        # If opacity 1.0 -> Img * pattern (Full multiply)
        # If opacity 0.5 -> Img * (0.5 + 0.5*pat) -> Darkens less

        # But weave has highlights too?
        # Let's map pattern 0..255 to something like 0.5..1.5?
        # No, standard multiply is safer for simulation (ink on cloth).

        factor = 1.0 - (opacity * 0.4)  # Don't go to 0 contrast
        # map pattern 0..1 to factor..1
        pat_mod = factor + (1.0 - factor) * pat_3

        res = img_f * pat_mod

        processed = np.clip(res, 0, 255).astype(np.uint8)

        self._update_editor(processed)

    def _generate_pattern(self, name):
        # Return uint8 grayscale arrays
        if name == "Plain / Tabby (1/1)":
            return np.array([[200, 50], [50, 200]], dtype=np.uint8)

        elif name == "Twill (2/1)":
            # Diagonal
            return np.array([
                [50, 200, 200],
                [200, 50, 200],
                [200, 200, 50]
            ], dtype=np.uint8)

        elif name == "Satin (5-End)":
            # Sateen look (smooth with dots)
            s = np.ones((5, 5), dtype=np.uint8) * 220
            # Binding points
            s[0, 0] = 50
            s[1, 2] = 50
            s[2, 4] = 50
            s[3, 1] = 50
            s[4, 3] = 50
            return s

        elif name == "Canvas (Rough)":
            # random noise
            return np.random.randint(100, 255, (32, 32), dtype=np.uint8)

        return np.ones((4, 4), dtype=np.uint8) * 255

    def _get_cv_img(self):
        qimg = self.editor.get_image()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
        # Return RGB for blend calculation ease
        rgb = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
        return rgb

    def _update_editor(self, rgb_img):
        # Input RGB
        h, w, ch = rgb_img.shape
        bpl = ch * w
        qimg = QImage(
            rgb_img.data,
            w,
            h,
            bpl,
            QImage.Format.Format_RGB888).copy()
        self.editor.set_image(qimg)
        self.editor.mask_updated.emit()


class WeaveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Weave Simulation")
        self.resize(300, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Weave Structure"))
        self.cmb = QComboBox()
        self.cmb.addItems(["Plain / Tabby (1/1)", "Twill (2/1)",
                          "Satin (5-End)", "Canvas (Rough)"])
        layout.addWidget(self.cmb)

        layout.addWidget(QLabel("Thread Scale (Zoom)"))
        self.sl_scale = QSlider(Qt.Orientation.Horizontal)
        self.sl_scale.setRange(1, 10)
        self.sl_scale.setValue(2)
        layout.addWidget(self.sl_scale)

        layout.addWidget(QLabel("Texture Strength (Opacity)"))
        self.sl_op = QSlider(Qt.Orientation.Horizontal)
        self.sl_op.setRange(0, 100)
        self.sl_op.setValue(50)
        layout.addWidget(self.sl_op)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_params(self):
        return self.cmb.currentText(), self.sl_scale.value(), self.sl_op.value() / 100.0
