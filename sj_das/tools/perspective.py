import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPen, QPolygonF
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsPolygonItem

from .base import Tool


class PerspectiveTool(Tool):
    """
    4-Point Perspective Correction Tool.
    User clicks 4 corners (Top-Left -> Top-Right -> Bottom-Right -> Bottom-Left).
    The image is then warped to a flat rectangle.
    """

    def __init__(self, editor):
        super().__init__(editor)
        self.points = []
        self.visual_items = []  # Markers
        self.poly_item = None

    def mouse_press(self, pos, buttons):
        if buttons & Qt.MouseButton.LeftButton and len(self.points) < 4:
            self.points.append(pos)
            self._update_visuals()

            if len(self.points) == 4:
                self._apply_correction()

    def mouse_move(self, pos, buttons):
        # Update dynamic line for next point?
        pass

    def _update_visuals(self):
        # Clear old
        for item in self.visual_items:
            self.editor.scene.removeItem(item)
        self.visual_items.clear()

        if self.poly_item:
            self.editor.scene.removeItem(self.poly_item)
            self.poly_item = None

        # Draw Points
        r = 5
        for pt in self.points:
            marker = QGraphicsEllipseItem(pt.x() - r, pt.y() - r, r * 2, r * 2)
            marker.setBrush(QBrush(QColor(255, 255, 0)))  # Yellow
            marker.setPen(QPen(Qt.GlobalColor.black))
            self.editor.scene.addItem(marker)
            self.visual_items.append(marker)

        # Draw Polygon
        if len(self.points) > 1:
            poly = QPolygonF(self.points)
            self.poly_item = QGraphicsPolygonItem(poly)
            self.poly_item.setPen(
                QPen(
                    QColor(
                        255,
                        255,
                        0),
                    2,
                    Qt.PenStyle.DashLine))
            self.poly_item.setBrush(QColor(255, 255, 0, 50))
            self.editor.scene.addItem(self.poly_item)

    def _apply_correction(self):
        """
        Calculates Homography and Warps Image.
        """
        if not self.editor.original_image:
            return

        # 1. Source Points
        src_pts = np.float32([[p.x(), p.y()] for p in self.points])

        # 2. Destination Points (A4 Ratio or Bounding Box?)
        # Let's estimate width/height from the bounding box of selection
        # Or just use the max width of the trapezoid

        # Order: TL, TR, BR, BL
        tl, tr, br, bl = src_pts

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # Destination Rect (Top-Left 0,0)
        dst_pts = np.float32([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ])

        # 3. Calculate Transform
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)

        # 4. Warp
        # Convert QImage to CV2
        self.editor._qimage_to_cv2(self.editor.original_image)
        # _qimage_to_cv2 returns BGRA (ARGB32), we need BGR ideally or handle alpha
        # Let's assume convertToFormat(RGB888) logic is better for warping
        # Use editor's helper if available or manual

        # Robust conversion
        ptr = self.editor.original_image.bits()
        ptr.setsize(
            self.editor.original_image.height() *
            self.editor.original_image.width() *
            3)  # Assuming RGB888 if converted?
        # Actually standard is:
        orig = self.editor.original_image.convertToFormat(
            self.editor.original_image.Format.Format_RGB888)
        ptr = orig.bits()
        ptr.setsize(orig.height() * orig.width() * 3)
        arr = np.array(ptr).reshape(orig.height(), orig.width(), 3)
        # RGB -> BGR
        # But wait, QImage RGB888 is Byte Order R G B.

        warped = cv2.warpPerspective(arr, M, (maxWidth, maxHeight))

        # 5. Set Result
        self.editor.set_image(warped)  # Will convert back to QImage

        # Cleanup
        self.points.clear()
        self._update_visuals()

        # Notify
        # self.editor is not a widget that has messagebox parent usually?
        # It's a valid QWidget.
        # But let's just print or signal.
        print("Perspective Correction Applied.")
        # Switch back to Pan tool?
        self.editor.setCursor(Qt.CursorShape.ArrowCursor)
