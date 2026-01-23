import os

import numpy as np
import torch

from sj_das.utils.logger import logger


class FluxGenerator:
    """
    Flux.1 [schnell] Generator - SOTA Text-to-Image.
    4-step distilled model for ultra-fast generation.
    """

    def __init__(self):
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = "black-forest-labs/FLUX.1-schnell"

    def load_model(self):
        """Loads Flux.1 pipeline."""
        if self.pipe is not None:
            return True

        try:
            from diffusers import FluxPipeline

            logger.info(f"Loading Flux.1 [schnell] on {self.device}...")

            # Load with bfloat16 for efficiency
            self.pipe = FluxPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.bfloat16
            )
            self.pipe.to(self.device)

            # Enable memory optimizations
            if self.device == "cuda":
                self.pipe.enable_model_cpu_offload()

            logger.info("Flux.1 loaded successfully.")
            return True

        except Exception as e:
            logger.error(f"Flux Load Error: {e}")
            return False

    def generate(self, prompt: str, width: int = 512,
                 height: int = 512, num_steps: int = 4) -> np.ndarray:
        """
        Generates image from text prompt.

        Args:
            prompt: Text description
            width: Image width
            height: Image height
            num_steps: Inference steps (4 is optimal for schnell)

        Returns:
            BGR numpy array
        """
        if not self.load_model():
            logger.warning("Flux unavailable, using fallback.")
            return self._fallback_generate(width, height)

        try:
            # Textile-specific prompt enhancement
            enhanced_prompt = f"high quality textile design, {prompt}, intricate patterns, vibrant colors, suitable for saree fabric"

            result = self.pipe(
                prompt=enhanced_prompt,
                width=width,
                height=height,
                num_inference_steps=num_steps,
                guidance_scale=0.0  # Schnell doesn't use CFG
            ).images[0]

            # Convert PIL to numpy BGR
            img_array = np.array(result)
            img_bgr = img_array[:, :, ::-1]  # RGB to BGR

            return img_bgr

        except Exception as e:
            logger.error(f"Flux Generation Error: {e}")
            return self._fallback_generate(width, height)

    def _fallback_generate(self, w, h):
        """Procedural fallback pattern."""
        import cv2
        canvas = np.zeros((h, w, 3), dtype=np.uint8)

        # Simple gradient
        for i in range(h):
            color_val = int((i / h) * 255)
            canvas[i, :] = [color_val, 100, 200]

        # Add noise for texture
        noise = np.random.randint(0, 50, (h, w, 3), dtype=np.uint8)
        canvas = cv2.add(canvas, noise)

        return canvas
