"""
Color Management System for SJ-DAS.
Handles color extraction, palette management, and yarn color operations.
"""
import json

import cv2
import numpy as np
from PyQt6.QtGui import QColor


class ColorPalette:
    """Represents a color palette with metadata."""

    def __init__(self, name: str = "Untitled Palette"):
        self.name = name
        self.colors: list[QColor] = []
        self.color_names: list[str] = []

    def add_color(self, color: QColor, name: str = ""):
        """Add a color to the palette."""
        self.colors.append(color)
        self.color_names.append(name or f"Color {len(self.colors)}")

    def remove_color(self, index: int):
        """Remove a color by index."""
        if 0 <= index < len(self.colors):
            del self.colors[index]
            del self.color_names[index]

    def to_dict(self) -> dict:
        """Convert palette to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "colors": [
                {
                    "r": c.red(),
                    "g": c.green(),
                    "b": c.blue(),
                    "name": self.color_names[i]
                }
                for i, c in enumerate(self.colors)
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ColorPalette':
        """Create palette from dictionary."""
        palette = cls(data.get("name", "Untitled Palette"))
        for color_data in data.get("colors", []):
            color = QColor(color_data["r"], color_data["g"], color_data["b"])
            palette.add_color(color, color_data.get("name", ""))
        return palette


class ColorManager:
    """Manages color operations for textile design."""

    @staticmethod
    def extract_colors(image: np.ndarray, max_colors: int = 16,
                       method: str = "kmeans") -> list[tuple[int, int, int]]:
        """
        Extract dominant colors from image.

        Args:
            image: BGR image array
            max_colors: Maximum number of colors to extract
            method: 'kmeans' or 'quantize'

        Returns:
            List of (R, G, B) tuples
        """
        if image is None or image.size == 0:
            return []

        # Reshape to pixel list
        pixels = image.reshape(-1, 3).astype(np.float32)

        if method == "kmeans":
            # K-means clustering
            criteria = (
                cv2.TERM_CRITERIA_EPS +
                cv2.TERM_CRITERIA_MAX_ITER,
                100,
                0.2)
            _, labels, centers = cv2.kmeans(pixels, max_colors, None, criteria, 10,
                                            cv2.KMEANS_PP_CENTERS)

            # Convert BGR to RGB and sort by frequency
            unique, counts = np.unique(labels, return_counts=True)
            # Sort by descending frequency
            sorted_indices = np.argsort(-counts)

            colors = []
            for idx in sorted_indices:
                bgr = centers[idx].astype(int)
                rgb = (int(bgr[2]), int(bgr[1]), int(bgr[0]))  # BGR to RGB
                colors.append(rgb)

            return colors

        else:  # quantize
            # Simple color quantization
            # Reduce to max_colors using uniform quantization
            levels = int(np.ceil(max_colors ** (1 / 3)))
            quantized = (pixels // (256 // levels)) * (256 // levels)

            # Get unique colors
            unique_colors = np.unique(quantized.astype(np.uint8), axis=0)

            # Limit to max_colors
            if len(unique_colors) > max_colors:
                unique_colors = unique_colors[:max_colors]

            # Convert BGR to RGB
            colors = [(int(c[2]), int(c[1]), int(c[0])) for c in unique_colors]
            return colors

    @staticmethod
    def save_palette(palette: ColorPalette, filepath: str) -> bool:
        """Save palette to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(palette.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving palette: {e}")
            return False

    @staticmethod
    def load_palette(filepath: str) -> ColorPalette | None:
        """Load palette from JSON file."""
        try:
            with open(filepath) as f:
                data = json.load(f)
            return ColorPalette.from_dict(data)
        except Exception as e:
            print(f"Error loading palette: {e}")
            return None

    @staticmethod
    def find_closest_color(target: QColor, palette: list[QColor]) -> int:
        """
        Find the closest color in palette to target.

        Returns:
            Index of closest color
        """
        if not palette:
            return -1

        min_dist = float('inf')
        closest_idx = 0

        tr, tg, tb = target.red(), target.green(), target.blue()

        for i, color in enumerate(palette):
            r, g, b = color.red(), color.green(), color.blue()
            # Euclidean distance in RGB space
            dist = ((r - tr) ** 2 + (g - tg) ** 2 + (b - tb) ** 2) ** 0.5

            if dist < min_dist:
                min_dist = dist
                closest_idx = i

        return closest_idx

    @staticmethod
    def reduce_to_palette(image: np.ndarray,
                          palette: list[QColor]) -> np.ndarray:
        """
        Reduce image colors to match palette (color quantization).

        Args:
            image: BGR image
            palette: List of QColor objects

        Returns:
            Quantized BGR image
        """
        if not palette:
            return image

        h, w = image.shape[:2]
        np.zeros_like(image)

        # Convert palette to numpy array (BGR)
        palette_bgr = np.array([
            [c.blue(), c.green(), c.red()] for c in palette
        ], dtype=np.uint8)

        # For each pixel, find closest palette color
        pixels = image.reshape(-1, 3)

        for i, pixel in enumerate(pixels):
            # Find closest color
            distances = np.sum((palette_bgr - pixel) ** 2, axis=1)
            closest_idx = np.argmin(distances)
            pixels[i] = palette_bgr[closest_idx]

        return pixels.reshape(h, w, 3)
