"""
Advanced Selection Tools for SJ-DAS.

Photoshop-quality selection tools including Magic Wand, Quick Selection,
and Color Range selection with tolerance and anti-aliasing.
"""

import logging
from typing import Optional, Tuple

import cv2
import numpy as np
from PyQt6.QtCore import QPoint, QRect
from PyQt6.QtGui import QColor, QImage

logger = logging.getLogger("SJ_DAS.SelectionTools")


class MagicWandTool:
    """
    Enhanced Magic Wand tool with tolerance and anti-aliasing.

    Features:
        - Adjustable tolerance (0-255)
        - Contiguous/Non-contiguous mode
        - Anti-aliasing
        - Sample all layers option
    """

    def __init__(self):
        self.tolerance = 32
        self.contiguous = True
        self.anti_alias = True
        self.sample_all_layers = False

    def select(
        self,
        image: QImage,
        point: QPoint,
        tolerance: Optional[int] = None
    ) -> np.ndarray:
        """
        Create selection using magic wand.

        Args:
            image: Source image
            point: Click point
            tolerance: Color tolerance (0-255)

        Returns:
            Selection mask (numpy array)
        """
        if tolerance is not None:
            self.tolerance = tolerance

        # Convert QImage to numpy
        img_array = self._qimage_to_numpy(image)

        # Get seed color
        x, y = point.x(), point.y()
        if x < 0 or y < 0 or x >= img_array.shape[1] or y >= img_array.shape[0]:
            return np.zeros(img_array.shape[:2], dtype=np.uint8)

        seed_color = img_array[y, x]

        # Create mask
        if self.contiguous:
            mask = self._flood_fill_select(img_array, (x, y), seed_color)
        else:
            mask = self._color_range_select(img_array, seed_color)

        # Apply anti-aliasing
        if self.anti_alias:
            mask = cv2.GaussianBlur(mask, (3, 3), 0)

        logger.debug(
            f"Magic wand selection: {np.sum(mask > 0)} pixels selected")
        return mask

    def _flood_fill_select(
        self,
        image: np.ndarray,
        seed: Tuple[int, int],
        seed_color: np.ndarray
    ) -> np.ndarray:
        """Flood fill selection (contiguous)."""
        h, w = image.shape[:2]
        mask = np.zeros((h + 2, w + 2), dtype=np.uint8)

        # Calculate color difference threshold
        lo_diff = (self.tolerance,) * 3
        up_diff = (self.tolerance,) * 3

        # Flood fill
        cv2.floodFill(
            image.copy(),
            mask,
            seed,
            (255, 255, 255),
            lo_diff,
            up_diff,
            cv2.FLOODFILL_MASK_ONLY
        )

        return mask[1:-1, 1:-1]

    def _color_range_select(
        self,
        image: np.ndarray,
        seed_color: np.ndarray
    ) -> np.ndarray:
        """Color range selection (non-contiguous)."""
        # Calculate color distance
        diff = np.abs(image.astype(np.float32) - seed_color.astype(np.float32))
        distance = np.sqrt(np.sum(diff ** 2, axis=2))

        # Create mask based on tolerance
        mask = (distance <= self.tolerance).astype(np.uint8) * 255

        return mask

    def _qimage_to_numpy(self, qimage: QImage) -> np.ndarray:
        """Convert QImage to numpy array."""
        qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(height * width * 3)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
        return arr.copy()


