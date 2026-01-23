from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsView

from .base import Tool


class PanTool(Tool):
    """
    Hand / Pan Tool.
    Seamlessly scrolls the canvas.
    """

    def mouse_press(self, pos, buttons):
        self.editor.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.editor.setCursor(Qt.CursorShape.ClosedHandCursor)
        # Emulate click to grab immediately
        # QGraphicsView usually needs a native event for this,
        # but setting DragMode + passing event super usually works.

    def mouse_release(self, pos, buttons):
        self.editor.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.editor.setCursor(Qt.CursorShape.OpenHandCursor)
