
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen

from .base import Tool


class EraserTool(Tool):
    """
    Standard Eraser Tool.
    """

    def __init__(self, editor):
        super().__init__(editor)
        self.last_pos = None

    def mouse_press(self, pos, buttons):
        self.last_pos = pos
        self.editor._start_stroke()
        self._erase(pos)

    def mouse_move(self, pos, buttons):
        if self.last_pos:
            self._erase_line(self.last_pos, pos)
        self.last_pos = pos

    def mouse_release(self, pos, buttons):
        self.last_pos = None
        self.editor._end_stroke("Eraser")

    def _erase(self, pos):
        if not self.editor.original_image:
            return
            
        painter = QPainter(self.editor.original_image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source) # Overwrite
        
        # Transparent "Color"
        color = QColor(0, 0, 0, 0) 
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        
        r = self.editor.brush_size / 2
        painter.drawEllipse(pos, r, r)
        painter.end()
        
        self.editor._update_scene_rect(pos.x(), pos.y(), self.editor.brush_size, self.editor.brush_size)

    def _erase_line(self, p1, p2):
        if not self.editor.original_image:
            return
            
        painter = QPainter(self.editor.original_image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        
        pen = QPen(QColor(0,0,0,0))
        pen.setWidth(self.editor.brush_size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(p1, p2)
        painter.end()
        
        # Invalidate area (rough)
        self.editor._update_scene() 
