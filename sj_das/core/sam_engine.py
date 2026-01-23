import os

import cv2
import numpy as np
import torch

from sj_das.utils.logger import logger


class SAMEngine:
    """
    Wrapper for Meta's Segment Anything Model (SAM).
    Provides "Click to Segment" functionality.
    """

    def __init__(self):
        self.predictor = None
        self.is_ready = False
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'sam',
            'sam_vit_b_01ec64.pth')
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """Loads the heavy model into memory."""
        if self.is_ready:
            return True

        if not os.path.exists(self.model_path):
            logger.error("SAM Model file not found.")
            return False

        try:
            from segment_anything import SamPredictor, sam_model_registry

            logger.info(f"Loading SAM (ViT-B) on {self.device}...")
            sam = sam_model_registry["vit_b"](checkpoint=self.model_path)
            sam.to(device=self.device)
            self.predictor = SamPredictor(sam)
            self.is_ready = True
            logger.info("SAM Loaded Successfully.")
            return True

        except ImportError:
            logger.error("SAM Library missing. pip install segment-anything")
            return False
        except Exception as e:
            logger.error(f"SAM Load Error: {e}")
            return False

    def set_image(self, image: np.ndarray):
        """Pre-computes embedding for the image (SLOW step)."""
        if not self.load_model():
            return

        try:
            # SAM expects RGB
            if image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            else:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            self.predictor.set_image(image)
        except Exception as e:
            logger.error(f"SAM Embedding Error: {e}")

    def predict_click(self, x: int, y: int, label: int = 1) -> np.ndarray:
        """
        Predicts mask from a single click.
        Args:
            x, y: Coordinates.
            label: 1 (Foreground) or 0 (Background).
        Returns:
            Binary Mask (uint8 0/255).
        """
        if not self.is_ready:
            return None

        try:
            input_point = np.array([[x, y]])
            input_label = np.array([label])

            masks, scores, logits = self.predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                multimask_output=True,  # We want the best 3
            )

            # Heuristic: Pick the one with highest score
            best_idx = np.argmax(scores)
            mask = masks[best_idx]

            return (mask * 255).astype(np.uint8)

        except Exception as e:
            logger.error(f"SAM Predict Error: {e}")
            return None
