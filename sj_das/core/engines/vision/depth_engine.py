import os
import warnings

import cv2
import numpy as np
import torch

# Suppress warnings
warnings.filterwarnings('ignore')


class DepthEstimationEngine:
    """
    Monocular Depth Estimation using MiDaS.
    Used for 3D Fabric Simulation and Relief Maps.
    """

    def __init__(self):
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'ecosystem',
            'dpt_beit_large_512.pt')
        self.model_type = "DPT_Large"  # MiDaS v3.1 - Large
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = None

    def load_model(self):
        if self.model is not None:
            return True

        if not os.path.exists(self.model_path):
            print(f"Depth model missing: {self.model_path}")
            return False

        try:
            print("Loading MiDaS Depth Model (this may take a few seconds)...")
            # Load midas definition
            # Since we don't have the midas code repo, we rely on Torch Hub or manual definition
            # For offline reliability, we can try robust load, but DPT requires architecture definition
            # If standard hub load fails offline, we might be stuck unless we have the code.
            # Assuming 'midas' package or 'timm' is installed, or try torch hub
            # with local source if configured.

            # ATTEMPT 1: Torch Hub (requires internet usually, but caches)
            # We will use small wrapper if possible, or assume torch.hub.load
            # works cached

            self.model = torch.hub.load(
                "intel-isl/MiDaS", self.model_type, pretrained=False)
            self.model.load_state_dict(
                torch.load(
                    self.model_path,
                    map_location=self.device))

            self.model.to(self.device)
            self.model.eval()

            # Transforms
            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
            if self.model_type == "DPT_Large" or self.model_type == "DPT_Hybrid":
                self.transform = midas_transforms.dpt_transform
            else:
                self.transform = midas_transforms.small_transform

            print("Depth Model Loaded Successfully!")
            return True

        except Exception as e:
            print(f"Failed to load MiDaS Depth: {e}")
            # Fallback checks?
            return False

    def generate_depth_map(self, image: np.ndarray) -> np.ndarray:
        if not self.load_model():
            return None

        try:
            # Preprocess
            if len(image.shape) == 2:
                img = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            else:
                img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            input_batch = self.transform(img).to(self.device)

            with torch.no_grad():
                prediction = self.model(input_batch)

                # Resize to original resolution
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()

            depth_map = prediction.cpu().numpy()

            # Normalize to 0-255 uint8 visualization
            depth_min = depth_map.min()
            depth_max = depth_map.max()
            depth_normalized = (depth_map - depth_min) / \
                (depth_max - depth_min)
            depth_uint8 = (depth_normalized * 255).astype(np.uint8)

            # Pseudo-Color Map (Magma or similar looks 3D)
            depth_color = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_MAGMA)

            return depth_color

        except Exception as e:
            print(f"Depth generation failed: {e}")
            return None
