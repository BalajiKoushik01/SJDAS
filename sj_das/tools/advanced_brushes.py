"""
PHASE 3: ADVANCED BRUSHES - Professional Photo Editing Tools
Implements Airbrush, Dodge, Burn, Smudge tools like Paint Shop Pro
"""

from sj_das.tools.base import Tool
from PyQt6.QtGui import QPixmap
import cv2
import numpy as np
from PyQt6.QtCore import QPoint, Qt


class AdvancedBrushTools:
    """Advanced brush tools for professional photo editing."""

    @staticmethod
    def airbrush(image, x, y, size, color, opacity=0.3, spread=1.5):
        """
        Airbrush effect with soft spray pattern.

        Args:
            image: numpy array
            x, y: center position
            size: brush size
            color: RGB tuple
            opacity: spray opacity (0-1)
            spread: spray spread factor
        """
        height, width = image.shape[:2]

        # Create spray pattern
        radius = int(size * spread)
        for _ in range(int(size * 5)):  # Number of spray particles
            # Random offset from center
            angle = np.random.uniform(0, 2 * np.pi)
            distance = np.random.uniform(0, radius) * np.random.uniform(0, 1)

            px = int(x + distance * np.cos(angle))
            py = int(y + distance * np.sin(angle))

            if 0 <= px < width and 0 <= py < height:
                # Apply color with falloff
                falloff = 1.0 - (distance / radius)
                alpha = opacity * falloff

                image[py, px] = (
                    image[py, px] * (1 - alpha) + np.array(color) * alpha
                ).astype(np.uint8)

        return image

    @staticmethod
    def dodge(image, x, y, size, strength=0.3):
        """
        Dodge tool - lighten areas.

        Args:
            image: numpy array
            x, y: center position
            size: brush size
            strength: dodge strength (0-1)
        """
        height, width = image.shape[:2]

        # Create circular mask
        y_coords, x_coords = np.ogrid[:height, :width]
        mask = ((x_coords - x)**2 + (y_coords - y)**2) <= size**2

        # Create soft falloff
        distances = np.sqrt((x_coords - x)**2 + (y_coords - y)**2)
        falloff = np.clip(1.0 - distances / size, 0, 1)

        # Apply dodge (lighten)
        dodge_amount = strength * falloff * mask
        image = image.astype(float)
        image = image + (255 - image) * dodge_amount[:, :, np.newaxis]

        return np.clip(image, 0, 255).astype(np.uint8)

    @staticmethod
    def burn(image, x, y, size, strength=0.3):
        """
        Burn tool - darken areas.

        Args:
            image: numpy array
            x, y: center position
            size: brush size
            strength: burn strength (0-1)
        """
        height, width = image.shape[:2]

        # Create circular mask
        y_coords, x_coords = np.ogrid[:height, :width]
        mask = ((x_coords - x)**2 + (y_coords - y)**2) <= size**2

        # Create soft falloff
        distances = np.sqrt((x_coords - x)**2 + (y_coords - y)**2)
        falloff = np.clip(1.0 - distances / size, 0, 1)

        # Apply burn (darken)
        burn_amount = strength * falloff * mask
        image = image.astype(float)
        image = image * (1 - burn_amount[:, :, np.newaxis])

        return np.clip(image, 0, 255).astype(np.uint8)

    @staticmethod
    def smudge(image, x, y, prev_x, prev_y, size, strength=0.5):
        """
        Smudge tool - blend/smear colors.

        Args:
            image: numpy array
            x, y: current position
            prev_x, prev_y: previous position
            size: brush size
            strength: smudge strength (0-1)
        """
        height, width = image.shape[:2]

        if prev_x is None or prev_y is None:
            return image

        # Get color from previous position
        if 0 <= prev_y < height and 0 <= prev_x < width:
            source_color = image[prev_y, prev_x].copy()
        else:
            return image

        # Create circular mask
        y_coords, x_coords = np.ogrid[:height, :width]
        mask = ((x_coords - x)**2 + (y_coords - y)**2) <= size**2

        # Create soft falloff
        distances = np.sqrt((x_coords - x)**2 + (y_coords - y)**2)
        falloff = np.clip(1.0 - distances / size, 0, 1)

        # Apply smudge
        smudge_amount = strength * falloff * mask
        image = image.astype(float)
        image = (
            image * (1 - smudge_amount[:, :, np.newaxis]) +
            source_color * smudge_amount[:, :, np.newaxis]
        )

        return np.clip(image, 0, 255).astype(np.uint8)

    @staticmethod
    def soften(image, x, y, size, strength=0.5):
        """
        Soften/blur brush - local smoothing.

        Args:
            image: numpy array
            x, y: center position
            size: brush size
            strength: soften strength (0-1)
        """
        height, width = image.shape[:2]

        # Extract region
        x1 = max(0, x - size)
        y1 = max(0, y - size)
        x2 = min(width, x + size)
        y2 = min(height, y + size)

        if x2 <= x1 or y2 <= y1:
            return image

        region = image[y1:y2, x1:x2].copy()

        # Apply Gaussian blur
        kernel_size = int(size / 2) * 2 + 1  # Must be odd
        blurred = cv2.GaussianBlur(region, (kernel_size, kernel_size), 0)

        # Blend with original
        image[y1:y2, x1:x2] = (
            region * (1 - strength) + blurred * strength
        ).astype(np.uint8)

        return image

    @staticmethod
    def sharpen(image, x, y, size, strength=0.5):
        """
        Sharpen brush - local sharpening.

        Args:
            image: numpy array
            x, y: center position
            size: brush size
            strength: sharpen strength (0-1)
        """
        height, width = image.shape[:2]

        # Extract region
        x1 = max(0, x - size)
        y1 = max(0, y - size)
        x2 = min(width, x + size)
        y2 = min(height, y + size)

        if x2 <= x1 or y2 <= y1:
            return image

        region = image[y1:y2, x1:x2].copy().astype(float)

        # Sharpen kernel
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        # Apply sharpening
        sharpened = cv2.filter2D(region, -1, kernel)

        # Blend with original
        image[y1:y2, x1:x2] = (
            region * (1 - strength) + sharpened * strength
        ).clip(0, 255).astype(np.uint8)

        return image


