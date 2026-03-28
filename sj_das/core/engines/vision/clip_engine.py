import os
import logging
from typing import Any

logger_clip = logging.getLogger("SJ_DAS.CLIPEngine")

try:
    import clip
    import torch
    import numpy as np
    from PIL import Image
    _CLIP_AVAILABLE = True
except Exception as e:
    logger_clip.warning(f"CLIP/Torch not available (GPU/DLL issue): {e}")
    clip = None
    torch = None
    np = None
    Image = None
    _CLIP_AVAILABLE = False

try:
    from sj_das.utils.logger import logger
except Exception:
    import logging as logger


class CLIPEngine:
    """
    CLIP (Contrastive Language-Image Pre-training) Engine.
    Enables semantic understanding of images.
    """

    def __init__(self):
        self.model = None
        self.preprocess = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_dir = os.path.abspath(os.path.join(
            os.getcwd(), 'sj_das', 'assets', 'models', 'ecosystem'))
        self.model_path = os.path.join(self.model_dir, 'ViT-L-14.pt')

    def load_model(self):
        """Loads CLIP model."""
        if self.model is not None:
            return True

        try:
            # Check if file exists to avoid openai-clip downloading it or failing on name mismatch
            if not os.path.exists(self.model_path) and not os.path.exists(os.path.join(self.model_dir, "ViT-L-14.pt")):
                logger.warning(f"CLIP weights not found at {self.model_path}. Attempting to download to {self.model_dir}...")

            # Load CLIP - Use explicit path if possible or let it find in download_root
            self.model, self.preprocess = clip.load(
                "ViT-L/14", 
                device=self.device, 
                download_root=self.model_dir
            )
            logger.info("CLIP loaded successfully")
            return True

        except Exception as e:
            logger.error(f"CLIP load error: {e}")
            # Fallback check: maybe it's already in the cache but the path had an issue
            try:
                self.model, self.preprocess = clip.load("ViT-L/14", device=self.device)
                logger.info("CLIP loaded from default cache")
                return True
            except:
                return False

    def describe_image(self, image: np.ndarray) -> dict[str, Any]:
        """
        Generates description and style classification of image.
        """
        if not self.load_model():
            return {"label": "CLIP unavailable", "confidence": 0.0}

        try:
            # Convert BGR to RGB PIL
            rgb = image[:, :, ::-1]
            pil_img = Image.fromarray(rgb)

            # Textile-specific prompts from Spec v2
            labels = ["Kanjivaram saree", "Banarasi saree", "Pochampally ikat saree", "Paithani saree", "plain saree"]
            clean_labels = ["Kanjivaram", "Banarasi", "Pochampally", "Paithani", "Other"]
            
            text_tokens = clip.tokenize(labels).to(self.device)

            # Get similarities
            with torch.no_grad():
                image_input = self.preprocess(pil_img).unsqueeze(0).to(self.device)
                image_features = self.model.encode_image(image_input)
                text_features = self.model.encode_text(text_tokens)

                # Normalize
                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)

                # Cosine similarity
                similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

            # Get best match
            probs = similarity[0]
            best_idx = probs.argmax().item()
            
            return {
                "label": clean_labels[best_idx],
                "confidence": float(probs[best_idx]),
                "raw_probs": {l: float(p) for l, p in zip(clean_labels, probs)}
            }

        except Exception as e:
            logger.error(f"CLIP describe error: {e}")
            return {"label": "Analysis failed", "confidence": 0.0}

    def classify_style(self, image: np.ndarray) -> tuple[str, float]:
        """Shortcut for style classification."""
        res = self.describe_image(image)
        return res["label"], res["confidence"]

    def compare_images(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Computes similarity between two images.

        Returns:
            Similarity score (0-1)
        """
        if not self.load_model():
            return 0.0

        try:
            # Process both images
            rgb1 = img1[:, :, ::-1]
            rgb2 = img2[:, :, ::-1]

            pil1 = Image.fromarray(rgb1)
            pil2 = Image.fromarray(rgb2)

            input1 = self.preprocess(pil1).unsqueeze(0).to(self.device)
            input2 = self.preprocess(pil2).unsqueeze(0).to(self.device)

            with torch.no_grad():
                feat1 = self.model.encode_image(input1)
                feat2 = self.model.encode_image(input2)

                feat1 /= feat1.norm(dim=-1, keepdim=True)
                feat2 /= feat2.norm(dim=-1, keepdim=True)

                similarity = (feat1 @ feat2.T).item()

            return similarity

        except Exception as e:
            logger.error(f"CLIP compare error: {e}")
            return 0.0
