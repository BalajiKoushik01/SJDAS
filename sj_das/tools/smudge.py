
import cv2
import numpy as np
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen

from .base import Tool


class SmudgeTool(Tool):
    """
    Smudges pixels along the stroke path.
    """

    def __init__(self, editor):
        super().__init__(editor)
        self.last_pos = None

    def mouse_press(self, pos, buttons):
        self.last_pos = pos
        self.editor._start_stroke()

    def mouse_move(self, pos, buttons):
        if not self.last_pos:
            return

        if not self.editor.original_image:
            return

        # Smudge logic:
        # Grab pixels from last_pos
        # Blend them into current pos
        # For simplicity in QPainter, we can use a soft brush with low opacity?
        # A true smudge requires reading pixels, which is slow in pure Python QPainter.
        # Simulation: Pick color from last_pos, draw line to pos with low opacity.

        # 1. Pick Color at last_pos
        x, y = int(self.last_pos.x()), int(self.last_pos.y())
        if self.editor.original_image.valid(x, y):
            color = self.editor.original_image.pixelColor(x, y)
            
            # 2. Draw Paint with reduced opacity
            # This simulates "dragging" the color
            painter = QPainter(self.editor.original_image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            smudge_color = QColor(color)
            smudge_color.setAlpha(150) # Semi-transparent trail
            
            pen = QPen(smudge_color)
            pen.setWidth(self.editor.brush_size)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            painter.drawLine(self.last_pos, pos)
            painter.end()
            
            self.editor._update_scene_rect(
                self.last_pos.x(), self.last_pos.y(), 
                self.editor.brush_size, self.editor.brush_size
            )
            self.editor._update_scene_rect(
                pos.x(), pos.y(), 
                self.editor.brush_size, self.editor.brush_size
            )

        self.last_pos = pos

    def mouse_release(self, pos, buttons):
        self.last_pos = None
        self.editor._end_stroke("Smudge")
