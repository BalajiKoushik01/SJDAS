import cv2
import numpy as np
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class PerspectiveTool:
    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        """Shows perspective correction dialog"""
        img = self._get_cv_img()
        dialog = PerspectiveDialog(img, self.editor)
        if dialog.exec():
            pts = dialog.get_points()
            self._apply_correction(pts)

    def _apply_correction(self, pts):
        # pts is list of 4 (x,y) specific to original image coords
        img = self._get_cv_img()

        # Source points
        src = np.array(pts, dtype="float32")

        # Destination points (Rectangle)
        # We need to compute width/height of the new image
        # Standard logic: max width of top/bottom, max height of left/right
        (tl, tr, br, bl) = pts

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        # Matrix
        M = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

        self._update_editor(warped)

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


class PerspectiveCanvas(QLabel):
    def __init__(self, img_q, parent=None):
        super().__init__(parent)
        self.original_pixmap = QPixmap.fromImage(img_q)
        # Scale for display if too big
        self.display_pixmap = self.original_pixmap.scaled(
            600, 600, Qt.AspectRatioMode.KeepAspectRatio)
        self.scale_x = self.original_pixmap.width() / self.display_pixmap.width()
        self.scale_y = self.original_pixmap.height() / self.display_pixmap.height()

        self.setPixmap(self.display_pixmap)

        # Points (Display Coords)
        w, h = self.display_pixmap.width(), self.display_pixmap.height()
        margin = 20
        self.points = [
            QPoint(margin, margin),      # TL
            QPoint(w - margin, margin),    # TR
            QPoint(w - margin, h - margin),  # BR
            QPoint(margin, h - margin)     # BL
        ]
        self.active_idx = -1

    def mousePressEvent(self, event):
        pos = event.pos()
        # Check if near point
        min_d = 20
        for i, pt in enumerate(self.points):
            d = (pt - pos).manhattanLength()
            if d < min_d:
                self.active_idx = i
                min_d = d

    def mouseMoveEvent(self, event):
        if self.active_idx >= 0:
            self.points[self.active_idx] = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.active_idx = -1

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Quad
        painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
        poly = self.points
        painter.drawLine(poly[0], poly[1])
        painter.drawLine(poly[1], poly[2])
        painter.drawLine(poly[2], poly[3])
        painter.drawLine(poly[3], poly[0])

        # Draw Handles
        painter.setBrush(QBrush(Qt.GlobalColor.cyan))
        for pt in self.points:
            painter.drawEllipse(pt, 6, 6)

    def get_real_points(self):
        # Map back to original coords
        real_pts = []
        for pt in self.points:
            rx = pt.x() * self.scale_x
            ry = pt.y() * self.scale_y
            real_pts.append([rx, ry])
        return real_pts


class PerspectiveDialog(QDialog):
    def __init__(self, cv_img, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Perspective Fixer")

        # Convert CV to QImage for display
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bpl = ch * w
        qimg = QImage(rgb.data, w, h, bpl, QImage.Format.Format_RGB888)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Drag corners to match the fabric boundaries:"))

        self.canvas = PerspectiveCanvas(qimg)
        layout.addWidget(self.canvas)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_points(self):
        return self.canvas.get_real_points()
