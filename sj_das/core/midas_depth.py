import os

import cv2
import numpy as np
import torch

from sj_das.utils.logger import logger


class MiDaSDepth:
    """
    MiDaS Depth Estimation Engine.
    Enhances 3D visualization with accurate depth maps.
    """

    def __init__(self):
        self.model = None
        self.transform = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'ecosystem',
            'dpt_beit_large_512.pt')

    def load_model(self):
        """Loads MiDaS model."""
        if self.model is not None:
            return True

        if not os.path.exists(self.model_path):
            logger.warning("MiDaS model not found")
            return False

        try:
            # Load MiDaS
            self.model = torch.hub.load(
                "intel-isl/MiDaS",
                "DPT_BEiT_L_512",
                pretrained=False)
            self.model.load_state_dict(
                torch.load(
                    self.model_path,
                    map_location=self.device))
            self.model.to(self.device)
            self.model.eval()

            # Load transforms
            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
            self.transform = midas_transforms.dpt_transform

            logger.info("MiDaS loaded successfully")
            return True

        except Exception as e:
            logger.error(f"MiDaS load error: {e}")
            return False

    def estimate_depth(self, image: np.ndarray) -> np.ndarray:
        """
        Estimates depth map from image.

        Args:
            image: BGR numpy array

        Returns:
            Depth map (normalized 0-255)
        """
        if not self.load_model():
            logger.warning("MiDaS unavailable, using fallback")
            return self._fallback_depth(image)

        try:
            # Convert BGR to RGB
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Transform
            input_batch = self.transform(rgb).to(self.device)

            # Predict
            with torch.no_grad():
                prediction = self.model(input_batch)
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=rgb.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()

            depth = prediction.cpu().numpy()

            # Normalize to 0-255
            depth_min = depth.min()
            depth_max = depth.max()
            depth_norm = (depth - depth_min) / (depth_max - depth_min) * 255
            depth_norm = depth_norm.astype(np.uint8)

            return depth_norm

        except Exception as e:
            logger.error(f"MiDaS depth error: {e}")
            return self._fallback_depth(image)

    def _fallback_depth(self, image):
        """Simple gradient-based depth fallback."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Use Sobel for pseudo-depth
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        magnitude = np.uint8(magnitude / magnitude.max() * 255)
        return magnitude
