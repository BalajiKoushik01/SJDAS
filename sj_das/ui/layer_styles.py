"""
Layer Styles for SJ-DAS.

Photoshop-quality layer effects including drop shadow, glow,
bevel & emboss, and stroke.
"""

import logging
from typing import Tuple

import cv2
import numpy as np
from PyQt6.QtGui import QColor, QImage

logger = logging.getLogger("SJ_DAS.LayerStyles")


class LayerStyles:
    """
    Photoshop-style layer effects.

    Supported effects:
        - Drop Shadow
        - Inner Shadow
        - Outer Glow
        - Inner Glow
        - Bevel and Emboss
        - Stroke
    """

    @staticmethod
    def add_drop_shadow(
        layer: np.ndarray,
        distance: int = 5,
        angle: int = 135,
        blur: int = 5,
        opacity: float = 0.75,
        color: Tuple[int, int, int] = (0, 0, 0)
    ) -> np.ndarray:
        """
        Add drop shadow effect.

        Args:
            layer: Input layer (RGBA)
            distance: Shadow distance in pixels
            angle: Shadow angle in degrees
            blur: Shadow blur radius
            opacity: Shadow opacity (0-1)
            color: Shadow color (R, G, B)

        Returns:
            Layer with drop shadow
        """
        h, w = layer.shape[:2]

        # Calculate shadow offset
        angle_rad = np.radians(angle)
        offset_x = int(distance * np.cos(angle_rad))
        offset_y = int(distance * np.sin(angle_rad))

        # Create shadow layer
        shadow = np.zeros((h, w, 4), dtype=np.uint8)

        # Extract alpha channel
        if layer.shape[2] == 4:
            alpha = layer[:, :, 3]
        else:
            alpha = np.ones((h, w), dtype=np.uint8) * 255

        # Create shadow from alpha
        shadow_alpha = alpha.copy()

        # Blur shadow
        if blur > 0:
            shadow_alpha = cv2.GaussianBlur(
                shadow_alpha, (blur * 2 + 1, blur * 2 + 1), 0)

        # Apply opacity
        shadow_alpha = (shadow_alpha * opacity).astype(np.uint8)

        # Set shadow color
        shadow[:, :, 0] = color[2]  # B
        shadow[:, :, 1] = color[1]  # G
        shadow[:, :, 2] = color[0]  # R
        shadow[:, :, 3] = shadow_alpha

        # Offset shadow
        M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
        shadow = cv2.warpAffine(shadow, M, (w, h))

        # Composite shadow under layer
        result = LayerStyles._composite_layers(shadow, layer)

        logger.debug(f"Added drop shadow: distance={distance}, angle={angle}")
        return result

    @staticmethod
    def show_dialog():
        """Show parameters dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Layer Styles",
            "Layer Styles dialog coming soon.")

    @staticmethod
    def add_outer_glow(
        layer: np.ndarray,
        size: int = 10,
        color: Tuple[int, int, int] = (255, 255, 0),
        opacity: float = 0.75
    ) -> np.ndarray:
        """
        Add outer glow effect.

        Args:
            layer: Input layer (RGBA)
            size: Glow size in pixels
            color: Glow color (R, G, B)
            opacity: Glow opacity (0-1)

        Returns:
            Layer with outer glow
        """
        h, w = layer.shape[:2]

        # Extract alpha
        if layer.shape[2] == 4:
            alpha = layer[:, :, 3]
        else:
            alpha = np.ones((h, w), dtype=np.uint8) * 255

        # Create glow
        glow = np.zeros((h, w, 4), dtype=np.uint8)
        glow[:, :, 0] = color[2]  # B
        glow[:, :, 1] = color[1]  # G
        glow[:, :, 2] = color[0]  # R

        # Dilate alpha for glow
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (size * 2, size * 2))
        glow_alpha = cv2.dilate(alpha, kernel)

        # Blur glow
        glow_alpha = cv2.GaussianBlur(
            glow_alpha, (size * 2 + 1, size * 2 + 1), 0)

        # Apply opacity
        glow_alpha = (glow_alpha * opacity).astype(np.uint8)
        glow[:, :, 3] = glow_alpha

        # Composite glow under layer
        result = LayerStyles._composite_layers(glow, layer)

        logger.debug(f"Added outer glow: size={size}")
        return result

    @staticmethod
    def add_bevel_emboss(
        layer: np.ndarray,
        depth: int = 5,
        size: int = 5,
        angle: int = 135,
        altitude: int = 30
    ) -> np.ndarray:
        """
        Add bevel and emboss effect.

        Args:
            layer: Input layer (RGBA)
            depth: Effect depth
            size: Bevel size
            angle: Light angle
            altitude: Light altitude

        Returns:
            Layer with bevel and emboss
        """
        if layer.shape[2] == 4:
            rgb = layer[:, :, :3]
            alpha = layer[:, :, 3]
        else:
            rgb = layer
            alpha = np.ones(layer.shape[:2], dtype=np.uint8) * 255

        # Convert to grayscale for emboss
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        # Create emboss kernel
        angle_rad = np.radians(angle)
        kx = int(np.cos(angle_rad) * size)
        ky = int(np.sin(angle_rad) * size)

        # Sobel-based emboss
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=size)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=size)

        # Combine gradients
        emboss = sobelx * np.cos(angle_rad) + sobely * np.sin(angle_rad)
        emboss = emboss * depth / 100.0

        # Normalize and apply
        emboss = np.clip(emboss + 128, 0, 255).astype(np.uint8)

        # Blend with original
        result = cv2.addWeighted(
            rgb, 0.7, cv2.cvtColor(
                emboss, cv2.COLOR_GRAY2RGB), 0.3, 0)

        # Restore alpha
        if layer.shape[2] == 4:
            result = np.dstack([result, alpha])

        logger.debug(f"Added bevel and emboss: depth={depth}, size={size}")
        return result

    @staticmethod
    def add_stroke(
        layer: np.ndarray,
        size: int = 3,
        color: Tuple[int, int, int] = (0, 0, 0),
        position: str = "outside"  # outside, inside, center
    ) -> np.ndarray:
        """
        Add stroke outline.

        Args:
            layer: Input layer (RGBA)
            size: Stroke width
            color: Stroke color (R, G, B)
            position: Stroke position

        Returns:
            Layer with stroke
        """
        h, w = layer.shape[:2]

        # Extract alpha
        if layer.shape[2] == 4:
            alpha = layer[:, :, 3]
        else:
            alpha = np.ones((h, w), dtype=np.uint8) * 255

        # Create stroke
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (size * 2 + 1, size * 2 + 1))

        if position == "outside":
            stroke_alpha = cv2.dilate(alpha, kernel) - alpha
        elif position == "inside":
            stroke_alpha = alpha - cv2.erode(alpha, kernel)
        else:  # center
            dilated = cv2.dilate(alpha, kernel)
            eroded = cv2.erode(alpha, kernel)
            stroke_alpha = dilated - eroded

        # Create stroke layer
        stroke = np.zeros((h, w, 4), dtype=np.uint8)
        stroke[:, :, 0] = color[2]  # B
        stroke[:, :, 1] = color[1]  # G
        stroke[:, :, 2] = color[0]  # R
        stroke[:, :, 3] = stroke_alpha

        # Composite
        if position == "outside":
            result = LayerStyles._composite_layers(stroke, layer)
        else:
            result = LayerStyles._composite_layers(layer, stroke)

        logger.debug(f"Added stroke: size={size}, position={position}")
        return result

    @staticmethod
    def _composite_layers(bottom: np.ndarray, top: np.ndarray) -> np.ndarray:
        """Composite two RGBA layers."""
        if bottom.shape[2] != 4 or top.shape[2] != 4:
            raise ValueError("Both layers must be RGBA")

        # Normalize alpha to 0-1
        alpha_top = top[:, :, 3:4] / 255.0
        alpha_bottom = bottom[:, :, 3:4] / 255.0

        # Composite RGB
        rgb_top = top[:, :, :3]
        rgb_bottom = bottom[:, :, :3]

        rgb_result = rgb_top * alpha_top + \
            rgb_bottom * alpha_bottom * (1 - alpha_top)

        # Composite alpha
        alpha_result = alpha_top + alpha_bottom * (1 - alpha_top)

        # Combine
        result = np.dstack([rgb_result, alpha_result * 255]).astype(np.uint8)

        return result
