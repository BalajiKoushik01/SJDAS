import cv2
import numpy as np


class FloatsVerifier:
    """
    Industry Standard Float Checking for Jacquard Weaving.
    Detects warp or weft floats that exceed a specified limit.
    Long floats cause snagging and fabric instability.
    """

    @staticmethod
    def check_floats(binary_pattern, max_float_length=20):
        """
        Scans a binary pattern (0/1 or 0/255) for floats.

        Args:
            binary_pattern (np.array): 2D array representing the weave.
                                       0 = Weft up (or Warp down)
                                       1 = Warp up (or Weft down)
            max_float_length (int): Maximum allowed continuous pixels.

        Returns:
            np.array: A mask where 255 indicates a float error.
        """
        # Ensure binary 0/1
        arr = (binary_pattern > 0).astype(np.uint8)

        h, w = arr.shape
        np.zeros((h, w), dtype=np.uint8)

        # 1. Check Horizontal Floats (Weft Floats if Row=Pick)
        # We look for continuous runs of 0s or 1s > max_float_length

        # Use simple run-length encoding logic or kernel checking
        # Kernel: A line of 1s of length (max + 1)
        kernel_size = max_float_length + 1
        kernel = np.ones((1, kernel_size), dtype=np.uint8)

        # Check for long runs of 1s (Warp Floats?)
        # Erode the image. If pixels survive, they belong to a block larger
        # than kernel
        eroded_1 = cv2.erode(arr, kernel, iterations=1)
        # Dilate back to mark the full float region
        floats_1 = cv2.dilate(eroded_1, kernel, iterations=1)

        # Check for long runs of 0s
        # Invert image and repeat
        arr_inv = 1 - arr
        eroded_0 = cv2.erode(arr_inv, kernel, iterations=1)
        floats_0 = cv2.dilate(eroded_0, kernel, iterations=1)

        # Combine
        horizontal_errors = cv2.bitwise_or(floats_1, floats_0)

        # 2. Check Vertical Floats (Warp Floats if Col=End)
        kernel_v = np.ones((kernel_size, 1), dtype=np.uint8)

        eroded_v_1 = cv2.erode(arr, kernel_v, iterations=1)
        floats_v_1 = cv2.dilate(eroded_v_1, kernel_v, iterations=1)

        eroded_v_0 = cv2.erode(arr_inv, kernel_v, iterations=1)
        floats_v_0 = cv2.dilate(eroded_v_0, kernel_v, iterations=1)

        vertical_errors = cv2.bitwise_or(floats_v_1, floats_v_0)

        # Final Error Mask
        total_errors = cv2.bitwise_or(horizontal_errors, vertical_errors)

        return total_errors * 255
