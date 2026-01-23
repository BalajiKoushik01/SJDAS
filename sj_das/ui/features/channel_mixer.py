import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QTabWidget, QVBoxLayout, QWidget)


class ChannelMixer:
    """
    Module for Professional Channel Mixing.
    Allows re-mixing R, G, B channels for advanced color grading.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = ChannelMixerDialog(self.editor)
        if dialog.exec():
            matrix = dialog.get_matrix()
            self._apply_mix(matrix)

    def _apply_mix(self, matrix):
        # Matrix is 3x3 (R, G, B output rows)
        img = self._get_cv_img()

        # Transform
        # Use cv2.transform which applies M to each pixel
        # M is typically 3x3 or 3x4 (with constant)
        # CV2 uses BGR, so we need to be careful with row order if matrix is RGB
        # Let's handle logical RGB -> RGB mixing

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # cv2.transform treats src as row vector: dst(I) = src(I) * M^T
        # Our matrix 'matrix' usually means:
        # R_out = R*rr + G*rg + B*rb
        # So we can pass it directly if structured correctly.

        # Matrix shape: (3, 3)
        processed = cv2.transform(rgb, matrix)

        # Clip
        processed = np.clip(processed, 0, 255).astype(np.uint8)

        # Back to BGR for editor update (logic wrapper handles it)
        # But wait, _update_editor expects BGR input.
        res_bgr = cv2.cvtColor(processed, cv2.COLOR_RGB2BGR)
        self._update_editor(res_bgr)

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


class ChannelMixerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Channel Mixer")
        self.resize(300, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        self.tab_r = self._create_channel_tab("Red Output", 100, 0, 0)
        self.tab_g = self._create_channel_tab("Green Output", 0, 100, 0)
        self.tab_b = self._create_channel_tab("Blue Output", 0, 0, 100)

        self.tabs.addTab(self.tab_r, "Red")
        self.tabs.addTab(self.tab_g, "Green")
        self.tabs.addTab(self.tab_b, "Blue")

        layout.addWidget(self.tabs)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _create_channel_tab(self, label, r, g, b):
        wid = QWidget()
        lay = QVBoxLayout(wid)

        lay.addWidget(QLabel("Source Red %"))
        sl_r = self._make_slider(r)
        lay.addWidget(sl_r)

        lay.addWidget(QLabel("Source Green %"))
        sl_g = self._make_slider(g)
        lay.addWidget(sl_g)

        lay.addWidget(QLabel("Source Blue %"))
        sl_b = self._make_slider(b)
        lay.addWidget(sl_b)

        # Store refs
        wid.sliders = (sl_r, sl_g, sl_b)
        return wid

    def _make_slider(self, val):
        sl = QSlider(Qt.Orientation.Horizontal)
        sl.setRange(-200, 200)
        sl.setValue(val)
        return sl

    def get_matrix(self):
        # Return 3x3 matrix normalized (divide by 100)
        r_row = [s.value() / 100.0 for s in self.tab_r.sliders]
        g_row = [s.value() / 100.0 for s in self.tab_g.sliders]
        b_row = [s.value() / 100.0 for s in self.tab_b.sliders]

        return np.array([r_row, g_row, b_row], dtype=np.float32)
