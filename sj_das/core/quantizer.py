"""
Refactored ColorQuantizerEngine with Enhanced Error Handling and Caching
"""
import time

import numpy as np
from PIL import Image
from sklearn.cluster import MiniBatchKMeans

from sj_das.utils.decorators import handle_errors, validate_input
from sj_das.utils.enhanced_logger import get_logger, log_performance
from sj_das.utils.exceptions import (ImageProcessingException,
                                     InvalidImageError, QuantizationError)
from sj_das.utils.validation import InputValidator

logger = get_logger(__name__)


class ColorQuantizerEngine:
    """
    Advanced Color Quantization Engine.

    Features:
    - K-means clustering for palette extraction
    - Floyd-Steinberg dithering support
    - Optimized for textile designs
    - Robust error handling
    """

    def __init__(self):
        """Initialize color quantizer."""
        logger.info("ColorQuantizerEngine initialized")

    @log_performance(logger)
    @validate_input(
        image=lambda x: x is not None and isinstance(x, np.ndarray),
        k=lambda x: isinstance(x, int) and 1 <= x <= 256
    )
    def quantize(
        self,
        image: np.ndarray,
        k: int = 8,
        dither: bool = False
    ) -> np.ndarray:
        """
        Reduce image colors using K-means clustering with caching.

        Args:
            image: Input image (H, W, 3)
            k: Number of colors to reduce to
            dither: Whether to apply dithering

        Returns:
            Quantized image with k colors

        Raises:
            InvalidImageError: If image is invalid
            QuantizationError: If quantization fails
        """
        # Check cache first
        from sj_das.utils.image_cache import get_cache
        cache = get_cache()
        cached_result = cache.get(
            image, 'quantize', {
                'k': k, 'dither': dither})
        if cached_result is not None:
            logger.debug(f"Using cached quantization result")
            return cached_result

        start_time = time.time()

        try:
            # Validate input
            if not InputValidator.validate_image(image):
                raise InvalidImageError("Invalid input image for quantization")

            if k < 2 or k > 256:
                raise QuantizationError(
                    f"Invalid k value: {k}. Must be between 2 and 256")

            logger.debug(
                f"Quantizing {image.shape} image to {k} colors (dither={dither})")

            # K-Means Palette Extraction
            data = image.reshape(-1, 3)

            logger.debug(f"Running K-means on {len(data)} pixels")
            kmeans = MiniBatchKMeans(
                n_clusters=k,
                random_state=42,
                batch_size=min(4096, len(data)),
                max_iter=100
            ).fit(data)

            palette = kmeans.cluster_centers_.astype(np.uint8)
            logger.debug(f"Extracted palette: {palette.shape}")

            if not dither:
                # Simple mapping
                labels = kmeans.predict(data)
                quantized = palette[labels].reshape(
                    image.shape).astype(np.uint8)
                logger.info(f"Quantization complete (simple mapping)")

                # Cache result
                cache.put(
                    image, 'quantize', {
                        'k': k, 'dither': dither}, quantized)
                return quantized
            else:
                # Floyd-Steinberg dithering
                logger.debug("Applying Floyd-Steinberg dithering")
                result = self._dither_pil(image, k)
                logger.info(f"Quantization complete (with dithering)")

                # Cache result
                if result is not None:
                    cache.put(
                        image, 'quantize', {
                            'k': k, 'dither': dither}, result)
                return result

        except InvalidImageError:
            raise
        except Exception as e:
            logger.error(
                "Color quantization failed",
                context={"k": k, "dither": dither, "error": str(e)},
                exc_info=True
            )
            raise ImageProcessingException(
                f"Quantization failed: {e}",
                context={"k": k, "image_shape": image.shape}
            )

    @handle_errors(default_return=None)
    def _dither_pil(self, image: np.ndarray, k: int) -> np.ndarray:
        """
        Apply dithering using PIL.

        Args:
            image: BGR image
            k: Number of colors

        Returns:
            Dithered image or None if fails
        """
        try:
            # Convert BGR to RGB
            rgb = image[:, :, ::-1]
            pil_img = Image.fromarray(rgb)

            # Quantize with dithering
            quantized_pil = pil_img.quantize(colors=k, method=2, dither=1)
            quantized_pil = quantized_pil.convert('RGB')

            # Convert back to BGR numpy
            result = np.array(quantized_pil)[:, :, ::-1]
            return result

        except Exception as e:
            logger.warning(
                f"PIL dithering failed: {e}, using simple quantization")
            return None
