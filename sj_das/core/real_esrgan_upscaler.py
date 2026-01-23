import os

import cv2
import numpy as np
import torch

from sj_das.utils.logger import logger


class RealESRGANUpscaler:
    """
    Real-ESRGAN Upscaler - Superior to EDSR.
    Better for photorealistic images.
    """

    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'ecosystem',
            'RealESRGAN_x4plus.pth')

    def load_model(self):
        """Loads Real-ESRGAN model."""
        if self.model is not None:
            return True

        if not os.path.exists(self.model_path):
            logger.warning("Real-ESRGAN model not found")
            return False

        try:
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer

            # Initialize model
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4)

            self.upsampler = RealESRGANer(
                scale=4,
                model_path=self.model_path,
                model=model,
                tile=0,
                tile_pad=10,
                pre_pad=0,
                half=True if self.device == "cuda" else False,
                device=self.device
            )

            self.model = model
            logger.info("Real-ESRGAN loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Real-ESRGAN load error: {e}")
            return False

    def upscale(self, image: np.ndarray, scale: int = 4) -> np.ndarray:
        """
        Upscales image using Real-ESRGAN.

        Args:
            image: BGR numpy array
            scale: Upscale factor (fixed at 4 for this model)

        Returns:
            Upscaled BGR image
        """
        if not self.load_model():
            logger.warning("Real-ESRGAN unavailable, using fallback")
            return self._fallback_upscale(image, scale)

        try:
            output, _ = self.upsampler.enhance(image, outscale=scale)
            return output

        except Exception as e:
            logger.error(f"Real-ESRGAN upscale error: {e}")
            return self._fallback_upscale(image, scale)

    def _fallback_upscale(self, img, scale):
        """Lanczos fallback."""
        h, w = img.shape[:2]
        new_dim = (w * scale, h * scale)
        return cv2.resize(img, new_dim, interpolation=cv2.INTER_LANCZOS4)
