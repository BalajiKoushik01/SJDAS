"""
Image Conversion Utilities for SJ-DAS
Handles conversion between QImage and numpy arrays
"""
import logging

import cv2
import numpy as np
from PyQt6.QtCore import QBuffer, QIODevice
from PyQt6.QtGui import QImage

logger = logging.getLogger("SJ_DAS.ImageConversion")


def qimage_to_numpy(qimage: QImage) -> np.ndarray:
    """
    Convert QImage to numpy array (OpenCV format: BGR).

    Args:
        qimage: QImage to convert

    Returns:
        numpy array in BGR format
    """
    try:
        # Convert to RGB32 format if needed
        if qimage.format() != QImage.Format.Format_RGB32:
            qimage = qimage.convertToFormat(QImage.Format.Format_RGB32)

        # Get image dimensions
        width = qimage.width()
        height = qimage.height()

        # Get pointer to image data
        ptr = qimage.constBits()
        ptr.setsize(height * width * 4)  # 4 bytes per pixel (RGBA)

        # Create numpy array from data
        arr = np.array(ptr).reshape(height, width, 4)

        # Convert RGBA to BGR (OpenCV format)
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

        return bgr
    except Exception as e:
        logger.error(f"Failed to convert QImage to numpy: {e}")
        # Return a blank image as fallback
        return np.zeros((height if 'height' in locals() else 100,
                        width if 'width' in locals() else 100, 3), dtype=np.uint8)


def numpy_to_qimage(arr: np.ndarray) -> QImage:
    """
    Convert numpy array to QImage.

    Args:
        arr: numpy array (BGR or RGB format)

    Returns:
        QImage
    """
    try:
        # Handle different array shapes
        if len(arr.shape) == 2:
            # Grayscale
            height, width = arr.shape
            bytes_per_line = width
            qimage = QImage(
                arr.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_Grayscale8)
        elif len(arr.shape) == 3:
            height, width, channels = arr.shape

            if channels == 3:
                # BGR to RGB
                rgb = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
                bytes_per_line = 3 * width
                qimage = QImage(
                    rgb.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_RGB888)
            elif channels == 4:
                # BGRA to RGBA
                rgba = cv2.cvtColor(arr, cv2.COLOR_BGRA2RGBA)
                bytes_per_line = 4 * width
                qimage = QImage(
                    rgba.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_RGBA8888)
            else:
                raise ValueError(f"Unsupported number of channels: {channels}")
        else:
            raise ValueError(f"Unsupported array shape: {arr.shape}")

        # Make a copy to ensure data persists
        return qimage.copy()
    except Exception as e:
        logger.error(f"Failed to convert numpy to QImage: {e}")
        # Return a blank image as fallback
        return QImage(100, 100, QImage.Format.Format_RGB888)


def ensure_numpy(image) -> np.ndarray:
    """
    Ensure image is a numpy array, converting if necessary.

    Args:
        image: QImage or numpy array

    Returns:
        numpy array
    """
    if isinstance(image, QImage):
        return qimage_to_numpy(image)
    elif isinstance(image, np.ndarray):
        return image
    else:
        logger.warning(f"Unsupported image type: {type(image)}")
        return np.zeros((100, 100, 3), dtype=np.uint8)


def ensure_qimage(image) -> QImage:
    """
    Ensure image is a QImage, converting if necessary.

    Args:
        image: QImage or numpy array

    Returns:
        QImage
    """
    if isinstance(image, np.ndarray):
        return numpy_to_qimage(image)
    elif isinstance(image, QImage):
        return image
    else:
        logger.warning(f"Unsupported image type: {type(image)}")
        return QImage(100, 100, QImage.Format.Format_RGB888)
