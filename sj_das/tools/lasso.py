"""Lasso selection tool - placeholder."""

from PyQt6.QtCore import QPointF, Qt

from sj_das.tools.base import Tool


class LassoTool(Tool):
    """Lasso selection tool (freehand selection)."""

    def __init__(self, editor):
        """Initialize lasso tool."""
        super().__init__(editor)
        self.path_points = []

    def mouse_press(self, pos: QPointF, buttons: Qt.MouseButton):
        """Start lasso path."""
        self.path_points = [pos]

    def mouse_move(self, pos: QPointF, buttons: Qt.MouseButton):
        """Add point to lasso path."""
        if buttons & Qt.MouseButton.LeftButton:
            self.path_points.append(pos)

    def mouse_release(self, pos: QPointF, buttons: Qt.MouseButton):
        """Complete lasso selection."""
        try:
            if len(self.path_points) < 3:
                # Need at least 3 points for a polygon
                self.path_points = []
                return

            # Convert QPointF to numpy array for polygon selection
            import numpy as np
            from PIL import Image, ImageDraw

            # Get image dimensions
            if hasattr(
                    self.editor, 'original_image') and self.editor.original_image is not None:
                h, w = self.editor.original_image.shape[:2]

                # Create mask from lasso path
                mask = Image.new('L', (w, h), 0)
                draw = ImageDraw.Draw(mask)

                # Convert points to tuples
                polygon_points = [(int(p.x()), int(p.y()))
                                  for p in self.path_points]
                draw.polygon(polygon_points, fill=255)

                # Convert to numpy array
                mask_array = np.array(mask)

                # Apply selection to editor
                if hasattr(self.editor, 'set_selection_mask'):
                    self.editor.set_selection_mask(mask_array)

        except Exception as e:
            import logging
            logging.getLogger("SJ_DAS").error(
                f"Lasso selection failed: {e}", exc_info=True)
        finally:
            self.path_points = []
