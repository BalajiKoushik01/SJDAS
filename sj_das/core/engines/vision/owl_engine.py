
import logging

import numpy as np
import torch
from PIL import Image
from transformers import Owlv2ForObjectDetection, Owlv2Processor

logger = logging.getLogger("SJ_DAS.OwlEngine")


class OwlEngine:
    """
    Intelligent Vision Engine using Google's OWL-ViT v2.
    Enables Zero-Shot Object Detection via text queries.
    """

    def __init__(
            self, model_id="google/owlv2-base-patch16-ensemble", device=None):
        self.device = device if device else (
            "cuda" if torch.cuda.is_available() else "cpu")
        self.model_id = model_id
        self.processor = None
        self.model = None
        self.is_loaded = False

    def load_model(self):
        """Lazy load the model to save memory until needed."""
        if self.is_loaded:
            return

        try:
            logger.info(
                f"Loading Owl-ViT ({self.model_id}) on {self.device}...")
            self.processor = Owlv2Processor.from_pretrained(self.model_id)
            self.model = Owlv2ForObjectDetection.from_pretrained(
                self.model_id).to(self.device)
            self.model.eval()
            self.is_loaded = True
            logger.info("Owl-ViT loaded successfully.")

        except Exception as e:
            logger.error(f"Failed to load Owl-ViT: {e}")
            raise RuntimeError(f"Could not load vision model: {e}")

    def detect(self, image: np.ndarray,
               text_queries: list[str], threshold: float = 0.1):
        """
        Detect objects in image based on text descriptions.

        Args:
            image: Numpy array (BGR or RGB)
            text_queries: List of strings e.g. ["flower", "border"]
            threshold: Confidence threshold (0.0 to 1.0)

        Returns:
            List of dicts: {'label': str, 'box': [x1, y1, x2, y2], 'score': float}
        """
        if not self.is_loaded:
            self.load_model()

        if image is None:
            raise ValueError("Image cannot be None")

        # Convert to PIL RGB
        # If input is BGR (OpenCV default), convert to RGB
        if isinstance(image, np.ndarray):
            if image.shape[2] == 3:
                # Assume BGR if coming from cv2, converting to RGB for PIL
                # Heuristic: Check if we need conversion. Most internal apps differ.
                # Safest is to mandate RGB input or convert.
                # Let's assume input is BGR from OpenCV.
                img_rgb = image[..., ::-1]
                pil_img = Image.fromarray(img_rgb)
            elif image.shape[2] == 4:
                img_rgb = image[..., :3][..., ::-1]
                pil_img = Image.fromarray(img_rgb)
            else:
                pil_img = Image.fromarray(image)
        else:
            pil_img = image  # Assume PIL

        try:
            # Inputs
            inputs = self.processor(
                text=text_queries,
                images=pil_img,
                return_tensors="pt").to(
                self.device)

            # Inference
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Post-process
            # Target sizes needed for un-normalizing boxes
            target_sizes = torch.tensor([pil_img.size[::-1]]).to(self.device)
            results = self.processor.post_process_object_detection(
                outputs, target_sizes=target_sizes, threshold=threshold
            )[0]

            # Format output
            detections = []

            boxes = results["boxes"].cpu().numpy()
            scores = results["scores"].cpu().numpy()
            labels = results["labels"].cpu().numpy()

            for box, score, label_idx in zip(boxes, scores, labels):
                label_text = text_queries[label_idx]
                x1, y1, x2, y2 = map(int, box)

                detections.append({
                    "label": label_text,
                    "score": float(score),
                    "box": [x1, y1, x2, y2]
                })

            return detections

        except Exception as e:
            logger.error(f"Detection failed: {e}", exc_info=True)
            return []
