import os

import torch
from diffusers import FluxPipeline

from sj_das.utils.logger import logger


class FluxEngine:
    """
    State-of-the-Art Generative AI using Flux.1-Schnell.
    Requires significant VRAM (12GB+ recommended) or runs on CPU (slow).
    """

    def __init__(self):
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Flux Schnell is open weights (Apache 2.0)
        self.model_id = "black-forest-labs/FLUX.1-schnell"

    def load_model(self):
        if self.pipeline:
            return True

        try:
            logger.info(f"Loading Flux.1-Schnell from {self.model_id}...")
            # Load with bfloat16 for memory efficiency if on CUDA
            dtype = torch.bfloat16 if self.device == "cuda" else torch.float32

            self.pipeline = FluxPipeline.from_pretrained(
                self.model_id,
                torch_dtype=dtype,
                # local_files_only=True # Enable if we want to force offline
            )

            if self.device == "cuda":
                # Enable optimizations for lower VRAM
                self.pipeline.enable_model_cpu_offload()

            self.pipeline.to(self.device)
            logger.info("Flux Engine Loaded Successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load Flux: {e}")
            return False

    def generate(self, prompt: str, width: int = 1024,
                 height: int = 1024, steps: int = 4, seed: int = None):
        """
        Generate image using Flux.
        Flux Schnell is optimized for 4 steps.
        """
        if not self.load_model():
            return None

        try:
            generator = None
            if seed is not None:
                generator = torch.Generator(
                    device=self.device).manual_seed(seed)

            logger.info(f"Generating Flux Art: '{prompt}' ({width}x{height})")

            image = self.pipeline(
                prompt,
                guidance_scale=0.0,  # Schnell doesn't use guidance
                num_inference_steps=steps,
                width=width,
                height=height,
                generator=generator,
                max_sequence_length=256
            ).images[0]

            return image

        except Exception as e:
            logger.error(f"Flux generation failed: {e}")
            return None
