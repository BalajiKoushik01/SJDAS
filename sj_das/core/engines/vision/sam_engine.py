import os
import logging
from typing import Optional

try:
    import cv2
    import numpy as np
    import torch
    _TORCH_AVAILABLE = True
except (ImportError, AttributeError) as e:
    logging.warning(f"SAMEngine: torch/cv2 unavailable: {e}")
    cv2 = None
    np = None
    torch = None
    _TORCH_AVAILABLE = False

try:
    from sj_das.utils.logger import logger
except Exception:
    import logging as _log
    logger = logging.getLogger("SJ_DAS.SAMEngine")


class SAMEngine:
    """
    Wrapper for Meta's Segment Anything Model (SAM).
    Provides "Click to Segment" functionality.
    """

    def __init__(self):
        self.predictor = None
        self.generator = None
        self.model_cfg = os.getenv("SAM2_MODEL_CFG", "sam2.1_hiera_l.yaml")
        
        # Search for model in multiple locations
        possible_paths = [
            os.getenv("SAM2_CHECKPOINT"),
            os.path.join(os.getcwd(), 'sj_das', 'assets', 'models', 'sam2', 'sam2.1_hiera_large.pt'),
            os.path.join(os.getcwd(), 'models', 'sam2.1_hiera_large.pt'),
            os.path.abspath("sam2.1_hiera_large.pt")
        ]
        
        self.model_path = None
        for p in possible_paths:
            if p and os.path.exists(p):
                self.model_path = p
                break
        
        if not self.model_path:
            self.model_path = possible_paths[1] # Default to the standard location
            
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._last_image_hash: Optional[int] = None

    def load_model(self):
        """Loads SAM2 model."""
        if self.is_ready:
            return True

        if not os.path.exists(self.model_path):
            logger.error(f"SAM2 Model file not found at {self.model_path}")
            return False

        try:
            from sam2.build_sam import build_sam2
            from sam2.sam2_image_predictor import SAM2ImagePredictor
            from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

            logger.info(f"Loading SAM2 (hiera-large) on {self.device}...")
            sam2_model = build_sam2(self.model_cfg, self.model_path, device=self.device)
            self.predictor = SAM2ImagePredictor(sam2_model)
            self.generator = SAM2AutomaticMaskGenerator(sam2_model)
            self.is_ready = True
            logger.info("SAM2 Loaded Successfully.")
            return True

        except ImportError:
            logger.error("SAM2 Library missing. pip install sam2")
            return False
        except Exception as e:
            logger.error(f"SAM2 Load Error: {e}")
            return False

    def set_image(self, image: np.ndarray):
        """Pre-computes embedding for the image."""
        if not self.load_model():
            return

        # Cache check
        current_hash = hash(image.tobytes())
        if hasattr(self, '_last_image_hash') and self._last_image_hash == current_hash:
            return

        try:
            # SAM2 expects BGR numpy array
            self.predictor.set_image(image)
            self._last_image_hash = current_hash

        except Exception as e:
            logger.error(f"SAM2 Embedding Error: {e}")

    def predict_mask(self, image: np.ndarray, point_coords=None,
                     point_labels=None) -> np.ndarray:
        """
        Predicts mask from points or generates all masks automatically.
        """
        self.set_image(image)

        if point_coords is None:
            # Automatic mask generation
            masks = self.generator.generate(image)
            return masks

        # Click-based prediction
        input_point = np.array(point_coords)
        input_label = np.array(point_labels)

        device_type = 'cuda' if 'cuda' in self.device else 'cpu'
        # Automatic dtype selection for CPU vs GPU
        dtype = torch.bfloat16 if device_type == 'cuda' else torch.float32
        
        with torch.inference_mode(), torch.autocast(device_type=device_type, dtype=dtype):
            masks, scores, _ = self.predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                multimask_output=True,
            )

        # Pick the best mask
        best_idx = np.argmax(scores)
        mask = masks[best_idx]
        
        # If mask is boolean, convert to uint8 (0, 255)
        if mask.dtype == bool:
            return (mask.astype(np.uint8) * 255)
        return mask.astype(np.uint8)
