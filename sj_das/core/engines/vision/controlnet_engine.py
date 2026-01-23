import os

import cv2
import numpy as np
import torch
from PIL import Image

from sj_das.utils.logger import logger

# Conditional imports to handle DLL load failures
try:
    from diffusers import (ControlNetModel, StableDiffusionControlNetPipeline,
                           UniPCMultistepScheduler)
    DIFFUSERS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Diffusers not available: {e}")
    logger.info("ControlNet features will be disabled")
    DIFFUSERS_AVAILABLE = False
    # Create dummy classes to prevent NameError
    StableDiffusionControlNetPipeline = None
    ControlNetModel = None
    UniPCMultistepScheduler = None


class ControlNetEngine:
    """
    Sketch-to-Design Engine using ControlNet (Canny) + Stable Diffusion 1.5.
    """

    def __init__(self):
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_path = os.path.join(
            os.getcwd(),
            "sj_das",
            "assets",
            "models",
            "controlnet",
            "control_v11p_sd15_canny.pth")
        # Reuse existing SD model if possible, but ControlNet needs specific pipeline
        # For simplicity, we load standard SD1.5 from cache or local
        self.base_model = "runwayml/stable-diffusion-v1-5"

    def load_model(self):
        if self.pipeline:
            return True

        try:
            logger.info("Loading ControlNet Canny model...")

            # Try HuggingFace cache first
            controlnet = ControlNetModel.from_pretrained(
                "lllyasviel/sd-controlnet-canny",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                cache_dir=os.path.expanduser("~/.cache/huggingface")
            )

            logger.info("Loading SD for ControlNet...")
            self.pipeline = StableDiffusionControlNetPipeline.from_pretrained(
                self.base_model,
                controlnet=controlnet,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None,
                cache_dir=os.path.expanduser("~/.cache/huggingface")
            )

            # Optimization
            self.pipeline.scheduler = UniPCMultistepScheduler.from_config(
                self.pipeline.scheduler.config)

            if self.device == "cuda":
                self.pipeline.enable_model_cpu_offload()
            else:
                self.pipeline.to(self.device)

            logger.info("ControlNet Engine Ready")
            return True

        except Exception as e:
            logger.error(f"ControlNet load error: {e}")
            logger.warning("ControlNet not available, returning original")
            return False

    def generate_from_sketch(self, sketch_img: np.ndarray,
                             prompt: str) -> np.ndarray:
        """
        Transform a sketch (Canny edge map or drawing) into a design.
        """
        if not self.load_model():
            return None

        try:
            # Preprocess sketch to Canny if it's not already
            # Ideally user provides a line drawing. We ensure it's suitable.
            image = Image.fromarray(
                cv2.cvtColor(
                    sketch_img,
                    cv2.COLOR_BGR2RGB))

            # If image is not edge map, Canny it?
            # Assuming user gives a refined sketch or we force Canny.
            # Let's force Canny to be safe, high thresholds
            image_np = np.array(image)
            image_canny = cv2.Canny(image_np, 100, 200)
            image_canny = dataset = Image.fromarray(image_canny[:, :])

            logger.info(f"Generating from sketch: {prompt}")

            output = self.pipeline(
                prompt,
                image=image_canny,
                num_inference_steps=20,
                guidance_scale=9.0,
                controlnet_conditioning_scale=1.0
            ).images[0]

            return cv2.cvtColor(np.array(output), cv2.COLOR_RGB2BGR)

        except Exception as e:
            logger.error(f"ControlNet gen failed: {e}")
            return None
