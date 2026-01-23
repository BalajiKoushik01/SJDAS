"""
Image Operations with Automatic Type Conversion
Wraps all image operations to handle QImage/numpy conversion automatically
"""
import logging

import cv2
import numpy as np
from PyQt6.QtGui import QImage

from sj_das.utils.image_conversion import ensure_numpy, numpy_to_qimage

logger = logging.getLogger("SJ_DAS.ImageOps")


def rotate_image(image, angle):
    """
    Rotate image by specified angle.

    Args:
        image: QImage or numpy array
        angle: 90, 180, or 270 degrees

    Returns:
        Rotated image in same format as input
    """
    was_qimage = isinstance(image, QImage)

    try:
        # Convert to numpy
        img_np = ensure_numpy(image)

        # Rotate
        if angle == 90:
            rotated = cv2.rotate(img_np, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            rotated = cv2.rotate(img_np, cv2.ROTATE_180)
        elif angle == 270:
            rotated = cv2.rotate(img_np, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            raise ValueError(f"Unsupported angle: {angle}")

        # Convert back if needed
        return numpy_to_qimage(rotated) if was_qimage else rotated
    except Exception as e:
        logger.error(f"Rotation failed: {e}")
        return image


def flip_image(image, direction="horizontal"):
    """
    Flip image horizontally or vertically.

    Args:
        image: QImage or numpy array
        direction: "horizontal" or "vertical"

    Returns:
        Flipped image in same format as input
    """
    was_qimage = isinstance(image, QImage)

    try:
        # Convert to numpy
        img_np = ensure_numpy(image)

        # Flip
        if direction == "horizontal":
            flipped = cv2.flip(img_np, 1)
        elif direction == "vertical":
            flipped = cv2.flip(img_np, 0)
        else:
            raise ValueError(f"Unsupported direction: {direction}")

        # Convert back if needed
        return numpy_to_qimage(flipped) if was_qimage else flipped
    except Exception as e:
        logger.error(f"Flip failed: {e}")
        return image


def resize_image(image, width, height, interpolation=cv2.INTER_LANCZOS4):
    """
    Resize image to specified dimensions.

    Args:
        image: QImage or numpy array
        width: Target width
        height: Target height
        interpolation: OpenCV interpolation method

    Returns:
        Resized image in same format as input
    """
    was_qimage = isinstance(image, QImage)

    try:
        # Convert to numpy
        img_np = ensure_numpy(image)

        # Resize
        resized = cv2.resize(img_np, (width, height),
                             interpolation=interpolation)

        # Convert back if needed
        return numpy_to_qimage(resized) if was_qimage else resized
    except Exception as e:
        logger.error(f"Resize failed: {e}")
        return image


def apply_filter(image, filter_func, *args, **kwargs):
    """
    Apply any OpenCV filter function with automatic type conversion.

    Args:
        image: QImage or numpy array
        filter_func: OpenCV filter function (e.g., cv2.GaussianBlur)
        *args, **kwargs: Arguments for the filter function

    Returns:
        Filtered image in same format as input
    """
    was_qimage = isinstance(image, QImage)

    try:
        # Convert to numpy
        img_np = ensure_numpy(image)

        # Apply filter
        filtered = filter_func(img_np, *args, **kwargs)

        # Convert back if needed
        return numpy_to_qimage(filtered) if was_qimage else filtered
    except Exception as e:
        logger.error(f"Filter failed: {e}")
        return image
