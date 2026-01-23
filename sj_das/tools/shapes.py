from PyQt6.QtCore import QLineF, QRectF, Qt
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem

from .base import Tool


class RectTool(Tool):
    """
    Draws Rectangles with Live Preview.
    """

    def __init__(self, editor):
        super().__init__(editor)
        self.start_pos = None
        self.preview_item = None

    def mouse_press(self, pos, buttons):
        self.start_pos = pos
        self.editor._start_stroke()

        # Setup Preview
        self.preview_item = QGraphicsRectItem()
        # Use simple contrast color for preview
        self.preview_item.setPen(
            QPen(
                Qt.GlobalColor.white,
                1,
                Qt.PenStyle.SolidLine))
        self.editor.scene.addItem(self.preview_item)
        self.preview_item.setRect(QRectF(pos, pos))

    def mouse_move(self, pos, buttons):
        if self.start_pos and self.preview_item:
            rect = QRectF(self.start_pos, pos).normalized()
            self.preview_item.setRect(rect)

    def mouse_release(self, pos, buttons):
        if self.preview_item:
            self.editor.scene.removeItem(self.preview_item)
            self.preview_item = None

        is_eraser = (buttons & Qt.MouseButton.RightButton)
        self.editor._draw_rect_shape(self.start_pos, pos, is_eraser)
        self.editor._end_stroke("Rectangle")


class LineTool(Tool):
    """
    Draws Straight Lines with Live Preview.
    """

    def __init__(self, editor):
        super().__init__(editor)
        self.start_pos = None
        self.preview_item = None

    def mouse_press(self, pos, buttons):
        self.start_pos = pos
        self.editor._start_stroke()

        # Setup Preview
        self.preview_item = QGraphicsLineItem()
        self.preview_item.setPen(
            QPen(
                Qt.GlobalColor.white,
                1,
                Qt.PenStyle.SolidLine))
        self.editor.scene.addItem(self.preview_item)
        self.preview_item.setLine(QLineF(pos, pos))

    def mouse_move(self, pos, buttons):
        if self.start_pos and self.preview_item:
            self.preview_item.setLine(QLineF(self.start_pos, pos))

    def mouse_release(self, pos, buttons):
        if self.preview_item:
            self.editor.scene.removeItem(self.preview_item)
            self.preview_item = None

        is_eraser = (buttons & Qt.MouseButton.RightButton)
        self.editor._draw_pixel_line(self.start_pos, pos, is_eraser)
        self.editor._end_stroke("Line")


class EllipseTool(Tool):
    """
    Draws Ellipses with Live Preview.
    """

    def __init__(self, editor):
        super().__init__(editor)
        self.start_pos = None
        self.preview_item = None

    def mouse_press(self, pos, buttons):
        self.start_pos = pos
        self.editor._start_stroke()

        # Setup Preview
        from PyQt6.QtWidgets import QGraphicsEllipseItem
        self.preview_item = QGraphicsEllipseItem()
        # Use simple contrast color for preview
        self.preview_item.setPen(
            QPen(
                Qt.GlobalColor.white,
                1,
                Qt.PenStyle.SolidLine))
        self.editor.scene.addItem(self.preview_item)
        self.preview_item.setRect(QRectF(pos, pos))

    def mouse_move(self, pos, buttons):
        if self.start_pos and self.preview_item:
            rect = QRectF(self.start_pos, pos).normalized()
            self.preview_item.setRect(rect)

    def mouse_release(self, pos, buttons):
        if self.preview_item:
            self.editor.scene.removeItem(self.preview_item)
            self.preview_item = None

        is_eraser = (buttons & Qt.MouseButton.RightButton)
        self.editor._draw_ellipse_shape(self.start_pos, pos, is_eraser)
        self.editor._end_stroke("Ellipse")
