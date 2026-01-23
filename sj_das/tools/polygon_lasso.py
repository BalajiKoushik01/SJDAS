"""Polygon Lasso Tool - Click-to-draw selection.

Professional polygon selection tool for precise selections.
"""

import logging

import cv2
import numpy as np
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPen, QPolygonF
from PyQt6.QtWidgets import QGraphicsPolygonItem

from sj_das.tools.base import Tool

logger = logging.getLogger(__name__)


class PolygonLassoTool(Tool):
    """
    Professional polygon lasso selection tool.

    Features:
    - Click to add point to polygon
    - Double-click or press Enter to complete
    - ESC to cancel
    - Backspace to remove last point
    - Shows preview line to cursor
    """

    def __init__(self, editor):
        """Initialize polygon lasso tool."""
        super().__init__(editor)
        self.points = []
        self.preview_line = None
        self.polygon_item = None
        self.is_active = False

    def mouse_press(self, pos: QPointF, buttons: Qt.MouseButton):
        """Add point to polygon."""
        if buttons & Qt.MouseButton.LeftButton:
            # Add point
            self.points.append(pos)
            self.is_active = True

            # Update visual preview
            self._update_preview()

            logger.debug(
                f"Polygon lasso: Added point {len(self.points)} at ({pos.x():.0f}, {pos.y():.0f})")

    def mouse_move(self, pos: QPointF, buttons: Qt.MouseButton):
        """Update preview line to cursor."""
        if not self.is_active or len(self.points) == 0:
            return

        # Update preview line from last point to cursor
        self._draw_preview_line(pos)

    def mouse_release(self, pos: QPointF, buttons: Qt.MouseButton):
        """Handle release (not used for polygon lasso)."""
        pass

    def mouse_double_click(self, pos: QPointF):
        """Complete polygon on double-click."""
        if len(self.points) >= 3:
            self._complete_selection()
        else:
            logger.warning("Polygon lasso: Need at least 3 points")

    def key_press(self, key: int):
        """
        Handle keyboard input.

        Enter: Complete selection
        ESC: Cancel selection
        Backspace: Remove last point
        """
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            if len(self.points) >= 3:
                self._complete_selection()

        elif key == Qt.Key.Key_Escape:
            self._cancel_selection()

        elif key == Qt.Key.Key_Backspace and self.points:
            self.points.pop()
            self._update_preview()
            logger.debug(
                f"Polygon lasso: Removed point, {len(self.points)} remaining")

    def _update_preview(self):
        """Update polygon preview visualization."""
        if not self.points:
            self._clear_preview()
            return

        # Remove old preview
        if self.polygon_item:
            self.editor.scene.removeItem(self.polygon_item)

        # Create polygon from points
        if len(self.points) >= 2:
            polygon = QPolygonF(self.points)

            # Create preview item
            self.polygon_item = QGraphicsPolygonItem(polygon)
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine)
            self.polygon_item.setPen(pen)
            self.polygon_item.setBrush(QColor(0, 120, 215, 30))

            self.editor.scene.addItem(self.polygon_item)

    def _draw_preview_line(self, cursor_pos: QPointF):
        """Draw line from last point to cursor."""
        # This would be implemented with a temporary line item
        pass

    def _complete_selection(self):
        """Complete polygon and create selection."""
        if len(self.points) < 3:
            return

        # Convert points to numpy array
        points_array = np.array([[p.x(), p.y()]
                                for p in self.points], dtype=np.int32)

        # Create mask from polygon
        if self.editor.selection_mask is not None:
            h, w = self.editor.selection_mask.shape
            mask = np.zeros((h, w), dtype=np.uint8)

            # Fill polygon
            cv2.fillPoly(mask, [points_array], 255)

            # Apply to editor
            from PyQt6.QtWidgets import QApplication
            modifiers = QApplication.keyboardModifiers()

            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                # Add to selection
                self.editor.selection_mask = np.maximum(
                    self.editor.selection_mask, mask)
            elif modifiers & Qt.KeyboardModifier.AltModifier:
                # Subtract from selection
                self.editor.selection_mask = np.maximum(
                    0, self.editor.selection_mask - mask)
            else:
                # Replace selection
                self.editor.selection_mask = mask

            self.editor.mask_updated.emit()
            logger.info(
                f"Polygon lasso: Selection created with {len(self.points)} points")

        self._clear_preview()
        self.is_active = False

    def _cancel_selection(self):
        """Cancel polygon selection."""
        self._clear_preview()
        self.is_active = False
        logger.debug("Polygon lasso: Selection cancelled")

    def _clear_preview(self):
        """Clear polygon preview."""
        self.points = []

        if self.polygon_item:
            self.editor.scene.removeItem(self.polygon_item)
            self.polygon_item = None
