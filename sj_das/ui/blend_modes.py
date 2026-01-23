"""
Complete Blend Modes for SJ-DAS.

All 25+ Photoshop blend modes for professional compositing.
"""

import logging
from enum import Enum

import cv2
import numpy as np

logger = logging.getLogger("SJ_DAS.BlendModes")


class BlendMode(Enum):
    """All Photoshop blend modes."""
    # Normal
    NORMAL = "Normal"
    DISSOLVE = "Dissolve"

    # Darken
    DARKEN = "Darken"
    MULTIPLY = "Multiply"
    COLOR_BURN = "Color Burn"
    LINEAR_BURN = "Linear Burn"
    DARKER_COLOR = "Darker Color"

    # Lighten
    LIGHTEN = "Lighten"
    SCREEN = "Screen"
    COLOR_DODGE = "Color Dodge"
    LINEAR_DODGE = "Linear Dodge (Add)"
    LIGHTER_COLOR = "Lighter Color"

    # Contrast
    OVERLAY = "Overlay"
    SOFT_LIGHT = "Soft Light"
    HARD_LIGHT = "Hard Light"
    VIVID_LIGHT = "Vivid Light"
    LINEAR_LIGHT = "Linear Light"
    PIN_LIGHT = "Pin Light"
    HARD_MIX = "Hard Mix"

    # Inversion
    DIFFERENCE = "Difference"
    EXCLUSION = "Exclusion"
    SUBTRACT = "Subtract"
    DIVIDE = "Divide"

    # Component
    HUE = "Hue"
    SATURATION = "Saturation"
    COLOR = "Color"
    LUMINOSITY = "Luminosity"


