"""
Procedural Design Generator - Fast algorithmic pattern generation
Creates loom-compatible designs using procedural techniques
"""

import math

import cv2
import numpy as np


class ProceduralMotifLibrary:
    """Library of procedural motif generators."""

    @staticmethod
    def peacock(size: int = 64, color_main: tuple = (255, 0, 0),
                color_accent: tuple = (255, 215, 0)) -> np.ndarray:
        """Generate a peacock motif."""
        img = np.zeros((size, size, 3), dtype=np.uint8)
        center = size // 2

        # Peacock body (simplified)
        cv2.circle(img, (center, center), size // 4, color_main, -1)

        # Feather pattern
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            end_x = int(center + math.cos(rad) * size // 2.5)
            end_y = int(center + math.sin(rad) * size // 2.5)

            # Feather line
            cv2.line(img, (center, center), (end_x, end_y), color_accent, 2)

            # Feather eye
            eye_x = int(center + math.cos(rad) * size // 3.5)
            eye_y = int(center + math.sin(rad) * size // 3.5)
            cv2.circle(img, (eye_x, eye_y), size // 12, color_accent, -1)
            cv2.circle(img, (eye_x, eye_y), size // 20, color_main, -1)

        return img

    @staticmethod
    def lotus(size: int = 64, color_main: tuple = (255, 192, 203),
              color_accent: tuple = (255, 255, 255)) -> np.ndarray:
        """Generate a lotus motif."""
        img = np.zeros((size, size, 3), dtype=np.uint8)
        center = size // 2

        # Lotus petals
        num_petals = 8
        for i in range(num_petals):
            angle = i * (360 / num_petals)
            rad = math.radians(angle)

            petal_len = size // 2.5
            int(center + math.cos(rad) * petal_len)
            int(center + math.sin(rad) * petal_len)

            # Petal shape (ellipse)
            axes = (size // 8, size // 4)
            cv2.ellipse(img, (center, center), axes, angle, 0, 180,
                        color_main, -1)

        # Center
        cv2.circle(img, (center, center), size // 6, color_accent, -1)
        cv2.circle(img, (center, center), size // 8, color_main, -1)

        return img

    @staticmethod
    def mango(size: int = 64, color_main: tuple = (0, 255, 0),
              color_accent: tuple = (255, 215, 0)) -> np.ndarray:
        """Generate a mango/paisley motif."""
        img = np.zeros((size, size, 3), dtype=np.uint8)

        # Paisley shape
        points = []
        center_x, center_y = size // 2, size // 2

        for angle in range(0, 360, 5):
            rad = math.radians(angle)
            r = size // 3 + (size // 8) * math.sin(3 * rad)
            x = int(center_x + r * math.cos(rad))
            y = int(center_y + r * math.sin(rad))
            points.append([x, y])

        pts = np.array(points, np.int32)
        cv2.fillPoly(img, [pts], color_main)

        # Inner pattern
        cv2.ellipse(img, (center_x, center_y), (size // 6, size // 4),
                    45, 0, 360, color_accent, 2)

        return img

    @staticmethod
    def geometric_diamond(size: int = 64, color_main: tuple = (0, 0, 255),
                          color_accent: tuple = (255, 255, 255)) -> np.ndarray:
        """Generate a diamond geometric pattern."""
        img = np.zeros((size, size, 3), dtype=np.uint8)
        center = size // 2

        # Diamond
        pts = np.array([
            [center, size // 6],
            [size - size // 6, center],
            [center, size - size // 6],
            [size // 6, center]
        ], np.int32)

        cv2.fillPoly(img, [pts], color_main)

        # Inner diamond
        pts_inner = np.array([
            [center, size // 3],
            [size - size // 3, center],
            [center, size - size // 3],
            [size // 3, center]
        ], np.int32)

        cv2.fillPoly(img, [pts_inner], color_accent)

        return img

    @staticmethod
    def temple_arch(size: int = 64, color_main: tuple = (139, 69, 19),
                    color_accent: tuple = (255, 215, 0)) -> np.ndarray:
        """Generate a temple architecture motif."""
        img = np.zeros((size, size, 3), dtype=np.uint8)
        center_x = size // 2

        # Temple steps
        for i in range(3):
            y = size - size // 6 - i * size // 8
            width = size - i * size // 6
            x1 = center_x - width // 2
            x2 = center_x + width // 2
            cv2.rectangle(img, (x1, y), (x2, y + size // 10),
                          color_main, -1)

        # Arch
        cv2.ellipse(img, (center_x, size // 2), (size // 3, size // 3),
                    0, 180, 360, color_accent, 3)

        # Pillars
        pillar_width = size // 12
        cv2.rectangle(img, (size // 4 - pillar_width, size // 2),
                      (size // 4, size - size // 6), color_main, -1)
        cv2.rectangle(img, (3 * size // 4, size // 2),
                      (3 * size // 4 + pillar_width, size - size // 6),
                      color_main, -1)

        return img


class ProceduralGenerator:
    """Procedural design generation engine."""

    def __init__(self):
        self.motif_lib = ProceduralMotifLibrary()

    def generate_design(self, params) -> np.ndarray:
        """
        Generate a complete design from parameters.

        Args:
            params: DesignParameters from prompt parser

        Returns:
            np.ndarray: Generated design image (RGB)
        """
        if params.design_type == 'border':
            return self.generate_border(params)
        elif params.design_type == 'pallu':
            return self.generate_pallu(params)
        elif params.design_type == 'blouse':
            return self.generate_blouse(params)
        else:
            return self.generate_border(params)  # Default

    def generate_border(self, params) -> np.ndarray:
        """Generate a border design."""
        # Calculate dimensions
        width_px = params.width_mm if params.width_mm else 150
        height_px = 512  # Standard length

        # Create base
        img = np.zeros((height_px, width_px, 3), dtype=np.uint8)

        # Get colors
        bg_color = self._get_color_rgb(
            params.colors[0] if params.colors else 'red')
        accent_color = self._get_color_rgb(
            params.colors[1] if len(
                params.colors) > 1 else 'gold')

        # Fill background
        img[:, :] = bg_color

        # Add motifs if specified
        if params.motifs:
            motif_type = params.motifs[0]
            motif_size = min(width_px - 10, 64)

            # Generate motif
            motif_img = self._get_motif(motif_type, motif_size,
                                        bg_color, accent_color)

            # Repeat along border
            spacing = motif_size + 20
            for y in range(20, height_px - motif_size, spacing):
                x = (width_px - motif_size) // 2
                self._blend_motif(img, motif_img, x, y)

        # Add decorative edge
        edge_width = max(2, width_px // 20)
        cv2.line(img, (edge_width, 0), (edge_width, height_px),
                 accent_color, 2)
        cv2.line(img, (width_px - edge_width, 0),
                 (width_px - edge_width, height_px), accent_color, 2)

        # Add weave texture if specified
        if params.weave == 'jeri':
            img = self._add_zari_texture(img, accent_color)

        return img

    def generate_pallu(self, params) -> np.ndarray:
        """Generate a pallu design."""
        # Pallu is wider and more elaborate
        width_px = 512
        length_px = params.length_mm if params.length_mm else 1200
        length_px = min(length_px, 2000)  # Cap for memory

        img = np.zeros((length_px, width_px, 3), dtype=np.uint8)

        # Get colors
        bg_color = self._get_color_rgb(
            params.colors[0] if params.colors else 'red')
        accent_color = self._get_color_rgb(
            params.colors[1] if len(
                params.colors) > 1 else 'gold')

        # Fill background
        img[:, :] = bg_color

        # Pallu has denser motif placement
        if params.motifs:
            motif_type = params.motifs[0]
            motif_size = 80

            motif_img = self._get_motif(motif_type, motif_size,
                                        bg_color, accent_color)

            # Grid pattern
            spacing_x = 100
            spacing_y = 100

            for y in range(50, length_px - motif_size, spacing_y):
                for x in range(50, width_px - motif_size, spacing_x):
                    # Offset alternate rows
                    offset = spacing_x // 2 if (y // spacing_y) % 2 == 1 else 0
                    self._blend_motif(img, motif_img, x + offset, y)

        # Add elaborate border
        border_width = 40
        cv2.rectangle(img, (0, 0), (border_width, length_px),
                      accent_color, -1)
        cv2.rectangle(img, (width_px - border_width, 0),
                      (width_px, length_px), accent_color, -1)

        return img

    def generate_blouse(self, params) -> np.ndarray:
        """Generate a blouse piece design."""
        # Blouse piece is smaller, coordinates with saree
        width_px = 512
        length_px = 400

        img = np.zeros((length_px, width_px, 3), dtype=np.uint8)

        # Get colors
        bg_color = self._get_color_rgb(
            params.colors[0] if params.colors else 'red')
        accent_color = self._get_color_rgb(
            params.colors[1] if len(
                params.colors) > 1 else 'gold')

        # Fill background
        img[:, :] = bg_color

        # Simple border pattern
        border_width = 30
        cv2.rectangle(img, (0, 0), (width_px, border_width),
                      accent_color, -1)
        cv2.rectangle(img, (0, length_px - border_width),
                      (width_px, length_px), accent_color, -1)

        # Small motif in center if specified
        if params.motifs:
            motif_type = params.motifs[0]
            motif_size = 60

            motif_img = self._get_motif(motif_type, motif_size,
                                        bg_color, accent_color)

            x = (width_px - motif_size) // 2
            y = (length_px - motif_size) // 2
            self._blend_motif(img, motif_img, x, y)

        return img

    def _get_motif(self, motif_type: str, size: int,
                   color_main: tuple, color_accent: tuple) -> np.ndarray:
        """Get a motif image."""
        if motif_type == 'peacock':
            return self.motif_lib.peacock(size, color_main, color_accent)
        elif motif_type == 'lotus':
            return self.motif_lib.lotus(size, color_main, color_accent)
        elif motif_type == 'mango':
            return self.motif_lib.mango(size, color_main, color_accent)
        elif motif_type == 'geometric':
            return self.motif_lib.geometric_diamond(
                size, color_main, color_accent)
        elif motif_type == 'temple':
            return self.motif_lib.temple_arch(size, color_main, color_accent)
        else:
            # Default geometric
            return self.motif_lib.geometric_diamond(
                size, color_main, color_accent)

    def _blend_motif(self, img: np.ndarray, motif: np.ndarray, x: int, y: int):
        """Blend motif into image at position."""
        h, w = motif.shape[:2]

        # Check bounds
        if y + h > img.shape[0] or x + w > img.shape[1]:
            return

        # Simple alpha blend (motif non-black pixels)
        mask = np.any(motif != [0, 0, 0], axis=-1)
        img[y:y + h, x:x + w][mask] = motif[mask]

    def _add_zari_texture(self, img: np.ndarray,
                          zari_color: tuple) -> np.ndarray:
        """Add metallic zari texture effect."""
        # Add subtle shimmer/texture
        texture = np.random.randint(-10, 10, img.shape, dtype=np.int16)
        img_int = img.astype(np.int16) + texture
        img = np.clip(img_int, 0, 255).astype(np.uint8)

        # Add metallic dots
        h, w = img.shape[:2]
        for _ in range(h * w // 1000):  # Sparse dots
            y = np.random.randint(0, h)
            x = np.random.randint(0, w)
            cv2.circle(img, (x, y), 1, zari_color, -1)

        return img

    def _get_color_rgb(self, color_name: str) -> tuple[int, int, int]:
        """Convert color name to RGB tuple."""
        colors = {
            'red': (200, 0, 0),
            'gold': (255, 215, 0),
            'green': (0, 150, 0),
            'blue': (0, 0, 200),
            'purple': (128, 0, 128),
            'pink': (255, 192, 203),
            'orange': (255, 165, 0),
            'yellow': (255, 255, 0),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'silver': (192, 192, 192),
            'maroon': (128, 0, 0)
        }
        return colors.get(color_name, (200, 0, 0))  # Default red


# Global instance
_generator_instance = None


def get_procedural_generator() -> ProceduralGenerator:
    """Get or create global generator instance."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = ProceduralGenerator()
    return _generator_instance
