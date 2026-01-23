from typing import Optional

import cv2
import numpy as np
import torch

from sj_das.utils.logger import logger


class ControlNetEngine:
    """
    ControlNet for structure-preserving textile generation.
    Generates designs from sketches while maintaining structure.
    """

    def __init__(self):
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_ready = False

    def load_model(self) -> bool:
        """Load ControlNet Canny model."""
        if self.pipeline is not None:
            return True

        try:
            from diffusers import (ControlNetModel,
                                   StableDiffusionControlNetPipeline,
                                   UniPCMultistepScheduler)

            logger.info("Loading ControlNet Canny model...")

            # Load ControlNet
            controlnet = ControlNetModel.from_pretrained(
                "lllyasviel/sd-controlnet-canny",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )

            # Load Stable Diffusion with ControlNet
            self.pipeline = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                controlnet=controlnet,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None
            )

            # Optimize scheduler
            self.pipeline.scheduler = UniPCMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )

            # Enable memory optimizations
            if self.device == "cuda":
                self.pipeline.enable_model_cpu_offload()
                self.pipeline.enable_attention_slicing()
            else:
                self.pipeline.to(self.device)

            self.is_ready = True
            logger.info("ControlNet loaded successfully")
            return True

        except Exception as e:
            logger.error(f"ControlNet load error: {e}")
            return False

    def generate_from_sketch(self, sketch_image: np.ndarray, prompt: str,
                             num_steps: int = 20, guidance_scale: float = 7.5) -> Optional[np.ndarray]:
        """
        Generate textile design from sketch.

        Args:
            sketch_image: BGR sketch/edge map
            prompt: Textile design description
            num_steps: Inference steps (default: 20)
            guidance_scale: How closely to follow prompt (default: 7.5)

        Returns:
            Generated BGR image or None if failed
        """
        if not self.load_model():
            logger.warning("ControlNet not available, returning original")
            return sketch_image

        try:
            # Prepare edge map
            edges = self._prepare_edges(sketch_image)

            # Enhance prompt for textiles
            enhanced_prompt = self._enhance_prompt(prompt)

            # Convert to PIL
            from PIL import Image
            edge_pil = Image.fromarray(edges)

            # Generate
            logger.info(
                f"Generating design from sketch: {enhanced_prompt[:50]}...")
            result = self.pipeline(
                enhanced_prompt,
                edge_pil,
                num_inference_steps=num_steps,
                guidance_scale=guidance_scale,
                negative_prompt="blurry, low quality, distorted, ugly, watermark, text"
            ).images[0]

            # Convert back to BGR numpy
            result_np = np.array(result)
            result_bgr = cv2.cvtColor(result_np, cv2.COLOR_RGB2BGR)

            logger.info("ControlNet generation complete")
            return result_bgr

        except Exception as e:
            logger.error(f"ControlNet generation error: {e}")
            return None

    def _prepare_edges(self, image: np.ndarray) -> np.ndarray:
        """Extract or enhance edges from image."""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Detect edges using Canny
        edges = cv2.Canny(gray, 100, 200)

        # Convert to RGB for ControlNet
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

        return edges_rgb

    def _enhance_prompt(self, prompt: str) -> str:
        """Add textile-specific enhancements to prompt."""
        textile_keywords = [
            "high quality textile design",
            "intricate patterns",
            "vibrant colors",
            "suitable for saree fabric",
            "detailed embroidery",
            "traditional Indian motifs"
        ]

        # Check if already enhanced
        if any(kw in prompt.lower() for kw in ["textile", "saree", "fabric"]):
            return prompt

        # Add enhancements
        enhanced = f"{prompt}, {', '.join(textile_keywords)}"
        return enhanced
