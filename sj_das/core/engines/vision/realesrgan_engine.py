import os
import logging
import numpy as np

try:
    import torch
    import torchvision
    if not hasattr(torchvision.transforms, 'functional_tensor'):
        torchvision.transforms.functional_tensor = torchvision.transforms.functional
    from realesrgan import RealESRGANer
    from basicsr.archs.rrdbnet_arch import RRDBNet
    _AVAILABLE = True
except ImportError as e:
    logging_re = logging.getLogger("SJ_DAS.RealESRGANEngine")
    logging_re.warning(f"Real-ESRGAN engine dependencies missing: {e}")
    _AVAILABLE = False
except Exception as e:
    logging_re = logging.getLogger("SJ_DAS.RealESRGANEngine")
    logging_re.error(f"Real-ESRGAN engine initialization error: {e}")
    _AVAILABLE = False

logger = logging.getLogger("SJ_DAS.RealESRGANEngine")

class RealESRGANEngine:
    """
    Wrapper for Real-ESRGAN for high-quality upscaling of textile designs.
    """
    def __init__(self, scale=4):
        self.scale = scale
        self.upsampler = None
        self.is_ready = False
        self.model_path = os.path.join(
            os.getcwd(), 'sj_das', 'assets', 'models', 'vision', 'RealESRGAN_x4plus.pth')

    def load_model(self):
        if self.is_ready:
            return True
        
        if not _AVAILABLE:
            logger.error("Real-ESRGAN or BasicSR not installed.")
            return False

        if not os.path.exists(self.model_path):
            logger.warning(f"Real-ESRGAN weights not found at {self.model_path}. Upscaling will use Lanczos interpolation.")
            return False

        try:
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
            self.upsampler = RealESRGANer(
                scale=self.scale,
                model_path=self.model_path,
                model=model,
                tile=400,
                tile_pad=10,
                pre_pad=0,
                half=True # Use half precision for speed
            )
            self.is_ready = True
            return True
        except Exception as e:
            logger.error(f"Error loading Real-ESRGAN: {e}")
            return False

    def enhance(self, image: np.ndarray) -> np.ndarray:
        """
        Enhances the image. Falls back to Lanczos if model is unavailable.
        """
        if self.load_model():
            try:
                output, _ = self.upsampler.enhance(image, outscale=self.scale)
                return output
            except Exception as e:
                logger.error(f"Real-ESRGAN enhancement error: {e}")
        
        # Fallback to OpenCV Lanczos
        import cv2
        h, w = image.shape[:2]
        return cv2.resize(image, (w * self.scale, h * self.scale), interpolation=cv2.INTER_LANCZOS4)
