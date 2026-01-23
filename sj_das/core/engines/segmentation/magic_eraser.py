import os

import cv2
import numpy as np

from sj_das.utils.logger import logger


class MagicEraserEngine:
    """
    State-of-the-Art Background Removal.
    Uses U-2-Net (if available) for 'Magic' extraction.
    Customized for Textile: Output is 'Sticker-like' with clean edges, not fuzzy alpha.
    """

    def __init__(self):
        self.net = None
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'segmentation',
            'u2net.onnx')
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.net = cv2.dnn.readNetFromONNX(self.model_path)
                logger.info("Magic Eraser: U-2-Net Loaded Successfully.")
            except Exception as e:
                logger.error(f"Magic Eraser: Model Load Failed - {e}")
        else:
            logger.warning(
                "Magic Eraser: U-2-Net model not found. Using Hue-heuristic fallback.")

    def remove_background(self, image: np.ndarray,
                          refine: bool = True, smoothness: int = 1) -> np.ndarray:
        """
        Removes background.
        Args:
            image: BGR image
            refine: Whether to binarize and clean edges
            smoothness: Kernel size for smoothing (0=Sharp, 1=Light, 2=Heavy)
        """
        if self.net:
            mask = self._predict_u2net(image)
        else:
            mask = self._heuristic_mask(image)

        if refine:
            mask = self._refine_mask(mask, smoothness)

        # Apply Mask
        b, g, r = cv2.split(image)
        # Resize mask to original if needed (U2Net output is fixed usually)
        if mask.shape[:2] != image.shape[:2]:
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]))

        # Final Combine
        result = cv2.merge([b, g, r, mask])

        # Auto Crop transparent areas
        result = self._auto_crop(result)

        return result

    def _predict_u2net(self, img):
        """Run U-2-Net Inference."""
        # U2Net expects 320x320 input usually
        blob = cv2.dnn.blobFromImage(
            img, 1.0 / 255, (320, 320), (0, 0, 0), swapRB=True, crop=False)
        self.net.setInput(blob)
        output = self.net.forward()
        # Output is (1, 1, 320, 320) probability map
        mask = output[0, 0]
        # Normalize to 0-255
        mask = cv2.normalize(mask, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        return mask

    def _heuristic_mask(self, img):
        """Simple GrabCut or Threshold fallback."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Otsu threshold as simple guess
        _, mask = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return mask

    def _refine_mask(self, mask, smoothness=1):
        """
        Custom Improvement:
        Textile designs need Sharp Edges (Jacquard can't weave semi-transparent).
        """
        # 1. Binarize (Hard Cut)
        _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        if smoothness > 0:
            # 2. Smooth Edges (Open/Close)
            # Kernel size: 3 for 1, 5 for 2, etc. (2*s + 1)
            k_size = (smoothness * 2) + 1
            kernel = np.ones((k_size, k_size), np.uint8)
            smooth = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            smooth = cv2.morphologyEx(smooth, cv2.MORPH_CLOSE, kernel)
            return smooth

        return binary

    def _auto_crop(self, img_bgra):
        """Crops image to content bounding box."""
        alpha = img_bgra[:, :, 3]
        coords = cv2.findNonZero(alpha)
        if coords is None:
            return img_bgra
        x, y, w, h = cv2.boundingRect(coords)
        return img_bgra[y:y + h, x:x + w]
