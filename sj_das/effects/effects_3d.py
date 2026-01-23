"""
3D Capabilities for SJ-DAS.

Basic 3D text and shape rendering for professional effects.
"""

import logging
from typing import Tuple

import cv2
import numpy as np
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPainterPath

logger = logging.getLogger("SJ_DAS.3D")


class Text3D:
    """
    3D text rendering.

    Features:
        - Extrude text
        - Bevel edges
        - Lighting effects
        - Material properties
    """

    def __init__(self):
        self.extrude_depth = 20
        self.bevel_depth = 5
        self.light_angle = 45
        self.light_intensity = 0.8

    def extrude_text(
        self,
        text: str,
        font: QFont,
        depth: int = 20,
        bevel: int = 5,
        color: QColor = QColor(100, 100, 200)
    ) -> np.ndarray:
        """
        Create 3D extruded text.

        Args:
            text: Text to render
            font: Font to use
            depth: Extrusion depth in pixels
            bevel: Bevel depth
            color: Base color

        Returns:
            RGBA image with 3D text
        """
        # Render base text
        base_image = self._render_text(text, font, color)
        h, w = base_image.shape[:2]

        # Create 3D effect by layering
        result = np.zeros((h + depth, w + depth, 4), dtype=np.uint8)

        # Draw extrusion layers
        for i in range(depth, 0, -1):
            # Calculate lighting for this layer
            layer_brightness = 1.0 - (i / depth) * 0.5
            layer_color = QColor(
                int(color.red() * layer_brightness),
                int(color.green() * layer_brightness),
                int(color.blue() * layer_brightness)
            )

            # Render layer
            layer = self._render_text(text, font, layer_color)

            # Place layer with offset
            offset = depth - i
            result[offset:offset + h, offset:offset + w] = self._blend_layers(
                result[offset:offset + h, offset:offset + w],
                layer
            )

        # Add front face (brightest)
        result[0:h, 0:w] = self._blend_layers(
            result[0:h, 0:w],
            base_image
        )

        # Add bevel if requested
        if bevel > 0:
            result = self._add_bevel(result, bevel)

        logger.debug(f"Created 3D text: '{text}' with depth={depth}")
        return result

    def _render_text(
        self,
        text: str,
        font: QFont,
        color: QColor
    ) -> np.ndarray:
        """Render 2D text to image."""
        # Estimate size
        from PyQt6.QtGui import QFontMetrics
        metrics = QFontMetrics(font)
        rect = metrics.boundingRect(text)

        w = rect.width() + 20
        h = rect.height() + 20

        # Create image
        image = QImage(w, h, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        # Draw text
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(10, h - 10, text)
        painter.end()

        # Convert to numpy
        ptr = image.bits()
        ptr.setsize(h * w * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((h, w, 4))

        return arr.copy()

    def _blend_layers(
        self,
        bottom: np.ndarray,
        top: np.ndarray
    ) -> np.ndarray:
        """Blend two RGBA layers."""
        if bottom.shape != top.shape:
            return top

        # Alpha compositing
        alpha_top = top[:, :, 3:4] / 255.0
        alpha_bottom = bottom[:, :, 3:4] / 255.0

        rgb_top = top[:, :, :3]
        rgb_bottom = bottom[:, :, :3]

        # Composite
        rgb_result = rgb_top * alpha_top + \
            rgb_bottom * alpha_bottom * (1 - alpha_top)
        alpha_result = alpha_top + alpha_bottom * (1 - alpha_top)

        result = np.dstack([rgb_result, alpha_result * 255]).astype(np.uint8)
        return result

    def _add_bevel(self, image: np.ndarray, bevel_depth: int) -> np.ndarray:
        """Add bevel effect to edges."""
        # Extract alpha for edge detection
        alpha = image[:, :, 3]

        # Detect edges
        edges = cv2.Canny(alpha, 50, 150)

        # Dilate edges for bevel area
        kernel = np.ones((bevel_depth, bevel_depth), np.uint8)
        bevel_mask = cv2.dilate(edges, kernel)

        # Apply highlight to bevel
        result = image.copy()
        result[bevel_mask > 0, :3] = np.minimum(
            result[bevel_mask > 0, :3].astype(int) + 30,
            255
        ).astype(np.uint8)

        return result

    def show_dialog(self):
        """Show parameters dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Convert to 3D",
            "3D Text tool coming soon.")


class Shapes3D:
    """
    3D shape primitives.

    Shapes:
        - Cube
        - Sphere
        - Cylinder
        - Cone
    """

    @staticmethod
    def create_cube(
        size: int = 100,
        color: QColor = QColor(150, 150, 200)
    ) -> np.ndarray:
        """
        Create 3D cube.

        Args:
            size: Cube size in pixels
            color: Base color

        Returns:
            RGBA image with 3D cube
        """
        # Create isometric cube
        w = int(size * 2)
        h = int(size * 1.5)

        image = np.zeros((h, w, 4), dtype=np.uint8)

        # Define cube vertices (isometric projection)
        # Top face
        top_pts = np.array([
            [w // 2, h // 4],
            [w // 4, h // 3],
            [w // 2, h // 2],
            [3 * w // 4, h // 3]
        ], dtype=np.int32)

        # Left face
        left_pts = np.array([
            [w // 4, h // 3],
            [w // 2, h // 2],
            [w // 2, 3 * h // 4],
            [w // 4, 2 * h // 3]
        ], dtype=np.int32)

        # Right face
        right_pts = np.array([
            [w // 2, h // 2],
            [3 * w // 4, h // 3],
            [3 * w // 4, 2 * h // 3],
            [w // 2, 3 * h // 4]
        ], dtype=np.int32)

        # Draw faces with different shading
        # Top (lightest)
        cv2.fillPoly(image, [top_pts], (
            color.red(),
            color.green(),
            color.blue(),
            255
        ))

        # Left (medium)
        left_color = (
            int(color.red() * 0.7),
            int(color.green() * 0.7),
            int(color.blue() * 0.7),
            255
        )
        cv2.fillPoly(image, [left_pts], left_color)

        # Right (darkest)
        right_color = (
            int(color.red() * 0.5),
            int(color.green() * 0.5),
            int(color.blue() * 0.5),
            255
        )
        cv2.fillPoly(image, [right_pts], right_color)

        # Draw edges
        cv2.polylines(image, [top_pts], True, (0, 0, 0, 255), 2)
        cv2.polylines(image, [left_pts], True, (0, 0, 0, 255), 2)
        cv2.polylines(image, [right_pts], True, (0, 0, 0, 255), 2)

        logger.debug(f"Created 3D cube: size={size}")
        return image

    @staticmethod
    def create_sphere(
        radius: int = 50,
        color: QColor = QColor(150, 150, 200)
    ) -> np.ndarray:
        """Create 3D sphere with shading."""
        size = radius * 2 + 20
        image = np.zeros((size, size, 4), dtype=np.uint8)

        center = (size // 2, size // 2)

        # Draw sphere with gradient shading
        for y in range(size):
            for x in range(size):
                dx = x - center[0]
                dy = y - center[1]
                dist = np.sqrt(dx**2 + dy**2)

                if dist <= radius:
                    # Calculate shading based on distance from center
                    # Simulate light from top-left
                    light_x = -radius * 0.3
                    light_y = -radius * 0.3

                    light_dist = np.sqrt((dx - light_x)**2 + (dy - light_y)**2)
                    brightness = 1.0 - (light_dist / (radius * 1.5))
                    brightness = max(0.3, min(1.0, brightness))

                    # Apply brightness to color
                    image[y, x] = [
                        int(color.red() * brightness),
                        int(color.green() * brightness),
                        int(color.blue() * brightness),
                        255
                    ]

        logger.debug(f"Created 3D sphere: radius={radius}")
        return image

    @staticmethod
    def create_cylinder(
        radius: int = 40,
        height: int = 100,
        color: QColor = QColor(150, 150, 200)
    ) -> np.ndarray:
        """Create 3D cylinder."""
        w = radius * 2 + 20
        h = height + radius + 20

        image = np.zeros((h, w, 4), dtype=np.uint8)

        center_x = w // 2
        top_y = radius + 10
        bottom_y = top_y + height

        # Draw cylinder body (rectangle with shading)
        for y in range(top_y, bottom_y):
            for x in range(center_x - radius, center_x + radius):
                dx = abs(x - center_x)
                brightness = 1.0 - (dx / radius) * 0.5

                image[y, x] = [
                    int(color.red() * brightness),
                    int(color.green() * brightness),
                    int(color.blue() * brightness),
                    255
                ]

        # Draw top ellipse
        cv2.ellipse(
            image,
            (center_x, top_y),
            (radius, radius // 3),
            0, 0, 360,
            (color.red(), color.green(), color.blue(), 255),
            -1
        )

        # Draw bottom ellipse (darker)
        bottom_color = (
            int(color.red() * 0.6),
            int(color.green() * 0.6),
            int(color.blue() * 0.6),
            255
        )
        cv2.ellipse(
            image,
            (center_x, bottom_y),
            (radius, radius // 3),
            0, 0, 360,
            bottom_color,
            -1
        )

        logger.debug(f"Created 3D cylinder: radius={radius}, height={height}")
        return image
