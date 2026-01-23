import os

import cv2
import numpy as np
from PIL import Image


class SegmentationEngine:
    def __init__(self):
        self.model = None
        self.device = None
        self.model_loaded = False
        self._torch_imported = False

    def _ensure_torch(self):
        """Lazy import torch only when needed"""
        if not self._torch_imported:
            global torch, transforms, UNetProduction
            import torch
            from torchvision import transforms

            from sj_das.core.unet import UNetProduction
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self._torch_imported = True

    def load_model(self):
        if self.model_loaded:
            return

        self._ensure_torch()  # Import torch only when loading model

        model_path = 'models/unet_saree_best.pth'
        if os.path.exists(model_path):
            try:
                self.model = UNetProduction(num_classes=3).to(self.device)
                self.model.load_state_dict(torch.load(
                    model_path, map_location=self.device))
                self.model.eval()
                print(f"Loaded U-Net model from {model_path}")
            except Exception as e:
                print(f"Failed to load U-Net: {e}")
                self.model = None
        else:
            print(f"Model not found at {model_path}")
        self.model_loaded = True

    def auto_segment(self, image_input, high_quality=True):
        """
        Segments image using U-Net if available, otherwise K-Means.
        Args:
            image_input (str or np.ndarray): Path to image or Numpy image (BGR).
            high_quality (bool): If True, uses higher resolution for inference/clustering.
        """
        # Lazy load
        self.load_model()

        if isinstance(image_input, str):
            img = cv2.imread(image_input)
        elif isinstance(image_input, np.ndarray):
            img = image_input.copy()
        else:
            return None

        if img is None:
            return None

        # Try U-Net first
        if self.model:
            try:
                # Resolution settings
                target_size = (1024, 1024) if high_quality else (512, 512)

                # Preprocess
                pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                transform = transforms.Compose([
                    transforms.Resize(target_size),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[
                            0.485, 0.456, 0.406], std=[
                            0.229, 0.224, 0.225])
                ])
                input_tensor = transform(pil_img).unsqueeze(0).to(self.device)

                # Inference
                with torch.no_grad():
                    output = self.model(input_tensor)
                    _, predicted = torch.max(output, 1)

                # Post-process
                mask = predicted.squeeze().cpu().numpy().astype(np.uint8)
                # Resize mask back to original size
                mask = cv2.resize(
                    mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
                return mask
            except Exception as e:
                print(f"U-Net inference failed: {e}, falling back to K-Means.")

        # Fallback to GrabCut (Graph Cut AI)
        # This is better than K-Means for structural segmentation

        if img.shape[0] < 10 or img.shape[1] < 10:
            # Too small for GrabCut
            return np.zeros(img.shape[:2], np.uint8)

        # 1. Initialize Mask
        mask = np.zeros(img.shape[:2], np.uint8)

        # 2. Define probable foreground (Center 80%)
        h, w = img.shape[:2]
        margin_x = int(w * 0.1)
        margin_y = int(h * 0.1)
        rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

        # 3. Models
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        try:
            # 4. Run GrabCut
            cv2.grabCut(
                img,
                mask,
                rect,
                bgdModel,
                fgdModel,
                5,
                cv2.GC_INIT_WITH_RECT)
        except cv2.error:
            # Fallback if GrabCut fails (e.g. rect invalid)
            return np.ones(img.shape[:2], np.uint8)

        # 5. Extract (0=BG, 1=FG, 2=Prob_BG, 3=Prob_FG)
        # We treat Prob_FG(3) and FG(1) as Body(1), others as BG(0)
        final_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

        # 6. Post-Process
        kernel = np.ones((5, 5), np.uint8)
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, kernel)

        return final_mask

    def get_overlay(self, image_path, mask, colors=None):
        """
        Creates a colored overlay based on the segmentation mask.
        Args:
            image_path: Path to source image
            mask: Segmentation mask (numpy array)
            colors: List of (B,G,R) tuples. Default: Green, Red, Blue.
        """
        img = cv2.imread(image_path)
        if img is None or mask is None:
            return None

        # Default Saree Colors (Body=Green, Border=Red, Pallu=Blue)
        if colors is None:
            colors = [
                # Class 0 (BG - usually Transparent/Green for visualization)
                [0, 255, 0],
                [0, 0, 255],   # Class 1
                [255, 0, 0],   # Class 2
                [0, 255, 255]  # Class 3
            ]

        overlay = np.zeros_like(img)

        # Determine num classes
        unique_classes = np.unique(mask)

        for cls_idx in unique_classes:
            if cls_idx > 0:  # Skip 0 (BG) optionally, or color it
                # Ensure we have enough colors
                color = colors[cls_idx % len(colors)]
                overlay[mask == cls_idx] = color

        return overlay
