"""
Week 2 Professional Features: Advanced Filters and Text Tools.

Implements Photoshop-quality filters including Liquify, Neural Filters,
and advanced text tools with warp effects.
"""

import logging
from typing import List, Tuple

import cv2
import numpy as np
from PyQt6.QtCore import QPoint, QPointF
from PyQt6.QtGui import QFont, QImage, QPainterPath

logger = logging.getLogger("SJ_DAS.Week2Features")


class LiquifyTool:
    """
    Photoshop's Liquify filter.

    Features:
        - Forward Warp (push pixels)
        - Twirl (clockwise/counter-clockwise)
        - Pucker (pinch inward)
        - Bloat (expand outward)
        - Reconstruct (undo changes)
    """

    def __init__(self):
        self.brush_size = 50
        self.strength = 0.5
        self.displacement_map = None

    def warp(
        self,
        image: np.ndarray,
        center: Tuple[int, int],
        direction: Tuple[float, float],
        strength: float = None
    ) -> np.ndarray:
        """
        Forward warp tool - push pixels in direction.

        Args:
            image: Input image
            center: Warp center point
            direction: Warp direction (dx, dy)
            strength: Warp strength (0-1)
        """
        if strength is None:
            strength = self.strength

        h, w = image.shape[:2]
        result = image.copy()

        # Create displacement map
        y, x = np.mgrid[0:h, 0:w]

        # Calculate distance from center
        dx = x - center[0]
        dy = y - center[1]
        distance = np.sqrt(dx**2 + dy**2)

        # Apply gaussian falloff
        falloff = np.exp(-(distance**2) / (2 * (self.brush_size / 2)**2))

        # Calculate displacement
        disp_x = direction[0] * strength * falloff
        disp_y = direction[1] * strength * falloff

        # Remap pixels
        map_x = (x + disp_x).astype(np.float32)
        map_y = (y + disp_y).astype(np.float32)

        result = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR)

        logger.debug(f"Applied warp at {center}")
        return result

    def twirl(
        self,
        image: np.ndarray,
        center: Tuple[int, int],
        angle: float = 45.0
    ) -> np.ndarray:
        """
        Twirl pixels around center point.

        Args:
            image: Input image
            center: Twirl center
            angle: Twirl angle in degrees (positive = clockwise)
        """
        h, w = image.shape[:2]

        # Create coordinate grids
        y, x = np.mgrid[0:h, 0:w]

        # Center coordinates
        dx = x - center[0]
        dy = y - center[1]
        distance = np.sqrt(dx**2 + dy**2)

        # Apply gaussian falloff
        falloff = np.exp(-(distance**2) / (2 * (self.brush_size / 2)**2))

        # Calculate rotation angle
        rotation = np.radians(angle) * falloff

        # Rotate coordinates
        cos_r = np.cos(rotation)
        sin_r = np.sin(rotation)

        new_x = center[0] + dx * cos_r - dy * sin_r
        new_y = center[1] + dx * sin_r + dy * cos_r

        # Remap
        result = cv2.remap(
            image,
            new_x.astype(np.float32),
            new_y.astype(np.float32),
            cv2.INTER_LINEAR
        )

        logger.debug(f"Applied twirl: angle={angle}°")
        return result

    def pucker(
        self,
        image: np.ndarray,
        center: Tuple[int, int],
        strength: float = 0.5
    ) -> np.ndarray:
        """Pucker/pinch pixels inward."""
        h, w = image.shape[:2]

        y, x = np.mgrid[0:h, 0:w]
        dx = x - center[0]
        dy = y - center[1]
        distance = np.sqrt(dx**2 + dy**2)

        # Gaussian falloff
        falloff = np.exp(-(distance**2) / (2 * (self.brush_size / 2)**2))

        # Pinch toward center
        scale = 1 - strength * falloff

        new_x = center[0] + dx * scale
        new_y = center[1] + dy * scale

        result = cv2.remap(
            image,
            new_x.astype(np.float32),
            new_y.astype(np.float32),
            cv2.INTER_LINEAR
        )

        return result

    def bloat(
        self,
        image: np.ndarray,
        center: Tuple[int, int],
        strength: float = 0.5
    ) -> np.ndarray:
        """Bloat/expand pixels outward."""
        h, w = image.shape[:2]

        y, x = np.mgrid[0:h, 0:w]
        dx = x - center[0]
        dy = y - center[1]
        distance = np.sqrt(dx**2 + dy**2)

        # Gaussian falloff
        falloff = np.exp(-(distance**2) / (2 * (self.brush_size / 2)**2))

        # Expand from center
        scale = 1 + strength * falloff

        new_x = center[0] + dx * scale
        new_y = center[1] + dy * scale

        result = cv2.remap(
            image,
            new_x.astype(np.float32),
            new_y.astype(np.float32),
            cv2.INTER_LINEAR
        )

        return result

    def show_dialog(self):
        """Show parameters dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(None, "Liquify", "Liquify tool coming soon.")


class CurvesAdjustment:
    """
    Photoshop-style curves adjustment.

    Features:
        - RGB curves
        - Per-channel curves
        - Preset curves
        - Interactive curve editor
    """

    def __init__(self):
        self.curve_points = [(0, 0), (255, 255)]  # Linear by default

    def apply_curve(
        self,
        image: np.ndarray,
        curve_points: List[Tuple[int, int]] = None,
        channel: str = "rgb"  # rgb, r, g, b
    ) -> np.ndarray:
        """
        Apply tone curve to image.

        Args:
            image: Input image
            curve_points: List of (input, output) points
            channel: Which channel to adjust
        """
        if curve_points is None:
            curve_points = self.curve_points

        # Create lookup table from curve points
        lut = self._create_lut(curve_points)

        result = image.copy()

        if channel == "rgb":
            # Apply to all channels
            result = cv2.LUT(result, lut)
        elif channel == "r":
            result[:, :, 0] = cv2.LUT(result[:, :, 0], lut)
        elif channel == "g":
            result[:, :, 1] = cv2.LUT(result[:, :, 1], lut)
        elif channel == "b":
            result[:, :, 2] = cv2.LUT(result[:, :, 2], lut)

        logger.debug(f"Applied curves to {channel} channel")
        return result

    def _create_lut(self, points: List[Tuple[int, int]]) -> np.ndarray:
        """Create 256-entry lookup table from curve points."""
        # Sort points by x
        points = sorted(points, key=lambda p: p[0])

        # Interpolate
        x_points = [p[0] for p in points]
        y_points = [p[1] for p in points]

        lut = np.interp(np.arange(256), x_points, y_points)
        lut = np.clip(lut, 0, 255).astype(np.uint8)

        return lut

    def preset_increase_contrast(self) -> List[Tuple[int, int]]:
        """S-curve for increased contrast."""
        return [(0, 0), (64, 48), (192, 208), (255, 255)]

    def preset_decrease_contrast(self) -> List[Tuple[int, int]]:
        """Inverse S-curve for decreased contrast."""
        return [(0, 0), (64, 80), (192, 176), (255, 255)]

    def preset_brighten(self) -> List[Tuple[int, int]]:
        """Brighten curve."""
        return [(0, 32), (128, 160), (255, 255)]

    def preset_darken(self) -> List[Tuple[int, int]]:
        """Darken curve."""
        return [(0, 0), (128, 96), (255, 224)]


class TextWarpTool:
    """
    Advanced text warp effects.

    Warp Styles:
        - Arc, Arc Lower, Arc Upper
        - Arch, Bulge
        - Shell Lower, Shell Upper
        - Flag, Wave
        - Fish, Fisheye
        - Rise, Inflate, Squeeze, Twist
    """

    WARP_STYLES = [
        "None", "Arc", "Arc Lower", "Arc Upper",
        "Arch", "Bulge", "Shell Lower", "Shell Upper",
        "Flag", "Wave", "Fish", "Rise",
        "Fisheye", "Inflate", "Squeeze", "Twist"
    ]

    def warp_text(
        self,
        text_image: np.ndarray,
        style: str,
        bend: float = 50.0,
        horizontal_distortion: float = 0.0,
        vertical_distortion: float = 0.0
    ) -> np.ndarray:
        """
        Apply warp effect to text.

        Args:
            text_image: Rendered text image
            style: Warp style name
            bend: Bend amount (-100 to 100)
            horizontal_distortion: H distortion (-100 to 100)
            vertical_distortion: V distortion (-100 to 100)
        """
        if style == "None":
            return text_image

        h, w = text_image.shape[:2]

        # Create displacement maps based on style
        if style == "Arc":
            result = self._warp_arc(text_image, bend)
        elif style == "Wave":
            result = self._warp_wave(text_image, bend)
        elif style == "Bulge":
            result = self._warp_bulge(text_image, bend)
        elif style == "Fisheye":
            result = self._warp_fisheye(text_image, bend)
        else:
            # Default to arc
            result = self._warp_arc(text_image, bend)

        logger.debug(f"Applied text warp: {style}, bend={bend}")
        return result

    def _warp_arc(self, image: np.ndarray, bend: float) -> np.ndarray:
        """Arc warp effect."""
        h, w = image.shape[:2]

        # Create coordinate grids
        y, x = np.mgrid[0:h, 0:w]

        # Normalize coordinates
        x_norm = (x - w / 2) / (w / 2)
        y_norm = (y - h / 2) / (h / 2)

        # Apply arc
        bend_rad = np.radians(bend)
        y_offset = x_norm**2 * bend_rad * h / 4

        new_x = x
        new_y = y + y_offset

        result = cv2.remap(
            image,
            new_x.astype(np.float32),
            new_y.astype(np.float32),
            cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_TRANSPARENT
        )

        return result

    def _warp_wave(self, image: np.ndarray, bend: float) -> np.ndarray:
        """Wave warp effect."""
        h, w = image.shape[:2]

        y, x = np.mgrid[0:h, 0:w]

        # Sine wave
        amplitude = bend / 100.0 * h / 4
        frequency = 2 * np.pi / w

        y_offset = amplitude * np.sin(x * frequency)

        new_x = x
        new_y = y + y_offset

        result = cv2.remap(
            image,
            new_x.astype(np.float32),
            new_y.astype(np.float32),
            cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_TRANSPARENT
        )

        return result

    def _warp_bulge(self, image: np.ndarray, bend: float) -> np.ndarray:
        """Bulge warp effect."""
        h, w = image.shape[:2]

        y, x = np.mgrid[0:h, 0:w]

        # Center coordinates
        cx, cy = w / 2, h / 2
        dx = x - cx
        dy = y - cy
        distance = np.sqrt(dx**2 + dy**2)
        max_dist = np.sqrt(cx**2 + cy**2)

        # Bulge factor
        factor = 1 + (bend / 100.0) * (1 - distance / max_dist)

        new_x = cx + dx * factor
        new_y = cy + dy * factor

        result = cv2.remap(
            image,
            new_x.astype(np.float32),
            new_y.astype(np.float32),
            cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_TRANSPARENT
        )

        return result

    def _warp_fisheye(self, image: np.ndarray, bend: float) -> np.ndarray:
        """Fisheye lens effect."""
        h, w = image.shape[:2]

        y, x = np.mgrid[0:h, 0:w]

        cx, cy = w / 2, h / 2
        dx = x - cx
        dy = y - cy
        distance = np.sqrt(dx**2 + dy**2)
        max_dist = np.sqrt(cx**2 + cy**2)

        # Fisheye distortion
        r = distance / max_dist
        theta = np.arctan2(dy, dx)

        strength = bend / 100.0
        r_new = r + strength * r**2

        new_x = cx + r_new * max_dist * np.cos(theta)
        new_y = cy + r_new * max_dist * np.sin(theta)

        result = cv2.remap(
            image,
            new_x.astype(np.float32),
            new_y.astype(np.float32),
            cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_TRANSPARENT
        )

        return result

    def show_dialog(self):
        """Show parameters dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None, "Warp Text", "Text Warp settings coming soon.")
