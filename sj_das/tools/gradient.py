"""
Gradient Tool for SJ-DAS.
Create linear and radial gradients with interactive preview.
"""
from typing import TYPE_CHECKING

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem

from .base import Tool

if TYPE_CHECKING:
    from sj_das.ui.editor_widget import PixelEditorWidget


class GradientTool(Tool):
    """
    Gradient tool for creating smooth color transitions.

    Modes:
    - Linear: Straight gradient from start to end point
    - Radial: Circular gradient from center outward
    """

    def __init__(self, editor: 'PixelEditorWidget', mode: str = "linear"):
        super().__init__(editor)
        self.mode = mode  # "linear" or "radial"
        self.start_pos = None
        self.end_pos = None
        self.preview_item = None

        # Gradient colors (start and end)
        self.start_color = QColor(255, 255, 255, 255)  # White
        self.end_color = QColor(0, 0, 0, 255)  # Black

    def set_colors(self, start_color: QColor, end_color: QColor):
        """Set gradient start and end colors."""
        self.start_color = start_color
        self.end_color = end_color

    def set_mode(self, mode: str):
        """Set gradient mode (linear or radial)."""
        self.mode = mode

    def mouse_press(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """Start defining gradient."""
        self.start_pos = pos
        self.end_pos = pos

        # Create preview item
        if self.mode == "linear":
            self.preview_item = QGraphicsLineItem()
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine)
            self.preview_item.setPen(pen)
            self.editor.scene().addItem(self.preview_item)
        else:  # radial
            self.preview_item = QGraphicsEllipseItem()
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine)
            self.preview_item.setPen(pen)
            self.editor.scene().addItem(self.preview_item)

    def mouse_move(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """Update gradient preview."""
        if not self.start_pos or not self.preview_item:
            return

        self.end_pos = pos

        if self.mode == "linear":
            # Update line preview
            self.preview_item.setLine(
                self.start_pos.x(), self.start_pos.y(),
                self.end_pos.x(), self.end_pos.y()
            )
        else:  # radial
            # Update circle preview
            dx = self.end_pos.x() - self.start_pos.x()
            dy = self.end_pos.y() - self.start_pos.y()
            radius = (dx**2 + dy**2) ** 0.5

            self.preview_item.setRect(
                self.start_pos.x() - radius,
                self.start_pos.y() - radius,
                radius * 2,
                radius * 2
            )

    def mouse_release(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """Apply gradient to canvas."""
        if not self.start_pos:
            return

        self.end_pos = pos

        # Remove preview
        if self.preview_item:
            self.editor.scene().removeItem(self.preview_item)
            self.preview_item = None

        # Apply gradient
        is_eraser = (buttons & Qt.MouseButton.RightButton) != 0

        if self.mode == "linear":
            self.editor._draw_linear_gradient(
                self.start_pos, self.end_pos,
                self.start_color, self.end_color,
                is_eraser
            )
        else:  # radial
            dx = self.end_pos.x() - self.start_pos.x()
            dy = self.end_pos.y() - self.start_pos.y()
            radius = (dx**2 + dy**2) ** 0.5

            self.editor._draw_radial_gradient(
                self.start_pos, radius,
                self.start_color, self.end_color,
                is_eraser
            )

        # Reset
        self.start_pos = None
        self.end_pos = None
