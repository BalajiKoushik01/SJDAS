"""
Camera RAW and Advanced Image Processing for SJ-DAS.

Professional RAW image processing with exposure, white balance,
and tone adjustments.
"""

import logging
from typing import Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger("SJ_DAS.CameraRAW")


class CameraRAW:
    """
    Camera RAW processing.

    Features:
        - Exposure adjustment
        - White balance
        - Highlights/Shadows recovery
        - Clarity and vibrance
        - Tone curve
    """

    def __init__(self):
        self.exposure = 0.0  # -2.0 to +2.0
        self.contrast = 0  # -100 to +100
        self.highlights = 0  # -100 to +100
        self.shadows = 0  # -100 to +100
        self.whites = 0  # -100 to +100
        self.blacks = 0  # -100 to +100
        self.clarity = 0  # -100 to +100
        self.vibrance = 0  # -100 to +100
        self.saturation = 0  # -100 to +100
        self.temperature = 0  # -100 to +100 (blue to yellow)
        self.tint = 0  # -100 to +100 (green to magenta)

    def process_image(
        self,
        image: np.ndarray,
        **adjustments
    ) -> np.ndarray:
        """
        Process image with RAW adjustments.

        Args:
            image: Input image (RGB)
            **adjustments: Adjustment parameters

        Returns:
            Processed image
        """
        result = image.astype(np.float32) / 255.0

        # Apply adjustments in order
        if 'exposure' in adjustments:
            result = self.adjust_exposure(result, adjustments['exposure'])

        if 'temperature' in adjustments or 'tint' in adjustments:
            temp = adjustments.get('temperature', 0)
            tint = adjustments.get('tint', 0)
            result = self.adjust_white_balance(result, temp, tint)

        if 'highlights' in adjustments or 'shadows' in adjustments:
            highlights = adjustments.get('highlights', 0)
            shadows = adjustments.get('shadows', 0)
            result = self.adjust_highlights_shadows(
                result, highlights, shadows)

        if 'clarity' in adjustments:
            result = self.adjust_clarity(result, adjustments['clarity'])

        if 'vibrance' in adjustments:
            result = self.adjust_vibrance(result, adjustments['vibrance'])

        if 'saturation' in adjustments:
            result = self.adjust_saturation(result, adjustments['saturation'])

        # Clip and convert back
        result = np.clip(result * 255, 0, 255).astype(np.uint8)

        logger.debug(
            f"Applied RAW processing with {len(adjustments)} adjustments")
        return result

    def adjust_exposure(self, image: np.ndarray, value: float) -> np.ndarray:
        """
        Adjust exposure (-2.0 to +2.0 stops).

        Args:
            image: Normalized image (0-1)
            value: Exposure adjustment in stops
        """
        # Exposure adjustment: multiply by 2^value
        factor = 2 ** value
        return image * factor

    def adjust_white_balance(
        self,
        image: np.ndarray,
        temperature: float,
        tint: float
    ) -> np.ndarray:
        """
        Adjust white balance.

        Args:
            image: Normalized RGB image
            temperature: -100 (blue) to +100 (yellow)
            tint: -100 (green) to +100 (magenta)
        """
        result = image.copy()

        # Temperature: adjust blue/yellow
        if temperature != 0:
            temp_factor = temperature / 100.0
            if temp_factor > 0:  # Warmer (more yellow/red)
                result[:, :, 0] *= (1 + temp_factor * 0.3)  # Red
                result[:, :, 2] *= (1 - temp_factor * 0.3)  # Blue
            else:  # Cooler (more blue)
                result[:, :, 0] *= (1 + temp_factor * 0.3)  # Red
                result[:, :, 2] *= (1 - temp_factor * 0.3)  # Blue

        # Tint: adjust green/magenta
        if tint != 0:
            tint_factor = tint / 100.0
            result[:, :, 1] *= (1 + tint_factor * 0.3)  # Green

        return result

    def adjust_highlights_shadows(
        self,
        image: np.ndarray,
        highlights: float,
        shadows: float
    ) -> np.ndarray:
        """
        Recover highlights and lift shadows.

        Args:
            image: Normalized image
            highlights: -100 (recover) to +100 (increase)
            shadows: -100 (darken) to +100 (lift)
        """
        # Convert to LAB for luminance adjustment
        lab = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2LAB)
        l_channel = lab[:, :, 0].astype(np.float32) / 255.0

        # Adjust highlights (bright areas)
        if highlights != 0:
            highlight_mask = l_channel > 0.7
            adjustment = -highlights / 100.0 * 0.3
            l_channel[highlight_mask] *= (1 + adjustment)

        # Adjust shadows (dark areas)
        if shadows != 0:
            shadow_mask = l_channel < 0.3
            adjustment = shadows / 100.0 * 0.3
            l_channel[shadow_mask] *= (1 + adjustment)

        # Convert back
        lab[:, :, 0] = np.clip(l_channel * 255, 0, 255).astype(np.uint8)
        result = cv2.cvtColor(
            lab, cv2.COLOR_LAB2RGB).astype(
            np.float32) / 255.0

        return result

    def adjust_clarity(self, image: np.ndarray, value: float) -> np.ndarray:
        """
        Adjust clarity (local contrast).

        Args:
            image: Normalized image
            value: -100 to +100
        """
        if value == 0:
            return image

        # Clarity = unsharp mask on luminance
        gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (0, 0), 5)

        # High-pass filter
        high_pass = cv2.subtract(gray, blurred)

        # Apply to luminance
        strength = value / 100.0
        enhanced = cv2.add(gray, (high_pass * strength).astype(np.uint8))

        # Convert back to RGB
        result = image.copy()
        factor = enhanced.astype(np.float32) / (gray.astype(np.float32) + 1e-6)
        result *= factor[:, :, np.newaxis]

        return result

    def adjust_vibrance(self, image: np.ndarray, value: float) -> np.ndarray:
        """
        Adjust vibrance (smart saturation).

        Args:
            image: Normalized image
            value: -100 to +100
        """
        if value == 0:
            return image

        # Convert to HSV
        hsv = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)

        # Vibrance: increase saturation of less saturated colors
        s_float = s.astype(np.float32) / 255.0
        adjustment = value / 100.0

        # Apply more to less saturated pixels
        mask = 1.0 - s_float
        s_float += adjustment * mask * 0.5

        s = np.clip(s_float * 255, 0, 255).astype(np.uint8)

        # Merge and convert back
        hsv = cv2.merge([h, s, v])
        result = cv2.cvtColor(
            hsv, cv2.COLOR_HSV2RGB).astype(
            np.float32) / 255.0

        return result

    def adjust_saturation(self, image: np.ndarray, value: float) -> np.ndarray:
        """
        Adjust overall saturation.

        Args:
            image: Normalized image
            value: -100 to +100
        """
        if value == 0:
            return image

        # Convert to HSV
        hsv = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)

        # Adjust saturation
        s_float = s.astype(np.float32)
        factor = 1 + (value / 100.0)
        s_float *= factor
        s = np.clip(s_float, 0, 255).astype(np.uint8)

        # Merge and convert back
        hsv = cv2.merge([h, s, v])
        result = cv2.cvtColor(
            hsv, cv2.COLOR_HSV2RGB).astype(
            np.float32) / 255.0

        return result

    def show_dialog(self):
        """Show parameters dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Camera RAW",
            "Camera RAW Filter settings coming soon.")


class PerspectiveCorrection:
    """
    Perspective correction and transformation tools.

    Features:
        - Auto-detect perspective
        - Manual 4-point correction
        - Lens distortion correction
        - Keystone correction
    """

    def correct_perspective(
        self,
        image: np.ndarray,
        src_points: np.ndarray,
        dst_points: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Correct perspective distortion.

        Args:
            image: Input image
            src_points: 4 source points (top-left, top-right, bottom-right, bottom-left)
            dst_points: 4 destination points (if None, use rectangle)

        Returns:
            Perspective-corrected image
        """
        h, w = image.shape[:2]

        # If no destination points, create rectangle
        if dst_points is None:
            # Calculate width and height from source points
            width_top = np.linalg.norm(src_points[1] - src_points[0])
            width_bottom = np.linalg.norm(src_points[2] - src_points[3])
            width = int(max(width_top, width_bottom))

            height_left = np.linalg.norm(src_points[3] - src_points[0])
            height_right = np.linalg.norm(src_points[2] - src_points[1])
            height = int(max(height_left, height_right))

            dst_points = np.array([
                [0, 0],
                [width - 1, 0],
                [width - 1, height - 1],
                [0, height - 1]
            ], dtype=np.float32)

        # Calculate perspective transform
        matrix = cv2.getPerspectiveTransform(
            src_points.astype(np.float32),
            dst_points.astype(np.float32)
        )

        # Apply transform
        result = cv2.warpPerspective(
            image,
            matrix,
            (int(dst_points[1][0]), int(dst_points[2][1]))
        )

        logger.debug("Applied perspective correction")
        return result

    def auto_detect_document(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Auto-detect document corners for perspective correction.

        Returns:
            4 corner points or None if not detected
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Edge detection
        edges = cv2.Canny(gray, 50, 150)

        # Find contours
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find largest quadrilateral
        for contour in sorted(contours, key=cv2.contourArea, reverse=True):
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            if len(approx) == 4:
                # Found quadrilateral
                points = approx.reshape(4, 2)

                # Order points: top-left, top-right, bottom-right, bottom-left
                points = self._order_points(points)

                logger.debug("Auto-detected document corners")
                return points

        logger.warning("Could not auto-detect document")
        return None

    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """Order points in clockwise order starting from top-left."""
        # Sort by y-coordinate
        sorted_pts = pts[np.argsort(pts[:, 1])]

        # Top two points
        top_pts = sorted_pts[:2]
        top_pts = top_pts[np.argsort(top_pts[:, 0])]

        # Bottom two points
        bottom_pts = sorted_pts[2:]
        bottom_pts = bottom_pts[np.argsort(bottom_pts[:, 0])]

        # Return in order: TL, TR, BR, BL
        return np.array([
            top_pts[0],
            top_pts[1],
            bottom_pts[1],
            bottom_pts[0]
        ])

    def correct_lens_distortion(
        self,
        image: np.ndarray,
        k1: float = 0.0,
        k2: float = 0.0
    ) -> np.ndarray:
        """
        Correct lens distortion (barrel/pincushion).

        Args:
            image: Input image
            k1: Radial distortion coefficient 1
            k2: Radial distortion coefficient 2
        """
        h, w = image.shape[:2]

        # Camera matrix (simplified)
        camera_matrix = np.array([
            [w, 0, w / 2],
            [0, h, h / 2],
            [0, 0, 1]
        ], dtype=np.float32)

        # Distortion coefficients
        dist_coeffs = np.array([k1, k2, 0, 0], dtype=np.float32)

        # Undistort
        result = cv2.undistort(image, camera_matrix, dist_coeffs)

        logger.debug(f"Corrected lens distortion: k1={k1}, k2={k2}")
        return result

    def show_dialog(self):
        """Show parameters dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Perspective Correction",
            "Perspective Correction tool coming soon.")