class QuickSelectionTool:
    """
    AI-powered quick selection tool.

    Features:
        - Brush-based selection
        - Edge detection
        - Intelligent region growing
        - Add/Subtract modes
    """

    def __init__(self):
        self.brush_size = 20
        self.mode = "add"  # add, subtract
        self.edge_threshold = 50

    def select(
        self,
        image: QImage,
        strokes: list[list[QPoint]],
        existing_mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Create selection from brush strokes.

        Args:
            image: Source image
            strokes: List of stroke paths
            existing_mask: Existing selection to modify

        Returns:
            Updated selection mask
        """
        img_array = self._qimage_to_numpy(image)
        h, w = img_array.shape[:2]

        if existing_mask is None:
            mask = np.zeros((h, w), dtype=np.uint8)
        else:
            mask = existing_mask.copy()

        # Detect edges for intelligent selection
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, self.edge_threshold, self.edge_threshold * 2)

        # Process each stroke
        for stroke in strokes:
            stroke_mask = self._process_stroke(img_array, edges, stroke)

            if self.mode == "add":
                mask = cv2.bitwise_or(mask, stroke_mask)
            else:  # subtract
                mask = cv2.bitwise_and(mask, cv2.bitwise_not(stroke_mask))

        logger.debug(f"Quick selection: {np.sum(mask > 0)} pixels selected")
        return mask

    def _process_stroke(
        self,
        image: np.ndarray,
        edges: np.ndarray,
        stroke: list[QPoint]
    ) -> np.ndarray:
        """Process single stroke."""
        h, w = image.shape[:2]
        stroke_mask = np.zeros((h, w), dtype=np.uint8)

        # Draw stroke path
        for i in range(len(stroke) - 1):
            p1 = stroke[i]
            p2 = stroke[i + 1]
            cv2.line(
                stroke_mask,
                (p1.x(), p1.y()),
                (p2.x(), p2.y()),
                255,
                self.brush_size
            )

        # Grow selection to edges
        stroke_mask = self._grow_to_edges(image, edges, stroke_mask)

        return stroke_mask

    def _grow_to_edges(
        self,
        image: np.ndarray,
        edges: np.ndarray,
        seed_mask: np.ndarray
    ) -> np.ndarray:
        """Grow selection until hitting edges."""
        # Use watershed or region growing
        # Simplified version: dilate until edges
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        grown = seed_mask.copy()

        for _ in range(10):  # Max iterations
            dilated = cv2.dilate(grown, kernel)
            # Stop at edges
            dilated[edges > 0] = 0
            if np.array_equal(dilated, grown):
                break
            grown = dilated

        return grown

    def _qimage_to_numpy(self, qimage: QImage) -> np.ndarray:
        """Convert QImage to numpy array."""
        qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(height * width * 3)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
        return arr.copy()


class ColorRangeSelector:
    """
    Select by color range.

    Features:
        - HSV-based selection
        - Fuzziness control
        - Preview mode
        - Invert selection
    """

    def __init__(self):
        self.fuzziness = 40
        self.use_hsv = True
        self.invert = False

    def show_dialog(self):
        """Show parameters dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Color Range",
            "Color Range Selector settings coming soon.\nUsing defaults: Fuzziness=40")

    def select_by_color(
        self,
        image: QImage,
        target_color: QColor,
        fuzziness: Optional[int] = None
    ) -> np.ndarray:
        """
        Select pixels by color range.

        Args:
            image: Source image
            target_color: Target color to select
            fuzziness: Color tolerance (0-200)

        Returns:
            Selection mask
        """
        if fuzziness is not None:
            self.fuzziness = fuzziness

        img_array = self._qimage_to_numpy(image)

        if self.use_hsv:
            mask = self._select_hsv(img_array, target_color)
        else:
            mask = self._select_rgb(img_array, target_color)

        if self.invert:
            mask = cv2.bitwise_not(mask)

        logger.debug(
            f"Color range selection: {np.sum(mask > 0)} pixels selected")
        return mask

    def _select_hsv(self, image: np.ndarray,
                    target_color: QColor) -> np.ndarray:
        """Select using HSV color space."""
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Convert target color to HSV
        target_rgb = np.uint8(
            [[[target_color.red(), target_color.green(), target_color.blue()]]])
        target_hsv = cv2.cvtColor(target_rgb, cv2.COLOR_RGB2HSV)[0][0]

        # Define range
        h_range = self.fuzziness // 2
        s_range = self.fuzziness
        v_range = self.fuzziness

        lower = np.array([
            max(0, target_hsv[0] - h_range),
            max(0, target_hsv[1] - s_range),
            max(0, target_hsv[2] - v_range)
        ])

        upper = np.array([
            min(179, target_hsv[0] + h_range),
            min(255, target_hsv[1] + s_range),
            min(255, target_hsv[2] + v_range)
        ])

        # Create mask
        mask = cv2.inRange(hsv, lower, upper)

        return mask

    def _select_rgb(self, image: np.ndarray,
                    target_color: QColor) -> np.ndarray:
        """Select using RGB color space."""
        target = np.array(
            [target_color.red(), target_color.green(), target_color.blue()])

        # Calculate color distance
        diff = np.abs(image.astype(np.float32) - target.astype(np.float32))
        distance = np.sqrt(np.sum(diff ** 2, axis=2))

        # Create mask
        mask = (distance <= self.fuzziness).astype(np.uint8) * 255

        return mask

    def _qimage_to_numpy(self, qimage: QImage) -> np.ndarray:
        """Convert QImage to numpy array."""
        qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(height * width * 3)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
        return arr.copy()


class SelectionRefiner:
    """
    Refine selection edges (Select and Mask).

    Features:
        - Edge refinement
        - Feathering
        - Smoothing
        - Smoothing
        - Contrast adjustment
    """

    def show_dialog(self):
        """Show parameters dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Refine Edge",
            "Refine Edge settings coming soon.")

    def refine_edge(
        self,
        mask: np.ndarray,
        radius: int = 5,
        smooth: int = 3,
        feather: float = 0.0,
        contrast: int = 0
    ) -> np.ndarray:
        """
        Refine selection edges.

        Args:
            mask: Input selection mask
            radius: Edge detection radius
            smooth: Smoothing amount
            feather: Feather amount (pixels)
            contrast: Edge contrast adjustment

        Returns:
            Refined mask
        """
        refined = mask.copy()

        # Smooth edges
        if smooth > 0:
            kernel_size = smooth * 2 + 1
            refined = cv2.GaussianBlur(refined, (kernel_size, kernel_size), 0)

        # Feather
        if feather > 0:
            kernel = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE,
                (int(feather * 2), int(feather * 2))
            )
            refined = cv2.morphologyEx(refined, cv2.MORPH_GRADIENT, kernel)

        # Adjust contrast
        if contrast != 0:
            refined = cv2.convertScaleAbs(refined, alpha=1 + contrast / 100.0)

        logger.debug("Selection edges refined")
        return refined
