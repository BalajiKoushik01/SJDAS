"""Brush and Eraser Tools for Pixel Editing.

Implements freehand drawing with variable brush sizes and
intelligent line interpolation using Bresenham's algorithm.
"""

from typing import TYPE_CHECKING

from PyQt6.QtCore import QPoint, QPointF, Qt

from .base import Tool

if TYPE_CHECKING:
    from sj_das.ui.editor_widget import PixelEditorWidget


class BrushTool(Tool):
    """
    Freehand brush/eraser tool with smooth line drawing.

    Features:
    - Bresenham line interpolation for smooth strokes
    - Variable brush size support
    - Stencil mask awareness (selection-aware drawing)
    - Efficient pixel-perfect rendering

    Attributes:
        is_eraser: True if tool erases, False if it paints
        last_pos: Last mouse position for line interpolation
    """

    def __init__(self, editor: 'PixelEditorWidget', is_eraser: bool = False):
        """
        Initialize brush tool.

        Args:
            editor: Editor widget reference
            is_eraser: True for eraser mode, False for paint mode
        """
        super().__init__(editor)
        self.is_eraser = is_eraser
        self.last_pos: QPointF | None = None

    def mouse_press(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Start drawing stroke.

        Args:
            pos: Initial brush position
            buttons: Mouse buttons pressed
        """
        self.editor._start_stroke()
        self.last_pos = pos
        self._draw(pos)

    def mouse_move(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Continue drawing stroke with line interpolation.

        Args:
            pos: Current brush position
            buttons: Mouse buttons pressed
        """
        if self.last_pos is not None:
            self._draw_line(self.last_pos, pos)
            self.last_pos = pos

    def mouse_release(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        End drawing stroke and commit to undo stack.

        Args:
            pos: Final brush position
            buttons: Mouse buttons pressed
        """
        action_name = "Eraser" if self.is_eraser else "Brush"
        self.editor._end_stroke(action_name)
        self.last_pos = None

    def _draw(self, pos: QPointF) -> None:
        """
        Draw at single point with current brush size.

        Args:
            pos: Position to draw at
        """
        x, y = int(pos.x()), int(pos.y())

        # Draw with current brush size
        self.editor._draw_pixel_circle(
            QPoint(x, y),
            self.editor.brush_size,
            self.is_eraser
        )

    def _draw_line(self, p0: QPointF, p1: QPointF) -> None:
        """
        Draw interpolated line using Bresenham's algorithm.

        Ensures no gaps in stroke even with fast mouse movement.

        Args:
            p0: Line start point
            p1: Line end point
        """
        x0, y0 = int(p0.x()), int(p0.y())
        x1, y1 = int(p1.x()), int(p1.y())

        # Bresenham's line algorithm
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = abs(y1 - y0)
        error = dx / 2
        ystep = 1 if y0 < y1 else -1
        y = y0

        for x in range(x0, x1 + 1):
            coord = QPoint(y, x) if steep else QPoint(x, y)
            self._draw(coord)

            error -= dy
            if error < 0:
                y += ystep
                error += dx

    def deactivate(self) -> None:
        """Clean up when tool is deactivated."""
        self.last_pos = None
