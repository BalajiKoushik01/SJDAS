import cv2
import numpy as np

from sj_das.utils.logger import logger


class DefectScannerEngine:
    """
    Industrial Weavability Checker.
    Detects manufacturing defects like Long Floats and Speckles.
    """

    def scan(self, image: np.ndarray, float_threshold: int = 200) -> dict:
        """
        Scans for defects.

        Args:
            image: BGR image (should be indexed/reduced ideally)
            float_threshold: Max allowed float length in pixels (mm depends on DPI)

        Returns:
            Dict with 'heatmap', 'float_count', 'speckle_count'
        """
        # Convert to Gray/Index
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # 1. Float Detection (Horizontal)
        # We look for runs of same pixel value > threshold
        float_mask = np.zeros_like(gray, dtype=np.uint8)

        # Vectorized Run-Length Encoding approach is complex.
        # Simple Kernel Convolution might work?
        # Or simple scanline loop (fast enough for Numba, slow for Python).
        # Let's use morphological Erosion to find long blocks.

        # Structure element horizontal line
        kernel_h = np.ones((1, float_threshold), np.uint8)
        # Note: this logic is flawed for multi-color.
        eroded = cv2.erode(gray, kernel_h, iterations=1)
        # Erosion shrinks bright areas. We need to find "Runs of Color X".
        # Correct approach: Iterate per color? Too slow if many colors.
        # But for Jacquard, we have limited colors (e.g. 8).

        colors = np.unique(gray)
        total_floats = 0

        for color in colors:
            # Mask for this color
            c_mask = cv2.inRange(gray, int(color), int(color))

            # Erode to find runs longer than threshold
            # E.g. if we erode by Kernel(1, 200), anything remaining was at
            # least 200 wide.
            long_runs = cv2.erode(c_mask, kernel_h, iterations=1)

            # Add to heatmap
            # Dilate back to show the full float?
            # For visualization, we just mark the risky area logic.
            float_mask = cv2.bitwise_or(float_mask, long_runs)

            if cv2.countNonZero(long_runs) > 0:
                total_floats += 1  # Rough count of "areas"

        # dilate float mask for visibility
        float_viz = cv2.dilate(
            float_mask, np.ones(
                (3, float_threshold), np.uint8), iterations=1)

        # 2. Speckle Detection (Isolated Pixels)
        # Pixel is different from all 4 neighbors
        # Laplacian or High Pass filter
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        # High derivative = sharp change.
        # Thresholding Laplacian gives edges/noise.
        speckle_mask = np.zeros_like(gray, dtype=np.uint8)
        # Simple Noise logic: Median Blur diff?
        median = cv2.medianBlur(gray, 3)
        diff = cv2.absdiff(gray, median)
        _, speckle_mask = cv2.threshold(diff, 10, 255, cv2.THRESH_BINARY)

        speckle_count = cv2.countNonZero(speckle_mask)

        # Combine Heatmap (Red for floats, Blue for speckles?)
        # Let's return a BGR Heatmap overlay
        heatmap = np.zeros_like(image)
        # Red channel = Floats
        heatmap[:, :, 2] = float_viz
        # Blue channel = Speckles
        heatmap[:, :, 0] = speckle_mask

        return {
            'heatmap': heatmap,
            'float_count': total_floats,
            'speckle_count': speckle_count
        }
