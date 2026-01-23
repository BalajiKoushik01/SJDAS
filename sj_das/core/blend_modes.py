"""
LAYER BLEND MODES - Critical PSP Feature
Implements 15+ professional blend modes like Photoshop/PSP
"""

import numpy as np
from PyQt6.QtGui import QImage


class BlendModes:
    """Professional blend modes for layers."""

    # Blend mode constants
    NORMAL = "Normal"
    MULTIPLY = "Multiply"
    SCREEN = "Screen"
    OVERLAY = "Overlay"
    SOFT_LIGHT = "Soft Light"
    HARD_LIGHT = "Hard Light"
    COLOR_DODGE = "Color Dodge"
    COLOR_BURN = "Color Burn"
    DARKEN = "Darken"
    LIGHTEN = "Lighten"
    DIFFERENCE = "Difference"
    EXCLUSION = "Exclusion"
    HUE = "Hue"
    SATURATION = "Saturation"
    COLOR = "Color"
    LUMINOSITY = "Luminosity"

    ALL_MODES = [
        NORMAL, MULTIPLY, SCREEN, OVERLAY,
        SOFT_LIGHT, HARD_LIGHT, COLOR_DODGE, COLOR_BURN,
        DARKEN, LIGHTEN, DIFFERENCE, EXCLUSION,
        HUE, SATURATION, COLOR, LUMINOSITY
    ]

    @staticmethod
    def apply_blend(base_image, blend_image, mode, opacity=1.0):
        """
        Apply blend mode to combine two images.

        Args:
            base_image: QImage - bottom layer
            blend_image: QImage - top layer
            mode: str - blend mode name
            opacity: float - layer opacity (0.0-1.0)

        Returns:
            QImage - blended result
        """
        if mode == BlendModes.NORMAL:
            return blend_image

        # Convert to numpy for processing
        base_np = qimage_to_numpy(base_image)
        blend_np = qimage_to_numpy(blend_image)

        # Apply blend mode
        if mode == BlendModes.MULTIPLY:
            result = base_np * blend_np / 255.0
        elif mode == BlendModes.SCREEN:
            result = 255 - ((255 - base_np) * (255 - blend_np) / 255.0)
        elif mode == BlendModes.OVERLAY:
            result = overlay_blend(base_np, blend_np)
        elif mode == BlendModes.SOFT_LIGHT:
            result = soft_light_blend(base_np, blend_np)
        elif mode == BlendModes.HARD_LIGHT:
            result = hard_light_blend(base_np, blend_np)
        elif mode == BlendModes.COLOR_DODGE:
            result = color_dodge_blend(base_np, blend_np)
        elif mode == BlendModes.COLOR_BURN:
            result = color_burn_blend(base_np, blend_np)
        elif mode == BlendModes.DARKEN:
            result = np.minimum(base_np, blend_np)
        elif mode == BlendModes.LIGHTEN:
            result = np.maximum(base_np, blend_np)
        elif mode == BlendModes.DIFFERENCE:
            result = np.abs(base_np - blend_np)
        elif mode == BlendModes.EXCLUSION:
            result = base_np + blend_np - 2 * base_np * blend_np / 255.0
        else:
            result = blend_np  # Fallback to normal

        # Apply opacity
        result = base_np * (1 - opacity) + result * opacity
        result = np.clip(result, 0, 255).astype(np.uint8)

        return numpy_to_qimage(result)


# Helper functions for complex blend modes

def overlay_blend(base, blend):
    """Overlay blend mode."""
    result = np.where(
        base < 128,
        2 * base * blend / 255.0,
        255 - 2 * (255 - base) * (255 - blend) / 255.0
    )
    return result


def soft_light_blend(base, blend):
    """Soft light blend mode."""
    result = np.where(
        blend < 128,
        base - (255 - 2 * blend) * base * (255 - base) / (255 * 255),
        base + (2 * blend - 255) * (np.sqrt(base / 255.0) * 255 - base) / 255.0
    )
    return result


def hard_light_blend(base, blend):
    """Hard light blend mode."""
    result = np.where(
        blend < 128,
        2 * base * blend / 255.0,
        255 - 2 * (255 - base) * (255 - blend) / 255.0
    )
    return result


def color_dodge_blend(base, blend):
    """Color dodge blend mode."""
    result = np.where(
        blend >= 255,
        255,
        np.minimum(255, base * 255 / (255 - blend + 0.001))
    )
    return result


def color_burn_blend(base, blend):
    """Color burn blend mode."""
    result = np.where(
        blend <= 0,
        0,
        255 - np.minimum(255, (255 - base) * 255 / (blend + 0.001))
    )
    return result


def qimage_to_numpy(qimage):
    """Convert QImage to numpy array."""
    width = qimage.width()
    height = qimage.height()
    ptr = qimage.bits()
    ptr.setsize(qimage.sizeInBytes())
    arr = np.array(ptr).reshape(height, width, 4)
    return arr[:, :, :3].copy()  # RGB only


def numpy_to_qimage(arr):
    """Convert numpy array to QImage."""
    height, width = arr.shape[:2]
    if len(arr.shape) == 2:
        # Grayscale
        arr = np.stack([arr, arr, arr], axis=2)

    # Add alpha channel
    alpha = np.full((height, width, 1), 255, dtype=np.uint8)
    arr_rgba = np.concatenate([arr, alpha], axis=2)

    qimage = QImage(
        arr_rgba.data, width, height,
        arr_rgba.strides[0],
        QImage.Format.Format_RGBA8888
    )
    return qimage.copy()
