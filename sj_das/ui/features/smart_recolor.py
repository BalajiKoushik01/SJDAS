import cv2
import numpy as np
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QLabel,
                             QVBoxLayout)


class SmartRecolor:
    """
    Intelligent Theme Swapper & Recolor Tool.

    Features:
    - **Luminance Matching**: Maps colors from source to target palette while preserving brightness.
    - **Theme Library**: Includes built-in themes (Pastel, Wedding, Monochrome, etc.).
    - **K-Means Clustering**: Automatically detects dominant colors in the design.

    Usage:
    >>> recolor = SmartRecolor(editor_instance)
    >>> recolor.show_dialog()
    """

    def __init__(self, editor):
        self.editor = editor

        # Predefined themes (BGR tuples)
        self.themes = {
            "Original": [],
            # Pink, Peach, Yellow, Mint, Blue
            "Pastel Dream": [(255, 182, 193), (255, 223, 186), (255, 255, 186), (186, 255, 201), (186, 225, 255)],
            # DarkRed, Gold, Navy, White, Black
            "Royal Wedding": [(0, 0, 139), (212, 175, 55), (139, 0, 0), (255, 255, 255), (0, 0, 0)],
            "Earthy Tones": [(47, 79, 79), (85, 107, 47), (139, 69, 19), (160, 82, 45), (205, 92, 92)],
            "Monochrome Blue": [(25, 25, 112), (0, 0, 205), (65, 105, 225), (135, 206, 235), (240, 248, 255)],
            "Sunset Gradient": [(128, 0, 128), (255, 69, 0), (255, 140, 0), (255, 215, 0), (255, 255, 224)]
        }

    def show_dialog(self):
        img = self._get_cv_img()
        # Pre-calculate centers for speed?
        # Let's do it in the dialog preview.
        dialog = RecolorDialog(img, self.themes, self.editor)
        if dialog.exec():
            # Apply confirmed
            pass  # Already applied via "Apply" button or restore original on cancel

    def _get_cv_img(self):
        qimg = self.editor.get_image()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)


class RecolorDialog(QDialog):
    def __init__(self, img, themes, editor, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Recolor (Theme Swapper)")
        self.resize(400, 300)
        self.orig_img = img
        self.themes = themes
        self.editor = editor
        self.curr_img = img.copy()

        # K-Means Analysis on init
        self.centers, self.labels = self._analyze_colors(img, k=5)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select Color Theme:"))
        self.cmb = QComboBox()
        self.cmb.addItems(self.themes.keys())
        self.cmb.currentIndexChanged.connect(self.apply_preview)
        layout.addWidget(self.cmb)

        layout.addWidget(QLabel("Mapping Strategy: Luminance Matching"))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _analyze_colors(self, img, k=5):
        pixels = np.float32(img.reshape(-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(
            pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        return centers, labels

        # Apply
        self._update_editor(res_img)

    def _apply_semantic_mapping(self, current_centers, target_palette, k):
        """
        Smart Recolor 2.0: Uses Color Distance to find best matches.
        """
        # Convert both to float
        centers = current_centers.astype(np.float32)
        # Target palette to numpy
        targets = np.array(target_palette, dtype=np.float32)

        # Simple Euclidean in RGB (Fast) or CIELAB (Better)
        # Using RGB for now as cv2.cvtColor requires image shapes

        mapping = {}
        used_targets = set()

        # Greedy Algo: Find closest match pair first?
        # Or just sort by Intensity (Luminance) as a baseline?
        # Let's keep Luminance Sort as baseline but allow manual override in UI
        # (TODO)

        # Current Implementation: Luminance Match (Robust for preservation)
        # Distance match often fails if source is Red and Target has no Red.

        # Re-using the logic from Preview but refined
        def get_lum(c):
            return 0.299 * c[2] + 0.587 * c[1] + 0.114 * c[0]  # BGR

        src_lums = [(i, get_lum(c)) for i, c in enumerate(centers)]
        src_lums.sort(key=lambda x: x[1])

        tgt_lums = [(i, get_lum(t)) for i, t in enumerate(targets)]
        tgt_lums.sort(key=lambda x: x[1])

        # Map rank to rank
        for i in range(k):
            src_idx = src_lums[i][0]
            # Handle if target has fewer colors
            tgt_idx = i % len(targets)
            tgt_idx_sorted = tgt_lums[tgt_idx][0]

            mapping[src_idx] = targets[tgt_idx_sorted]

        return mapping

    def apply_preview(self):
        theme_name = self.cmb.currentText()
        if theme_name == "Original":
            self._update_editor(self.orig_img)
            return

        target_palette = self.themes[theme_name]
        k = len(self.centers)

        mapping = self._apply_semantic_mapping(self.centers, target_palette, k)

        new_centers = np.zeros_like(self.centers, dtype=np.uint8)
        for i in range(k):
            new_centers[i] = mapping[i]

        labels_flat = self.labels.flatten()
        res_flat = new_centers[labels_flat]
        res_img = res_flat.reshape(self.orig_img.shape)

        self._update_editor(res_img)

    def _update_editor(self, bgr_img):
        rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bpl = ch * w
        qimg = QImage(rgb.data, w, h, bpl, QImage.Format.Format_RGB888).copy()
        self.editor.set_image(qimg)
        self.editor.mask_updated.emit()

    def reject(self):
        self._update_editor(self.orig_img)
        super().reject()
