import os

import cv2
import numpy as np

from sj_das.utils.logger import logger


class AIUpscaler:
    """
    AI Super-Resolution Engine.
    Scales images 2x, 3x, 4x using Deep Learning models (EDSR/ESPCN)
    or High-Quality Lanczos fallback.
    """

    def __init__(self):
        self.sr = cv2.dnn_superres.DnnSuperResImpl_create()
        self.models_loaded = {}
        # Path to models (user needs to download these potentially)
        # Path to models (Auto-downloaded by tools/download_models.py)
        self.model_path = os.path.join(
            os.getcwd(), 'sj_das', 'assets', 'models', 'super_res')

    def upscale(self, image: np.ndarray, scale: int = 4,
                model_name: str = 'edsr', loom_safe: bool = False) -> np.ndarray:
        """
        Upscale image using AI.

        Args:
            image: Source BGR image
            scale: 2, 3, or 4
            model_name: 'edsr' (Best), 'espcn' (Fast), 'fsrcnn' (Fast)
            loom_safe: If True, quantizes output to remove anti-aliasing (gradients).

        Returns:
            Upscaled BGR image
        """
        upscaled = None
        try:
            # 1. Try Loading AI Model
            # File structure: e.g. EDSR_x4.pb
            model_file = f"{model_name.upper()}_x{scale}.pb"
            full_path = os.path.join(self.model_path, model_file)

            if os.path.exists(full_path):
                logger.info(f"Using AI Model: {model_name} x{scale}")
                # Check if model is already loaded
                model_key = f"{model_name}_{scale}"
                if model_key not in self.models_loaded:
                    self.sr.readModel(full_path)
                    self.models_loaded[model_key] = True
                self.sr.setModel(model_name, scale)
                upscaled = self.sr.upsample(image)
            else:
                logger.warning(
                    f"AI Model {model_file} not found. Using High-Quality Cubic.")
                # Fallback
                upscaled = self._fallback_upscale(image, scale)

            if loom_safe and upscaled is not None:
                # Customization: Re-Quantize to original palette count?
                # Or just basic posterization
                # Let's simple K-Means reduction to 8 colors to ensure
                # cleanliness
                from sj_das.core.quantizer import ColorQuantizerEngine
                qe = ColorQuantizerEngine()
                # Keep more detail, but sharp
                upscaled = qe.quantize(upscaled, k=16, dither=False)

            return upscaled

        except Exception as e:
            logger.error(f"Upscale Error: {e}")
            return self._fallback_upscale(image, scale)

    def _fallback_upscale(self, img, scale):
        """High-quality procedural upscale (Lanczos + Sharpen)."""
        h, w = img.shape[:2]
        new_dim = (w * scale, h * scale)

        # 1. Lanczos Resampling (Best standard interpolation)
        upscaled = cv2.resize(img, new_dim, interpolation=cv2.INTER_LANCZOS4)

        # 2. Unsharp Masking to fake "Super Res" details
        gaussian = cv2.GaussianBlur(upscaled, (0, 0), 2.0)
        sharp = cv2.addWeighted(upscaled, 1.5, gaussian, -0.5, 0)

        return sharp
