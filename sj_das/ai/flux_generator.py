import os
import logging

try:
    import numpy as np
    _LIBS_AVAILABLE = True
except Exception as e:
    logging.warning(f"FluxGenerator: Libraries unavailable: {e}")
    np = None
    _LIBS_AVAILABLE = False

try:
    import torch
except (ImportError, OSError):
    torch = None

from sj_das.utils.logger import logger


class FluxGenerator:
    """
    Flux.1 [schnell] Generator - SOTA Text-to-Image.
    4-step distilled model for ultra-fast generation.
    """

    def __init__(self):
        self.pipe = None
        self.device = "cuda" if torch and torch.cuda.is_available() else "cpu"
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

    def generate(self, params, width: int = 512, height: int = 512, num_steps: int = 4) -> 'np.ndarray':
        """
        Generates image from text prompt or DesignParameters.
        """
        if not self.load_model():
            logger.warning("Flux unavailable, using fallback.")
            return self._fallback_generate(width, height)

        try:
            # Handle prompt construction
            if hasattr(params, 'prompt'): # If raw object with prompt
                 raw_prompt = params.prompt
            elif isinstance(params, str):
                 raw_prompt = params
            else:
                 # It's DesignParameters
                 raw_prompt = self._build_textile_prompt(params)

            # Flux doesn't need much negative prompt, it adheres well.
            logger.info(f"Flux Generating: {raw_prompt[:60]}...")

            result = self.pipe(
                prompt=raw_prompt,
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

    def _build_textile_prompt(self, params) -> str:
        """Build a detailed prompt optimized for textile designs (Ported from SD)."""
        parts = []
        
        # Style Prefixes
        style_prefixes = {
            'kanchipuram': "traditional South Indian Kanchipuram silk saree design, heavy zari work, intricate patterns,",
            'banarasi': "classic Banarasi silk brocade design, Mughal motifs, gold thread work,",
            'paithani': "Maharashtrian Paithani saree design, peacock and lotus motifs, vibrant colors,",
            'traditional': "traditional Indian silk saree design, cultural motifs, ethnic patterns,"
        }
        
        # Add style prefix
        style = getattr(params, 'style', 'traditional')
        parts.append(style_prefixes.get(style, style_prefixes['traditional']))

        # Design type
        design_type = getattr(params, 'design_type', 'saree')
        parts.append(f"{design_type} design,")

        # Basic attributes
        if hasattr(params, 'colors') and params.colors:
             parts.append(f"{' and '.join(params.colors)} color scheme,")
        
        if hasattr(params, 'motifs') and params.motifs:
             parts.append(f"featuring {' '.join(params.motifs)} motifs,")

        # Quality Suffix for Flux
        parts.append("macro photography, ultra detailed, fabric texture, 4k, photorealistic")
        
        return " ".join(parts)

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