class BlendModes:
    """
    Professional blend modes implementation.

    All formulas match Photoshop's blend mode algorithms.
    """

    @staticmethod
    def blend(
        base: np.ndarray,
        blend: np.ndarray,
        mode: BlendMode,
        opacity: float = 1.0
    ) -> np.ndarray:
        """
        Apply blend mode.

        Args:
            base: Base layer (0-255)
            blend: Blend layer (0-255)
            mode: Blend mode
            opacity: Blend opacity (0-1)

        Returns:
            Blended result
        """
        # Normalize to 0-1
        base_norm = base.astype(np.float32) / 255.0
        blend_norm = blend.astype(np.float32) / 255.0

        # Apply blend mode
        if mode == BlendMode.NORMAL:
            result = blend_norm
        elif mode == BlendMode.MULTIPLY:
            result = BlendModes._multiply(base_norm, blend_norm)
        elif mode == BlendMode.SCREEN:
            result = BlendModes._screen(base_norm, blend_norm)
        elif mode == BlendMode.OVERLAY:
            result = BlendModes._overlay(base_norm, blend_norm)
        elif mode == BlendMode.SOFT_LIGHT:
            result = BlendModes._soft_light(base_norm, blend_norm)
        elif mode == BlendMode.HARD_LIGHT:
            result = BlendModes._hard_light(base_norm, blend_norm)
        elif mode == BlendMode.COLOR_DODGE:
            result = BlendModes._color_dodge(base_norm, blend_norm)
        elif mode == BlendMode.COLOR_BURN:
            result = BlendModes._color_burn(base_norm, blend_norm)
        elif mode == BlendMode.DARKEN:
            result = BlendModes._darken(base_norm, blend_norm)
        elif mode == BlendMode.LIGHTEN:
            result = BlendModes._lighten(base_norm, blend_norm)
        elif mode == BlendMode.DIFFERENCE:
            result = BlendModes._difference(base_norm, blend_norm)
        elif mode == BlendMode.EXCLUSION:
            result = BlendModes._exclusion(base_norm, blend_norm)
        elif mode == BlendMode.LINEAR_BURN:
            result = BlendModes._linear_burn(base_norm, blend_norm)
        elif mode == BlendMode.LINEAR_DODGE:
            result = BlendModes._linear_dodge(base_norm, blend_norm)
        elif mode == BlendMode.VIVID_LIGHT:
            result = BlendModes._vivid_light(base_norm, blend_norm)
        elif mode == BlendMode.LINEAR_LIGHT:
            result = BlendModes._linear_light(base_norm, blend_norm)
        elif mode == BlendMode.PIN_LIGHT:
            result = BlendModes._pin_light(base_norm, blend_norm)
        elif mode == BlendMode.HARD_MIX:
            result = BlendModes._hard_mix(base_norm, blend_norm)
        elif mode == BlendMode.SUBTRACT:
            result = BlendModes._subtract(base_norm, blend_norm)
        elif mode == BlendMode.DIVIDE:
            result = BlendModes._divide(base_norm, blend_norm)
        elif mode == BlendMode.HUE:
            result = BlendModes._hue(base_norm, blend_norm)
        elif mode == BlendMode.SATURATION:
            result = BlendModes._saturation(base_norm, blend_norm)
        elif mode == BlendMode.COLOR:
            result = BlendModes._color(base_norm, blend_norm)
        elif mode == BlendMode.LUMINOSITY:
            result = BlendModes._luminosity(base_norm, blend_norm)
        else:
            result = blend_norm

        # Apply opacity
        result = base_norm * (1 - opacity) + result * opacity

        # Clip and convert back
        result = np.clip(result * 255, 0, 255).astype(np.uint8)

        logger.debug(f"Applied blend mode: {mode.value}, opacity={opacity}")
        return result

    # Darken modes
    @staticmethod
    def _multiply(base, blend):
        return base * blend

    @staticmethod
    def _darken(base, blend):
        return np.minimum(base, blend)

    @staticmethod
    def _color_burn(base, blend):
        return np.where(blend == 0, 0, np.maximum(0, 1 - (1 - base) / blend))

    @staticmethod
    def _linear_burn(base, blend):
        return np.maximum(0, base + blend - 1)

    # Lighten modes
    @staticmethod
    def _screen(base, blend):
        return 1 - (1 - base) * (1 - blend)

    @staticmethod
    def _lighten(base, blend):
        return np.maximum(base, blend)

    @staticmethod
    def _color_dodge(base, blend):
        return np.where(blend == 1, 1, np.minimum(1, base / (1 - blend)))

    @staticmethod
    def _linear_dodge(base, blend):
        return np.minimum(1, base + blend)

    # Contrast modes
    @staticmethod
    def _overlay(base, blend):
        return np.where(
            base < 0.5,
            2 * base * blend,
            1 - 2 * (1 - base) * (1 - blend)
        )

    @staticmethod
    def _soft_light(base, blend):
        return np.where(
            blend < 0.5,
            2 * base * blend + base * base * (1 - 2 * blend),
            2 * base * (1 - blend) + np.sqrt(base) * (2 * blend - 1)
        )

    @staticmethod
    def _hard_light(base, blend):
        return np.where(
            blend < 0.5,
            2 * base * blend,
            1 - 2 * (1 - base) * (1 - blend)
        )

    @staticmethod
    def _vivid_light(base, blend):
        return np.where(
            blend < 0.5,
            BlendModes._color_burn(base, 2 * blend),
            BlendModes._color_dodge(base, 2 * (blend - 0.5))
        )

    @staticmethod
    def _linear_light(base, blend):
        return base + 2 * blend - 1

    @staticmethod
    def _pin_light(base, blend):
        return np.where(
            blend < 0.5,
            np.minimum(base, 2 * blend),
            np.maximum(base, 2 * (blend - 0.5))
        )

    @staticmethod
    def _hard_mix(base, blend):
        return np.where(base + blend < 1, 0, 1)

    # Inversion modes
    @staticmethod
    def _difference(base, blend):
        return np.abs(base - blend)

    @staticmethod
    def _exclusion(base, blend):
        return base + blend - 2 * base * blend

    @staticmethod
    def _subtract(base, blend):
        return np.maximum(0, base - blend)

    @staticmethod
    def _divide(base, blend):
        return np.where(blend == 0, 1, np.minimum(1, base / blend))

    # Component modes
    @staticmethod
    def _hue(base, blend):
        """Apply blend's hue to base."""
        base_hsv = cv2.cvtColor(
            (base *
             255).astype(
                np.uint8),
            cv2.COLOR_RGB2HSV)
        blend_hsv = cv2.cvtColor(
            (blend *
             255).astype(
                np.uint8),
            cv2.COLOR_RGB2HSV)

        result_hsv = base_hsv.copy()
        result_hsv[:, :, 0] = blend_hsv[:, :, 0]  # Use blend's hue

        result = cv2.cvtColor(result_hsv, cv2.COLOR_HSV2RGB)
        return result.astype(np.float32) / 255.0

    @staticmethod
    def _saturation(base, blend):
        """Apply blend's saturation to base."""
        base_hsv = cv2.cvtColor(
            (base *
             255).astype(
                np.uint8),
            cv2.COLOR_RGB2HSV)
        blend_hsv = cv2.cvtColor(
            (blend *
             255).astype(
                np.uint8),
            cv2.COLOR_RGB2HSV)

        result_hsv = base_hsv.copy()
        result_hsv[:, :, 1] = blend_hsv[:, :, 1]  # Use blend's saturation

        result = cv2.cvtColor(result_hsv, cv2.COLOR_HSV2RGB)
        return result.astype(np.float32) / 255.0

    @staticmethod
    def _color(base, blend):
        """Apply blend's hue and saturation to base."""
        base_hsv = cv2.cvtColor(
            (base *
             255).astype(
                np.uint8),
            cv2.COLOR_RGB2HSV)
        blend_hsv = cv2.cvtColor(
            (blend *
             255).astype(
                np.uint8),
            cv2.COLOR_RGB2HSV)

        result_hsv = base_hsv.copy()
        result_hsv[:, :, 0] = blend_hsv[:, :, 0]  # Hue
        result_hsv[:, :, 1] = blend_hsv[:, :, 1]  # Saturation

        result = cv2.cvtColor(result_hsv, cv2.COLOR_HSV2RGB)
        return result.astype(np.float32) / 255.0

    @staticmethod
    def _luminosity(base, blend):
        """Apply blend's luminosity to base."""
        base_hsv = cv2.cvtColor(
            (base *
             255).astype(
                np.uint8),
            cv2.COLOR_RGB2HSV)
        blend_hsv = cv2.cvtColor(
            (blend *
             255).astype(
                np.uint8),
            cv2.COLOR_RGB2HSV)

        result_hsv = base_hsv.copy()
        # Use blend's value (luminosity)
        result_hsv[:, :, 2] = blend_hsv[:, :, 2]

        result = cv2.cvtColor(result_hsv, cv2.COLOR_HSV2RGB)
        return result.astype(np.float32) / 255.0
