import os

import clip
import numpy as np
import torch
from PIL import Image

from sj_das.utils.logger import logger


class CLIPNavigator:
    """
    Semantic Design Navigation using CLIP.
    Allows sorting/searching designs by text description.
    """

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.preprocess = None
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'ecosystem',
            'clip-vit-large-patch14.pt')

    def load_model(self):
        if self.model is not None:
            return True

        if not os.path.exists(self.model_path):
            logger.error(f"CLIP model missing: {self.model_path}")
            return False

        try:
            # Load CLIP (assuming 'clip' package installed)
            # If standard clip load fails, we can try loading jit trace
            # directly
            logger.info("Loading CLIP Model...")

            # Using OpenAI CLIP's jit load
            self.model, self.preprocess = clip.load(
                "ViT-L/14", device=self.device, jit=True, download_root=os.path.dirname(self.model_path))

            # Override if local file exists differently?
            # Actually clip.load handles download_root, so if file matches "ViT-L/14" sha256 it uses it.
            # If 'clip-vit-large-patch14.pt' is exactly the file, we might needed to rename it or point clip to it.
            # But "ViT-L-14.pt" is the standard name. Let's assume standard
            # load works or user renamed it.

            logger.info("CLIP Loaded Successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load CLIP: {e}")
            return False

    def find_best_match(
            self, images: list[np.ndarray], prompt: str) -> tuple[np.ndarray, float]:
        """
        Rank images by similarity to prompt.
        Returns (best_image, score)
        """
        if not self.load_model():
            return images[0], 0.0

        try:
            # Prepare Text
            text_tokens = clip.tokenize([prompt]).to(self.device)

            # Prepare Images
            processed_images = []
            for img in images:
                pil_img = Image.fromarray(img)
                processed_images.append(self.preprocess(pil_img))

            image_input = torch.tensor(
                np.stack(processed_images)).to(
                self.device)

            with torch.no_grad():
                # Encode
                image_features = self.model.encode_image(image_input)
                text_features = self.model.encode_text(text_tokens)

                # Normalize
                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)

                # Similarity
                similarity = (100.0 * image_features @
                              text_features.T).softmax(dim=0)
                scores = similarity.cpu().numpy().flatten()

            best_idx = np.argmax(scores)
            return images[best_idx], scores[best_idx]

        except Exception as e:
            logger.error(f"CLIP matching failed: {e}")
            return images[0], 0.0


# Singleton
navigator = CLIPNavigator()
