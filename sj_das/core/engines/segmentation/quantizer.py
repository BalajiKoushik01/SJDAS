import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans

from sj_das.utils.logger import logger


class ColorQuantizerEngine:
    """
    Industrial Smart Color Reducer.
    Converts True Color images to Indexed Color (Palettized) for Jacquard.
    Supports K-Means and Dithering.
    """

    def quantize(self, image: np.ndarray, k: int = 8,
                 dither: bool = False) -> np.ndarray:
        """
        Reduces image to k colors.

        Args:
            image: BGR image
            k: Number of colors
            dither: Apply Floyd-Steinberg Dithering
        """
        try:
            # 1. K-Means Palette Extraction
            data = image.reshape(-1, 3)
            kmeans = MiniBatchKMeans(
                n_clusters=k,
                random_state=42,
                batch_size=4096).fit(data)
            palette = kmeans.cluster_centers_.astype(np.uint8)

            if not dither:
                # Simple Mapping
                labels = kmeans.predict(data)
                quantized = palette[labels].reshape(image.shape)
                return quantized.astype(np.uint8)
            else:
                # Floyd-Steinberg Dithering (Error Diffusion)
                # Note: This is slow in pure Python, usually done in C++ or specialized libs (PIL/Pillow).
                # Using a vectorized approximation or simplified error diffusion.
                # For high performance, we might just use PIL here.
                return self._dither_pil(image, k)

        except Exception as e:
            logger.error(f"Quantization Error: {e}")
            return image

    def _dither_pil(self, img_bgr, k):
        """Use Pillow for high-quality Dithering (PMode)."""
        try:
            from PIL import Image
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)

            # Quantize
            quantized = pil_img.quantize(
                colors=k,
                method=Image.Quantize.MEDIANCUT,
                kmeans=k,
                dither=Image.Dither.FLOYDSTEINBERG)

            # Convert back
            res_rgb = np.array(quantized.convert('RGB'))
            return cv2.cvtColor(res_rgb, cv2.COLOR_RGB2BGR)
        except ImportError:
            logger.warning(
                "Pillow not installed. Falling back to non-dithered.")
            return self.quantize(img_bgr, k, False)
