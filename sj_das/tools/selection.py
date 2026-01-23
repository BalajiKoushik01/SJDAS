"""Selection Tools for Precise Area Editing.

Implements marquee and magic wand selection with
modifier key support (add/subtract modes).
"""

from typing import TYPE_CHECKING

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtWidgets import QApplication, QGraphicsRectItem

from .base import Tool

if TYPE_CHECKING:
    from sj_das.ui.editor_widget import PixelEditorWidget


class RectSelectTool(Tool):
    """
    Rectangular marquee selection tool.

    Features:
    - Live visual preview during selection
    - Modifier key support (Shift=add, Alt=subtract)
    - Precise pixel-level selection
    - Professional marching ants style

    Attributes:
        start_pos: Selection start point
        preview_item: Visual preview rectangle
    """

    def __init__(self, editor: 'PixelEditorWidget'):
        """
        Initialize rectangular selection tool.

        Args:
            editor: Editor widget reference
        """
        super().__init__(editor)
        self.start_pos: QPointF | None = None
        self.preview_item: QGraphicsRectItem | None = None

    def mouse_press(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Start selection rectangle.

        Args:
            pos: Selection start position
            buttons: Mouse buttons pressed
        """
        self.start_pos = pos

        # Remove previous preview
        if self.preview_item:
            self.editor.scene.removeItem(self.preview_item)
            self.preview_item = None

        # Create new preview rectangle
        self.preview_item = QGraphicsRectItem()

        # Style: marching ants effect
        pen = QPen(Qt.GlobalColor.white, 1, Qt.PenStyle.DashLine)
        self.preview_item.setPen(pen)

        # Semi-transparent blue fill
        brush_color = QColor(0, 120, 255, 50)
        self.preview_item.setBrush(brush_color)

        # Add to scene
        self.editor.scene.addItem(self.preview_item)
        self.preview_item.setRect(QRectF(pos, pos))
        self.preview_item.setZValue(1000)  # Always on top

    def mouse_move(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Update selection preview as user drags.

        Args:
            pos: Current mouse position
            buttons: Mouse buttons pressed
        """
        if self.start_pos and self.preview_item:
            rect = QRectF(self.start_pos, pos).normalized()
            self.preview_item.setRect(rect)

    def mouse_release(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Finalize selection and apply to editor.

        Args:
            pos: Final selection position
            buttons: Mouse buttons pressed
        """
        if not self.start_pos:
            return

        # Determine operation mode from modifiers
        modifiers = QApplication.keyboardModifiers()

        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            operation = "add"
        elif modifiers & Qt.KeyboardModifier.AltModifier:
            operation = "subtract"
        else:
            operation = "replace"

        # Apply selection
        self.editor._apply_rect_selection(
            self.start_pos,
            pos,
            op=operation
        )

        # Cleanup
        self._cleanup()

    def _cleanup(self) -> None:
        """Remove preview and reset state."""
        if self.preview_item:
            self.editor.scene.removeItem(self.preview_item)
            self.preview_item = None
        self.start_pos = None

    def deactivate(self) -> None:
        """Clean up when tool is deactivated."""
        self._cleanup()


class MagicWandTool(Tool):
    """
    Magic wand selection tool (color-based selection).

    Features:
    - Intelligent color tolerance
    - Flood-fill based selection
    - Modifier key support for selection operations

    Attributes:
        tolerance: Color matching tolerance (0-255)
    """

    def __init__(self, editor: 'PixelEditorWidget', tolerance: int = 20):
        """
        Initialize magic wand tool.

        Args:
            editor: Editor widget reference
            tolerance: Color matching tolerance
        """
        super().__init__(editor)
        self.tolerance = tolerance

    def mouse_press(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Select contiguous area of similar color.

        Args:
            pos: Click position
            buttons: Mouse buttons pressed
        """
        # Determine operation mode
        modifiers = QApplication.keyboardModifiers()

        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            op = "add"
        elif modifiers & Qt.KeyboardModifier.AltModifier:
            op = "subtract"
        else:
            op = "replace"

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Force Classic Selection
            self.editor._magic_wand(pos, op, self.tolerance)
            return

        # Use Smart AI Selection (Default)
        if hasattr(self.editor, '_smart_magic_wand'):
            self.editor._smart_magic_wand(pos, op, self.tolerance)
        else:
            self.editor._magic_wand(pos, op, self.tolerance)

    def set_tolerance(self, tolerance: int) -> None:
        """
        Set color matching tolerance.

        Args:
            tolerance: New tolerance value (0-255)
        """
        self.tolerance = max(0, min(255, tolerance))
