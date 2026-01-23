import cv2
import numpy as np
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QInputDialog


class SymmetryFeature:
    """
    Module for applying symmetry effects to the canvas.
    """

    def __init__(self, editor):
        self.editor = editor

    def apply_mandala(self):
        """Apply 4-way or 8-way mirror symmetry based on user choice"""
        modes = [
            "4-Way (Mirror Quadrants)",
            "Horizontal Mirror",
            "Vertical Mirror"]
        mode, ok = QInputDialog.getItem(
            self.editor, "Symmetry Mode", "Select Mode:", modes, 0, False)

        if ok:
            if "4-Way" in mode:
                self._apply_quad_mirror()
            elif "Horizontal" in mode:
                self._apply_h_mirror()
            elif "Vertical" in mode:
                self._apply_v_mirror()

    def _apply_h_mirror(self):
        # Left side reflects to Right
        img = self._get_cv_img()
        h, w = img.shape[:2]
        mid = w // 2

        left = img[:, :mid]
        right = cv2.flip(left, 1)
        img[:, mid:] = right

        self._update_editor(img)

    def _apply_v_mirror(self):
        # Top reflects to Bottom
        img = self._get_cv_img()
        h, w = img.shape[:2]
        mid = h // 2

        top = img[:mid, :]
        bottom = cv2.flip(top, 0)
        img[mid:, :] = bottom

        self._update_editor(img)

    def _apply_quad_mirror(self):
        # Top-Left reflects to all
        img = self._get_cv_img()
        h, w = img.shape[:2]
        mid_x, mid_y = w // 2, h // 2

        tl = img[:mid_y, :mid_x]

        tr = cv2.flip(tl, 1)
        bl = cv2.flip(tl, 0)
        br = cv2.flip(bl, 1)

        img[:mid_y, mid_x:] = tr
        img[mid_y:, :mid_x] = bl
        img[mid_y:, mid_x:] = br

        self._update_editor(img)

    def _get_cv_img(self):
        qimg = self.editor.get_image()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)  # Return BGR

    def _update_editor(self, cv_img):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bpl = ch * w
        qimg = QImage(rgb.data, w, h, bpl, QImage.Format.Format_RGB888).copy()
        self.editor.set_image(qimg)
        self.editor.mask_updated.emit()
