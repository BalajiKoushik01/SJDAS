import os

import clip
import numpy as np
import torch
from PIL import Image

from sj_das.utils.logger import logger


class CLIPEngine:
    """
    CLIP (Contrastive Language-Image Pre-training) Engine.
    Enables semantic understanding of images.
    """

    def __init__(self):
        self.model = None
        self.preprocess = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'ecosystem',
            'clip-vit-large-patch14.pt')

    def load_model(self):
        """Loads CLIP model."""
        if self.model is not None:
            return True

        try:
            # Load CLIP
            self.model, self.preprocess = clip.load(
                "ViT-L/14", device=self.device, download_root=os.path.dirname(self.model_path))
            logger.info("CLIP loaded successfully")
            return True

        except Exception as e:
            logger.error(f"CLIP load error: {e}")
            return False

    def describe_image(self, image: np.ndarray) -> str:
        """
        Generates description of image.

        Args:
            image: BGR numpy array

        Returns:
            Text description
        """
        if not self.load_model():
            return "CLIP unavailable"

        try:
            # Convert BGR to RGB PIL
            rgb = image[:, :, ::-1]
            pil_img = Image.fromarray(rgb)

            # Preprocess
            image_input = self.preprocess(pil_img).unsqueeze(0).to(self.device)

            # Textile-specific prompts
            text_prompts = [
                "a traditional Indian saree design",
                "a modern geometric textile pattern",
                "a floral motif fabric",
                "a paisley pattern design",
                "a temple border design",
                "a plain solid color fabric"
            ]

            text_tokens = clip.tokenize(text_prompts).to(self.device)

            # Get similarities
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                text_features = self.model.encode_text(text_tokens)

                # Normalize
                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)

                # Cosine similarity
                similarity = (100.0 * image_features @
                              text_features.T).softmax(dim=-1)

            # Get best match
            values, indices = similarity[0].topk(1)
            return text_prompts[indices[0].item()]

        except Exception as e:
            logger.error(f"CLIP describe error: {e}")
            return "Analysis failed"

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
