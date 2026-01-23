"""Selection Manager for Selection Mask Operations.

Manages selection masks with support for multiple operation modes
and visual feedback rendering.
"""

import logging

import numpy as np
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor, QImage

logger = logging.getLogger(__name__)


class SelectionManager:
    """
    Professional selection management system.

    Handles selection masks with support for add/subtract/replace modes,
    providing photoshop-like selection functionality.

    Features:
    - Multiple operation modes (replace/add/subtract)
    - Rectangular and flood-fill selections
    - Visual feedback rendering
    - Selection inversion and clearing

    Attributes:
        selection_mask: Binary mask (255=selected, 0=not selected)
        width: Selection mask width
        height: Selection mask height
    """

    def __init__(self, width: int = 0, height: int = 0):
        """
        Initialize selection manager.

        Args:
            width: Initial mask width
            height: Initial mask height
        """
        self.width = width
        self.height = height
        self.selection_mask: np.ndarray | None = None

        if width > 0 and height > 0:
            self.clear_selection()

        logger.debug(f"Initialized SelectionManager: {width}x{height}")

    def resize(self, width: int, height: int) -> None:
        """
        Resize selection mask.

        Args:
            width: New width
            height: New height
        """
        self.width = width
        self.height = height
        self.clear_selection()

        logger.debug(f"Resized selection mask: {width}x{height}")

    def clear_selection(self) -> None:
        """Clear selection (nothing selected)."""
        self.selection_mask = np.zeros(
            (self.height, self.width), dtype=np.uint8)

    def select_all(self) -> None:
        """Select entire canvas."""
        self.selection_mask = np.full(
            (self.height, self.width),
            255,
            dtype=np.uint8
        )

    def invert_selection(self) -> None:
        """Invert current selection."""
        if self.selection_mask is not None:
            self.selection_mask = 255 - self.selection_mask

    def apply_rect_selection(
        self,
        start: QPointF,
        end: QPointF,
        mode: str = "replace"
    ) -> None:
        """
        Apply rectangular selection.

        Args:
            start: Selection rectangle start point
            end: Selection rectangle end point
            mode: Operation mode ("replace", "add", "subtract")
        """
        if self.selection_mask is None:
            self.clear_selection()

        # Convert to pixel coordinates
        x1, y1 = int(start.x()), int(start.y())
        x2, y2 = int(end.x()), int(end.y())

        # Ensure correct order
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # Clip to bounds
        x1 = max(0, min(x1, self.width - 1))
        x2 = max(0, min(x2, self.width - 1))
        y1 = max(0, min(y1, self.height - 1))
        y2 = max(0, min(y2, self.height - 1))

        # Create rectangle mask
        rect_mask = np.zeros((self.height, self.width), dtype=np.uint8)
        rect_mask[y1:y2 + 1, x1:x2 + 1] = 255

        # Apply based on mode
        if mode == "replace":
            self.selection_mask = rect_mask
        elif mode == "add":
            self.selection_mask = np.maximum(self.selection_mask, rect_mask)
        elif mode == "subtract":
            self.selection_mask = np.where(
                rect_mask == 255, 0, self.selection_mask)

        logger.debug(
            f"Applied rect selection: ({x1},{y1})-({x2},{y2}), mode={mode}")

    def apply_magic_wand(
        self,
        point: QPointF,
        tolerance: int,
        source_image: QImage
    ) -> None:
        """
        Apply magic wand (flood fill) selection.

        Args:
            point: Click point
            tolerance: Color matching tolerance
            source_image: Source image for color sampling
        """
        if self.selection_mask is None:
            self.clear_selection()

        x, y = int(point.x()), int(point.y())

        # Validate coordinates
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        # Get target color
        target_color = source_image.pixelColor(x, y)

        # Simple flood fill implementation
        # Note: This is a basic version, could be optimized
        visited = np.zeros((self.height, self.width), dtype=bool)
        to_visit = [(x, y)]

        while to_visit:
            cx, cy = to_visit.pop()

            if visited[cy, cx]:
                continue

            if not (0 <= cx < self.width and 0 <= cy < self.height):
                continue

            # Check color similarity
            current_color = source_image.pixelColor(cx, cy)
            if not self._colors_similar(
                    target_color, current_color, tolerance):
                continue

            # Mark as selected
            visited[cy, cx] = True
            self.selection_mask[cy, cx] = 255

            # Add neighbors
            to_visit.extend([
                (cx + 1, cy), (cx - 1, cy),
                (cx, cy + 1), (cx, cy - 1)
            ])

        logger.debug(f"Applied magic wand at ({x},{y}), tolerance={tolerance}")

    def _colors_similar(
        self,
        color1: QColor,
        color2: QColor,
        tolerance: int
    ) -> bool:
        """
        Check if two colors are similar within tolerance.

        Args:
            color1: First color
            color2: Second color
            tolerance: Acceptable difference

        Returns:
            True if colors are similar
        """
        diff_r = abs(color1.red() - color2.red())
        diff_g = abs(color1.green() - color2.green())
        diff_b = abs(color1.blue() - color2.blue())

        return (diff_r + diff_g + diff_b) <= (tolerance * 3)

    def has_selection(self) -> bool:
        """Check if any area is selected."""
        if self.selection_mask is None:
            return False
        return np.any(self.selection_mask > 0)

    def is_point_selected(self, x: int, y: int) -> bool:
        """
        Check if a point is within selection.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if point is selected
        """
        if self.selection_mask is None:
            return True  # No selection = everything selected

        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        return self.selection_mask[y, x] > 0

    def get_selection_bounds(self) -> tuple[int, int, int, int] | None:
        """
        Get bounding box of selection.

        Returns:
            (x1, y1, x2, y2) or None if no selection
        """
        if not self.has_selection():
            return None

        # Find bounds
        rows, cols = np.where(self.selection_mask > 0)

        if len(rows) == 0:
            return None

        y1, y2 = rows.min(), rows.max()
        x1, x2 = cols.min(), cols.max()

        return (x1, y1, x2, y2)
