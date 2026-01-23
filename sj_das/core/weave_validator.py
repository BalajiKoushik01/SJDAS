import cv2
import numpy as np


class WeaveValidator:
    """
    Validates designs for Jacquard weaving constraints.
    Detects long floats that would cause snagging on the loom.
    """

    @staticmethod
    def detect_float_errors(image_array, max_float_length=24):
        """
        Detects float errors in weft (horizontal) and warp (vertical) directions.

        Args:
            image_array: Numpy array (H, W) or (H, W, 3/4)
            max_float_length: Maximum allowed run of identical pixels.
                              Standard: ~20-30 pixels for high density.

        Returns:
            error_mask: Uint8 mask (H, W) where 255 indicates an error (too long float).
        """
        # Convert to grayscale/class indices for analysis
        if len(image_array.shape) == 3:
            # Simple approach: Check intensity or specific checking per channel?
            # For weaving, we check if the 'structure' repeats.
            # Let's use grayscale for pattern continuity check.
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_array

        h, w = gray.shape
        error_mask = np.zeros((h, w), dtype=np.uint8)

        # 1. Weft Floats (Horizontal)
        # We iterate rows. Optimized with shifting?
        # A float is a sequence of identical values > max_float_length.

        # Fast Vectorized Approach for 2 colors (Binary) is easy.
        # For multi-color, shifting is good.

        # Check: pixel[i] == pixel[i+1] ... == pixel[i+k]
        # This is expensive in pure python loops.
        # Use simple morphological operation!

        # Logic:
        # Long run of same color -> Low frequency.
        # If we take derivative, it's 0.
        # Run-length encoding per row?

        # Optimized Morphological Approach:
        # 1. Edge detection (derivative) finds transitions.
        # 2. Invert edges = smooth areas.
        # 3. Erode smooth areas by (max_float, 1).
        # 4. If any pixels remain, they are part of a long float.
        # 5. Dilate back to show the area.

        # Edges (Unsigned difference)
        diff_x = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
        is_flat_x = (diff_x == 0).astype(np.uint8)

        # Filter: horizontal line of length max_float
        # kernel of shape (1, max_float)
        kernel_x = np.ones((1, max_float_length), np.uint8)

        # Erode: shrinks flat areas. If area < kernel, it disappears.
        # If area >= kernel, center remains.
        long_floats_x = cv2.erode(is_flat_x, kernel_x)

        # Dilate back to recover the full length of the float
        # This highlights the whole problematic segment
        float_regions_x = cv2.dilate(long_floats_x, kernel_x)

        # 2. Warp Floats (Vertical)
        diff_y = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
        is_flat_y = (diff_y == 0).astype(np.uint8)

        kernel_y = np.ones((max_float_length, 1), np.uint8)
        long_floats_y = cv2.erode(is_flat_y, kernel_y)
        float_regions_y = cv2.dilate(long_floats_y, kernel_y)

        # Combine
        # Using 255 for visualization
        error_mask = cv2.bitwise_or(float_regions_x, float_regions_y) * 255

        return error_mask
