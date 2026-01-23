"""Clone Stamp Tool - Professional implementation.

Sample from one area and paint to another, essential for textile pattern creation.
"""

import logging

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPainter

from sj_das.tools.base import Tool

logger = logging.getLogger(__name__)


class CloneStampTool(Tool):
    """
    Professional clone stamp tool for textile design.

    Features:
    - Alt+Click to set source point
    - Click+drag to clone from source
    - Aligned mode: source moves with brush
    - Non-aligned mode: fixed source
    - Opacity control
    """

    def __init__(self, editor):
        """Initialize clone stamp tool."""
        super().__init__(editor)
        self.source_point = None
        self.aligned = True
        self.opacity = 100
        self.offset = None
        self.is_sampling = False
        self.last_paint_point = None

    def mouse_press(self, pos: QPointF, buttons: Qt.MouseButton):
        """Handle mouse press - sample or start cloning."""
        from PyQt6.QtWidgets import QApplication

        # Check if Alt key is pressed (sample mode)
        if QApplication.keyboardModifiers() & Qt.KeyboardModifier.AltModifier:
            # Set source point
            self.source_point = pos
            self.is_sampling = True
            logger.info(f"Clone source set at ({pos.x():.0f}, {pos.y():.0f})")
            return

        if self.source_point is None:
            logger.warning(
                "Clone stamp: No source point set. Hold Alt and click to set source.")
            return

        # Start cloning
        if self.aligned and self.offset is None:
            # Calculate offset on first paint
            self.offset = QPointF(pos.x() - self.source_point.x(),
                                  pos.y() - self.source_point.y())

        self._clone_at_point(pos)
        self.last_paint_point = pos

    def mouse_move(self, pos: QPointF, buttons: Qt.MouseButton):
        """Handle mouse move - continuous cloning."""
        if not (buttons & Qt.MouseButton.LeftButton):
            return

        if self.is_sampling:
            return

        if self.source_point is None:
            return

        # Clone at current position
        self._clone_at_point(pos)
        self.last_paint_point = pos

    def mouse_release(self, pos: QPointF, buttons: Qt.MouseButton):
        """Handle mouse release."""
        if self.is_sampling:
            self.is_sampling = False
            return

        if not self.aligned:
            # Reset offset for non-aligned mode
            self.offset = None

        self.last_paint_point = None

    def _clone_at_point(self, dest_point: QPointF):
        """Clone from source to destination point."""
        if not self.editor.original_image:
            return

        # Calculate source position
        if self.aligned and self.offset:
            source_x = dest_point.x() - self.offset.x()
            source_y = dest_point.y() - self.offset.y()
        else:
            source_x = self.source_point.x()
            source_y = self.source_point.y()

        # Get brush size
        brush_size = self.editor.brush_size
        half_size = brush_size // 2

        # Convert QImage to numpy for sampling
        width = self.editor.original_image.width()
        height = self.editor.original_image.height()

        # Get source region
        src_x = int(source_x - half_size)
        src_y = int(source_y - half_size)

        # Get destination region
        dst_x = int(dest_point.x() - half_size)
        dst_y = int(dest_point.y() - half_size)

        # Bounds checking
        if (src_x < 0 or src_y < 0 or src_x + brush_size > width or src_y + brush_size > height or
                dst_x < 0 or dst_y < 0 or dst_x + brush_size > width or dst_y + brush_size > height):
            return

        # Sample from source

        # Create stamp from source area
        stamp = self.editor.original_image.copy(
            src_x, src_y, brush_size, brush_size)

        # Paint stamp to destination on mask layer
        painter = QPainter(self.editor.mask_image)

        # Apply opacity
        painter.setOpacity(self.opacity / 100.0)

        # Draw stamp
        painter.drawImage(dst_x, dst_y, stamp)
        painter.end()

        # Update display
        self.editor._update_scene()
