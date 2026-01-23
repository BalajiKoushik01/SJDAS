"""Advanced Image Ingestion Engine for Textile Design.

Provides intelligent image preprocessing, quantization, and optimization
for converting photographs into loom-ready weave patterns.
"""

import logging

import cv2
import numpy as np

from .exceptions import AIProcessingError, ValidationError

logger = logging.getLogger(__name__)


class ImageIngestionEngine:
    """
    Advanced AI-powered image processing pipeline for textile design.

    Transforms raw photographs into production-ready weave patterns through:
    1. Bilateral filtering for texture smoothing
    2. CLAHE for illumination correction
    3. Intelligent color quantization (k-means)
    4. Edge-preserving cleanup

    Attributes:
        None (stateless processor)
    """

    def _quantize_sklearn(self, image_lab, max_colors):
        """
        Uses Scikit-Learn's MiniBatchKMeans for 'Best-in-Class' Color Quantization.
        Superior clustering for textile palettes compared to basic cv2.kmeans.
        """
        h, w = image_lab.shape[:2]
        image_array = image_lab.reshape((h * w, 3))

        try:
            from sklearn.cluster import MiniBatchKMeans
            clt = MiniBatchKMeans(
                n_clusters=max_colors,
                n_init=3,
                batch_size=4096)
            labels = clt.fit_predict(image_array)
            quantized = clt.cluster_centers_.astype("uint8")[labels]

            # Reshape back to image
            quantized_lab = quantized.reshape((h, w, 3))
            return cv2.cvtColor(quantized_lab, cv2.COLOR_LAB2BGR)

        except ImportError:
            # Fallback if sklearn install failed despite our best efforts
            print("Sklearn not found, falling back to CV2.")
            return self._quantize_cv2(image_lab, max_colors)

    def _quantize_cv2(self, image_lab, max_colors):
        # ... (Existing CV2 Logic as Fallback) ...
        data = image_lab.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(
            data, max_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        res = centers[labels.flatten()].reshape(image_lab.shape)
        return cv2.cvtColor(res, cv2.COLOR_LAB2BGR)

    def process_image(
        self,
        image_path: str,
        target_width: int = 480,
        max_colors: int = 8
    ) -> np.ndarray:
        """
        Process image into loom-ready format with intelligent preprocessing.

        Args:
            image_path: Path to input image file
            target_width: Target width in pixels (hooks)
            max_colors: Maximum number of yarn colors

        Returns:
            Processed BGR image ready for weave mapping

        Raises:
            AIProcessingError: If image cannot be processed
            ValidationError: If parameters are invalid
            FileIOError: If file cannot be read
        """
        # Validation
        if not isinstance(image_path, str) or not image_path:
            raise ValidationError("image_path must be a non-empty string")

        if not (100 <= target_width <= 4800):
            raise ValidationError(
                f"target_width must be between 100-4800, got {target_width}"
            )

        if not (2 <= max_colors <= 32):
            raise ValidationError(
                f"max_colors must be between 2-32, got {max_colors}"
            )

        try:
            # Load image
            logger.debug(f"Loading image: {image_path}")
            img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

            if img is None:
                raise AIProcessingError(
                    "Failed to load image",
                    f"File: {image_path}. Ensure file exists and is a valid image format."
                )

            # Handle transparency
            img = self._normalize_channels(img)

            # Resize with aspect preservation
            img_resized = self._smart_resize(img, target_width)

            # Advanced enhancement pipeline
            img_enhanced = self._enhance_image(img_resized)

            # Intelligent quantization
            img_quantized = self._quantize_sklearn(img_enhanced, max_colors)

            # Final cleanup
            img_clean = cv2.medianBlur(img_quantized, 3)

            logger.info(
                f"Processed image: {img.shape} -> {img_clean.shape}, "
                f"{max_colors} colors"
            )

            return img_clean

        except cv2.error as e:
            raise AIProcessingError(
                "OpenCV processing error",
                str(e)
            )
        except Exception as e:
            if isinstance(e, (AIProcessingError, ValidationError)):
                raise
            raise AIProcessingError(
                "Unexpected error during image processing",
                str(e)
            )

    def _normalize_channels(self, img: np.ndarray) -> np.ndarray:
        """Convert image to standard BGR format."""
        if len(img.shape) == 2:
            # Grayscale -> BGR
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        if img.shape[2] == 4:
            # BGRA -> BGR with white background
            trans_mask = img[:, :, 3] == 0
            img[trans_mask] = [255, 255, 255, 255]
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return img

    def _smart_resize(
        self,
        img: np.ndarray,
        target_width: int
    ) -> np.ndarray:
        """Resize image preserving aspect ratio with optimal interpolation."""
        h, w = img.shape[:2]
        aspect_ratio = h / w
        target_height = int(target_width * aspect_ratio)

        # Choose best interpolation method
        # Lanczos4: Best quality for downscaling
        # Linear: Good balance for upscaling
        interp = cv2.INTER_LANCZOS4 if target_width < w else cv2.INTER_LINEAR

        return cv2.resize(
            img,
            (target_width, target_height),
            interpolation=interp
        )

    def _enhance_image(self, img: np.ndarray) -> np.ndarray:
        """Apply advanced enhancement pipeline."""
        # 1. Texture smoothing (preserves edges)
        # Bilateral filter: Removes fabric texture while keeping pattern sharp
        img_smooth = cv2.bilateralFilter(
            img, d=9, sigmaColor=75, sigmaSpace=75)

        # 2. Illumination correction
        # CLAHE in LAB color space for better results
        lab = cv2.cvtColor(img_smooth, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)

        lab_enhanced = cv2.merge((l_enhanced, a, b))

        return lab_enhanced

    def extract_edges_for_jacquard(self, img_cv):
        """Returns a binary edge map suitable for 'Binder' points."""
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return edges
