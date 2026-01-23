
import cv2
import numpy as np
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget


class ColorSeparator:
    """
    Module for Color Separation (Jacquard Card Prep).
    Extracts unique color planes as binary masks.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        img = self._get_cv_img()

        # Analyze colors (Quantize first if needed? No, assume user cleaned it)
        # Find unique colors
        # Reshape to list of pixels
        pixels = img.reshape(-1, 3)
        uniques, counts = np.unique(pixels, axis=0, return_counts=True)

        # Sort by count (dominance)
        sorted_indices = np.argsort(-counts)
        sorted_colors = uniques[sorted_indices]

        # Limit to reasonable number (e.g. 16) for performance/display
        if len(sorted_colors) > 32:
            # Explain to user
            pass

        dialog = SeparatorDialog(sorted_colors, self.editor, self)
        dialog.exec()

    def apply_separation_view(self, color_bgr):
        img = self._get_cv_img()

        # Create mask
        # cv2.inRange is fast
        lower = np.array(color_bgr, dtype=np.uint8)
        upper = np.array(color_bgr, dtype=np.uint8)

        mask = cv2.inRange(img, lower, upper)

        # Convert mask (0/255) to Visual (Black on White)
        # Usually masks are white on black in CV.
        # Jacquard cards: Black dots = punch = lift?
        # Let's show Standard Binary: Black = Selected Color, White =
        # Background

        # Invert mask (0->255, 255->0) for "Ink on Paper" look
        visual = cv2.bitwise_not(mask)

        # Convert to RGB for display
        visual_rgb = cv2.cvtColor(visual, cv2.COLOR_GRAY2BGR)
        self._update_editor(visual_rgb)

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


class SeparatorDialog(QDialog):
    def __init__(self, colors, editor, controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Color Separation (Loom Ready)")
        self.resize(300, 400)
        self.colors = colors
        self.editor = editor
        self.controller = controller

        # Cache original image to restore
        self.orig_qimg = self.editor.get_image().copy()

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Found {len(self.colors)} Unique Colors"))
        layout.addWidget(QLabel("Click to View Separation Mask:"))

        # Scroll area for colors
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(2)

        for i, c_bgr in enumerate(self.colors):
            b, g, r = c_bgr
            hex_code = f"#{r:02x}{g:02x}{b:02x}"

            btn = QPushButton(f"Layer {i+1}: {hex_code}")
            btn.setStyleSheet(
                f"text-align: left; padding: 5px; background-color: {hex_code}; color: {'black' if (int(r)+int(g)+int(b))/3 > 128 else 'white'}")
            btn.clicked.connect(
                lambda checked,
                c=c_bgr: self.controller.apply_separation_view(c))
            vbox.addWidget(btn)

        container.setLayout(vbox)  # Fix layout assignment
        # Add scroll area if needed, simplified here
        layout.addWidget(container)

        layout.addStretch()

        btn_reset = QPushButton("Restore Original Image")
        btn_reset.clicked.connect(self.restore_original)
        layout.addWidget(btn_reset)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def restore_original(self):
        self.editor.set_image(self.orig_qimg)
        self.editor.mask_updated.emit()

    def reject(self):
        # Restore on close?
        self.restore_original()
        super().reject()
