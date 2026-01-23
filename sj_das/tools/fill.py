"""Fill Tool for Area Painting.

Implements intelligent flood fill with selection awareness
and configurable tolerance.
"""

from typing import TYPE_CHECKING

from PyQt6.QtCore import QPointF, Qt

from .base import Tool

if TYPE_CHECKING:
    from sj_das.ui.editor_widget import PixelEditorWidget


class FillTool(Tool):
    """
    Paint bucket / flood fill tool.

    Features:
    - Intelligent flood fill algorithm
    - Selection-aware filling (respects active selection)
    - Undo/redo support
    - Right-click to erase

    Attributes:
        tolerance: Color matching tolerance for fill
    """

    def __init__(self, editor: 'PixelEditorWidget', tolerance: int = 5):
        """
        Initialize fill tool.

        Args:
            editor: Editor widget reference
            tolerance: Color tolerance for fill operation
        """
        super().__init__(editor)
        self.tolerance = tolerance

    def mouse_press(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Perform flood fill at clicked position.

        Args:
            pos: Fill start position
            buttons: Mouse buttons pressed
        """
        # Start undo transaction
        self.editor._start_stroke()

        # Determine if erasing (right button)
        is_eraser = (buttons & Qt.MouseButton.RightButton) != 0

        # Check for Pattern Mode from Editor State
        use_pattern = getattr(self.editor, 'fill_use_pattern', False)

        # Perform fill
        self.editor._fill(pos, is_eraser, use_pattern=use_pattern)

        # End undo transaction
        self.editor._end_stroke("Fill")

    def set_tolerance(self, tolerance: int) -> None:
        """
        Set color matching tolerance.

        Args:
            tolerance: New tolerance value (0-100)
        """
        self.tolerance = max(0, min(100, tolerance))
