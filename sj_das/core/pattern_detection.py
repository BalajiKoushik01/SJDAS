"""Pattern Detection Engine.

Extract and replicate patterns from any image (e.g., from Google).
Detects repeating motifs and generates graph representation.
"""

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class PatternDetectionEngine:
    """
    Advanced pattern detection for textile designs.

    Features:
    - Detect repeating patterns in images
    - Extract motifs from complex designs
    - Generate graph/grid representation
    - Find optimal repeat size
    """

    def __init__(self):
        """Initialize pattern detection engine."""
        self.min_repeat_size = 10
        self.max_repeat_size = 500

    def detect_pattern(
        self,
        image: np.ndarray,
        max_colors: int = 3
    ) -> tuple[np.ndarray, dict]:
        """
        Detect and extract pattern from image.

        Args:
            image: Input image (numpy array)
            max_colors: Maximum colors to detect

        Returns:
            (pattern_image, info_dict)
        """
        logger.info("Starting pattern detection...")

        # Step 1: Preprocess image
        processed = self._preprocess_image(image)

        # Step 2: Detect repeat unit
        repeat_size = self._detect_repeat_size(processed)

        # Step 3: Extract single repeat
        pattern = self._extract_repeat_unit(processed, repeat_size)

        # Step 4: Simplify colors
        simplified = self._simplify_colors(pattern, max_colors)

        # Step 5: Convert to graph
        graph = self._convert_to_graph(simplified)

        info = {
            "repeat_width": repeat_size[0],
            "repeat_height": repeat_size[1],
            "num_colors": max_colors,
            "original_size": image.shape[:2]
        }

        logger.info(
            f"Pattern detected: {repeat_size[0]}×{repeat_size[1]} repeat")

        return graph, info

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for pattern detection."""
        # Convert to grayscale for pattern matching
        gray = cv2.cvtColor(
            image, cv2.COLOR_BGR2GRAY) if len(
            image.shape) == 3 else image.copy()

        # Enhance contrast
        gray = cv2.equalizeHist(gray)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, h=10)

        return denoised

    def _detect_repeat_size(self, image: np.ndarray) -> tuple[int, int]:
        """
        Detect repeat unit size using autocorrelation.

        Finds the smallest repeating pattern in the image.
        """
        h, w = image.shape[:2]

        # Use FFT for faster correlation
        f_image = np.fft.fft2(image)
        f_conj = np.conj(f_image)
        correlation = np.fft.ifft2(f_image * f_conj).real

        # Normalize
        correlation = correlation / correlation.max()

        # Find peaks (excluding center)
        center_y, center_x = h // 2, w // 2
        correlation[center_y - 5:center_y + 5, center_x - 5:center_x + 5] = 0

        # Find first strong peak
        threshold = 0.7
        peaks = np.where(correlation > threshold)

        if len(peaks[0]) > 0:
            # Get closest peak to center
            distances = np.sqrt((peaks[0] - center_y)
                                ** 2 + (peaks[1] - center_x)**2)
            closest_idx = np.argmin(distances)

            repeat_y = abs(peaks[0][closest_idx] - center_y)
            repeat_x = abs(peaks[1][closest_idx] - center_x)

            # Clamp to reasonable range
            repeat_y = max(
                self.min_repeat_size, min(
                    repeat_y, self.max_repeat_size))
            repeat_x = max(
                self.min_repeat_size, min(
                    repeat_x, self.max_repeat_size))

            return (repeat_x, repeat_y)

        # Fallback: use portion of image
        return (min(100, w // 2), min(100, h // 2))

    def _extract_repeat_unit(
        self,
        image: np.ndarray,
        repeat_size: tuple[int, int]
    ) -> np.ndarray:
        """Extract single repeat unit from image."""
        repeat_w, repeat_h = repeat_size
        h, w = image.shape[:2]

        # Extract from center for best quality
        start_x = (w - repeat_w) // 2
        start_y = (h - repeat_h) // 2

        repeat_unit = image[start_y:start_y +
                            repeat_h, start_x:start_x + repeat_w]

        return repeat_unit.copy()

    def _simplify_colors(
        self,
        image: np.ndarray,
        max_colors: int
    ) -> np.ndarray:
        """
        Simplify image to specified number of colors.

        Uses K-means clustering for optimal color reduction.
        """
        if len(image.shape) == 2:
            # Convert grayscale to RGB for processing
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        # Reshape for K-means
        pixels = image.reshape(-1, 3).astype(np.float32)

        # K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(
            pixels,
            max_colors,
            None,
            criteria,
            10,
            cv2.KMEANS_PP_CENTERS
        )

        # Map pixels to cluster centers
        centers = centers.astype(np.uint8)
        simplified = centers[labels.flatten()]
        simplified = simplified.reshape(image.shape)

        return simplified

    def _convert_to_graph(self, image: np.ndarray) -> np.ndarray:
        """
        Convert simplified image to graph representation.

        Creates indexed image where each color is a number (0, 1, 2, etc.)
        """
        if len(image.shape) == 2:
            return image

        # Get unique colors
        pixels = image.reshape(-1, 3)
        unique_colors = np.unique(pixels, axis=0)

        # Create indexed image
        h, w = image.shape[:2]
        graph = np.zeros((h, w), dtype=np.uint8)

        for idx, color in enumerate(unique_colors):
            # Find all pixels of this color
            mask = np.all(image == color, axis=2)
            graph[mask] = idx

        logger.info(f"Graph created with {len(unique_colors)} distinct values")

        return graph

    def extract_from_url(self, image_path: str,
                         max_colors: int = 3) -> tuple[np.ndarray, dict]:
        """
        Extract pattern from image file or URL.

        Args:
            image_path: Path to image file
            max_colors: Maximum colors

        Returns:
            (pattern_graph, info_dict)
        """
        # Load image
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")

        # Detect pattern
        return self.detect_pattern(image, max_colors)