# --- TOOL WRAPPERS ---


class AirbrushTool(Tool):
    """Tool wrapper for Airbrush effect."""

    def mouse_press(self, pos: QPoint, buttons: Qt.MouseButton):
        self.mouse_move(pos, buttons)

    def mouse_move(self, pos: QPoint, buttons: Qt.MouseButton):
        if not (buttons & Qt.MouseButton.LeftButton):
            return

        # Convert QImage to Numpy (Optimized)
        ptr = self.editor.mask_image.bits()
        ptr.setsize(self.editor.mask_image.height() *
                    self.editor.mask_image.width() * 4)
        arr = np.frombuffer(
            ptr, np.uint8).reshape(
            (self.editor.mask_image.height(), self.editor.mask_image.width(), 4))

        # Get Color
        c = self.editor.brush_color
        if hasattr(c, 'red'):
            # QImage ARGB32 is B G R A
            color = (c.blue(), c.green(), c.red(), 255)
        else:
            color = (0, 0, 0, 255)

        # Apply
        AdvancedBrushTools.airbrush(arr, int(pos.x()), int(pos.y()),
                                    self.editor.brush_size * 2, color, opacity=0.1)

        self.editor.mask_item.setPixmap(
            QPixmap.fromImage(self.editor.mask_image))


class SmudgeTool(Tool):
    """Tool wrapper for Smudge effect."""

    def __init__(self, editor):
        super().__init__(editor)
        self.last_pos = None

    def mouse_press(self, pos: QPoint, buttons: Qt.MouseButton):
        self.last_pos = (int(pos.x()), int(pos.y()))

    def mouse_move(self, pos: QPoint, buttons: Qt.MouseButton):
        if not (buttons & Qt.MouseButton.LeftButton):
            return
        if self.last_pos is None:
            self.last_pos = (int(pos.x()), int(pos.y()))
            return

        x, y = int(pos.x()), int(pos.y())

        # Convert QImage to Numpy
        ptr = self.editor.mask_image.bits()
        ptr.setsize(self.editor.mask_image.height() *
                    self.editor.mask_image.width() * 4)
        arr = np.frombuffer(
            ptr, np.uint8).reshape(
            (self.editor.mask_image.height(), self.editor.mask_image.width(), 4))

        # Apply Smudge
        AdvancedBrushTools.smudge(arr, x, y, self.last_pos[0], self.last_pos[1],
                                  self.editor.brush_size, strength=0.5)

        self.last_pos = (x, y)
        self.editor.mask_item.setPixmap(
            QPixmap.fromImage(self.editor.mask_image))

    def mouse_release(self, pos: QPoint, buttons: Qt.MouseButton):
        self.last_pos = None
