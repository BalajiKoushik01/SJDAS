"""
Stable Diffusion Integration - Photorealistic textile design generation
Integrates with Hugging Face Diffusers for high-quality AI generation
"""

import warnings

import cv2
import numpy as np
import torch
from PIL import Image

# Suppress warnings
warnings.filterwarnings('ignore')


class StableDiffusionGenerator:
    """
    High-quality textile design generation using Stable Diffusion.
    Supports both local models and Hugging Face Inference API.
    """

    def __init__(self, use_local_model: bool = True):
        self.use_local_model = use_local_model
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False

        # Textile-specific prompt engineering
        self.style_prefixes = {
            'kanchipuram': "traditional South Indian Kanchipuram silk saree design, heavy zari work, intricate patterns,",
            'banarasi': "classic Banarasi silk brocade design, Mughal motifs, gold thread work,",
            'paithani': "Maharashtrian Paithani saree design, peacock and lotus motifs, vibrant colors,",
            'traditional': "traditional Indian silk saree design, cultural motifs, ethnic patterns,"
        }

        self.quality_suffix = ", high resolution, detailed, professional textile design, clean edges, symmetrical, traditional craftsmanship"

        self.negative_prompt = "blurry, low quality, distorted, asymmetric, modern patterns, western design, poor craftsmanship, pixelated"

    def load_model(self) -> bool:
        """Load Stable Diffusion model."""
        if self.model_loaded:
            return True

        try:
            if self.use_local_model:
                import os

                from diffusers import (DPMSolverMultistepScheduler,
                                       StableDiffusionPipeline)

                print("Loading Stable Diffusion model...")
                print(f"Device: {self.device}")

                # Use local model if available
                local_path = os.path.join(
                    os.getcwd(),
                    'sj_das',
                    'models',
                    'stable_diffusion',
                    'dreamshaper_8.safetensors')

                if os.path.exists(local_path):
                    print(f"Loading local checkpoint: {local_path}")
                    self.pipe = StableDiffusionPipeline.from_single_file(
                        local_path,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                        use_safetensors=True
                    )
                else:
                    print(
                        f"Local model not found at {local_path}, downloading from Hub...")
                    # Use a smaller, faster model
                    model_id = "runwayml/stable-diffusion-v1-5"
                    self.pipe = StableDiffusionPipeline.from_pretrained(
                        model_id,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )

                # Optimize
                self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                    self.pipe.scheduler.config
                )

                if self.device == "cuda":
                    self.pipe = self.pipe.to("cuda")
                    # Enable memory optimizations
                    self.pipe.enable_attention_slicing()
                    try:
                        self.pipe.enable_xformers_memory_efficient_attention()
                    except BaseException:
                        pass  # xformers not available

                self.model_loaded = True
                print("✅ Model loaded successfully!")
                return True
            else:
                # API mode - no model loading needed
                self.model_loaded = True
                return True

        except Exception as e:
            print(f"Error loading Stable Diffusion model: {e}")
            print("Falling back to procedural generation")
            return False

    def generate(self, params, num_images: int = 1) -> list[np.ndarray]:
        """
        Generate designs using Stable Diffusion.

        Args:
            params: DesignParameters from prompt parser
            num_images: Number of variations to generate

        Returns:
            List of generated images as numpy arrays
        """
        if not self.model_loaded and not self.load_model():
            return []

        # Build textile-specific prompt
        prompt = self._build_textile_prompt(params)

        print(f"Generating with SD prompt: {prompt[:100]}...")

        try:
            if self.use_local_model and self.pipe:
                return self._generate_local(prompt, num_images, params)
            else:
                return self._generate_api(prompt, num_images, params)
        except Exception as e:
            print(f"SD Generation error: {e}")
            return []

    def _generate_local(self, prompt: str, num_images: int,
                        params) -> list[np.ndarray]:
        """Generate using local Stable Diffusion model."""
        results = []

        # Calculate dimensions
        width = min(params.width_mm if params.width_mm else 512, 768)
        height = 512  # Standard

        # Make dimensions multiples of 8 (SD requirement)
        width = (width // 8) * 8
        height = (height // 8) * 8

        for i in range(num_images):
            print(f"  Generating variation {i+1}/{num_images}...")

            image = self.pipe(
                prompt=prompt,
                negative_prompt=self.negative_prompt,
                num_inference_steps=30,  # Balance quality/speed
                guidance_scale=7.5,
                width=width,
                height=height
            ).images[0]

            # Convert PIL to numpy
            img_array = np.array(image)
            results.append(img_array)

        return results

    def generate_variations(self, image: np.ndarray, prompt: str = "textile design variation, high quality",
                            strength: float = 0.75, num_images: int = 1) -> list[np.ndarray]:
        """Generate variations of an input image (Img2Img)."""
        if not self.model_loaded and not self.load_model():
            return []

        try:
            from diffusers import StableDiffusionImg2ImgPipeline
            from PIL import Image

            # Create Img2Img pipe from Txt2Img pipe components (Shared VRAM)
            img2img_pipe = StableDiffusionImg2ImgPipeline(
                **self.pipe.components)

            # Convert Numpy to PIL
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            init_image = Image.fromarray(image).resize((512, 512))

            print(
                f"Generating {num_images} variations with strength {strength}...")

            results = []
            for i in range(num_images):
                out_img = img2img_pipe(
                    prompt=prompt,
                    image=init_image,
                    strength=strength,
                    guidance_scale=7.5
                ).images[0]

                results.append(np.array(out_img))

            return results

        except Exception as e:
            print(f"Img2Img Error: {e}")
            return []

    def _generate_api(self, prompt: str, num_images: int,
                      params) -> list[np.ndarray]:
        """Generate using Hugging Face Inference API."""
        try:
            import io
            import os

            import requests

            API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

            # Get API token from environment or config
            api_token = os.environ.get("HUGGINGFACE_TOKEN", "")

            if not api_token:
                print("Warning: No Hugging Face API token found")
                print("Set HUGGINGFACE_TOKEN environment variable")
                return []

            headers = {"Authorization": f"Bearer {api_token}"}

            results = []
            for _i in range(num_images):
                response = requests.post(
                    API_URL,
                    headers=headers,
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "negative_prompt": self.negative_prompt,
                            "num_inference_steps": 30
                        }
                    }
                )

                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    img_array = np.array(image)
                    results.append(img_array)
                else:
                    print(f"API Error: {response.status_code}")

            return results

        except Exception as e:
            print(f"API generation error: {e}")
            return []

    def _build_textile_prompt(self, params) -> str:
        """Build a detailed prompt optimized for textile designs."""
        parts = []

        # Add style prefix if available
        if params.style and params.style in self.style_prefixes:
            parts.append(self.style_prefixes[params.style])
        else:
            parts.append(self.style_prefixes['traditional'])

        # Design type
        type_descriptions = {
            'border': "intricate border pattern, vertical design,",
            'pallu': "elaborate pallu end-piece design, ornate decorative section,",
            'blouse': "coordinating blouse piece design, complementary pattern,",
            'full_saree': "complete saree design with border, body, and pallu,"
        }
        parts.append(
            type_descriptions.get(
                params.design_type,
                "saree design,"))

        # Occasion context
        if params.occasion:
            occasion_desc = {
                'bridal': "bridal wear, wedding ceremony, heavy ornamentation, luxurious,",
                'festive': "festive celebration wear, vibrant and decorative,",
                'casual': "everyday wear, subtle elegance, comfortable,",
                'formal': "formal occasion wear, sophisticated and refined,"
            }
            parts.append(occasion_desc.get(params.occasion, ""))

        # Colors
        if params.colors:
            color_str = " and ".join(params.colors)
            parts.append(f"{color_str} color scheme,")

        # Motifs
        if params.motifs:
            motif_descriptions = {
                'peacock': "peacock feather motifs, traditional mayil design,",
                'lotus': "lotus flower patterns, kamal motifs,",
                'mango': "paisley mango designs, traditional kairi patterns,",
                'temple': "temple architecture motifs, gopuram designs,",
                'geometric': "geometric patterns, symmetrical shapes,",
                'flower': "floral patterns, blooming flowers,",
                'elephant': "elephant motifs, traditional gaja designs,",
                'leaf': "leaf and vine patterns, natural motifs,"
            }

            for motif in params.motifs[:2]:  # Limit to avoid overloading
                if motif in motif_descriptions:
                    parts.append(motif_descriptions[motif])

        # Weave type
        if params.weave:
            weave_desc = {
                'jeri': "gold zari thread work, metallic embellishments, shimmering texture,",
                'meena': "meenakari enamel work, colorful intricate details,",
                'ani': "smooth weave texture, refined craftsmanship,"
            }
            parts.append(weave_desc.get(params.weave, ""))

        # Complexity
        complexity_desc = {
            'simple': "clean and minimal design,",
            'medium': "moderately detailed pattern,",
            'complex': "highly detailed and intricate work,",
            'elaborate': "extremely ornate and elaborate craftsmanship, museum quality,"
        }
        parts.append(complexity_desc.get(params.complexity, ""))

        # Add quality suffix
        parts.append(self.quality_suffix)

        # Combine all parts
        prompt = " ".join(parts)

        return prompt

    def refine_for_loom(self, image: np.ndarray) -> np.ndarray:
        """Post-process SD output to be more loom-compatible."""
        # Enhance edges
        enhanced = cv2.detailEnhance(image, sigma_s=10, sigma_r=0.15)

        # Slight sharpening
        kernel = np.array([[-1, -1, -1],
                          [-1, 9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)

        # Blend
        result = cv2.addWeighted(enhanced, 0.7, sharpened, 0.3, 0)

        return result


class HybridGenerator:
    """
    Hybrid generation: Combines templates with AI variation.
    Best balance of speed, quality, and loom compatibility.
    """

    def __init__(self):
        from .procedural_generator import get_procedural_generator

        self.procedural = get_procedural_generator()
        self.sd_generator = None
        self.use_sd = False

    def generate(self, params, use_ai_variation: bool = True) -> np.ndarray:
        """
        Generatehybrid design.

        Args:
            params: DesignParameters
            use_ai_variation: Whether to use SD for variation (slower but more creative)

        Returns:
            Generated design as numpy array
        """
        # Start with procedural base (fast, loom-compatible)
        base_design = self.procedural.generate_design(params)

        if not use_ai_variation:
            return base_design

        # Optionally enhance with AI
        if self.sd_generator is None:
            self.sd_generator = StableDiffusionGenerator()

        # Use SD for img2img variation (preserves structure, adds creativity)
        try:
            # Use real SD Img2Img
            return self.sd_generator.generate_variations(
                base_design, strength=0.6, num_images=1)[0]
        except Exception as e:
            print(f"Hybrid variation error: {e}")
            return base_design

    def generate_variations(self, image, num=4):
        """Public API for UI to request variations only."""
        if self.sd_generator is None:
            self.sd_generator = StableDiffusionGenerator()
        return self.sd_generator.generate_variations(image, num_images=num)


# Global instances
_sd_generator = None
_hybrid_generator = None


def get_sd_generator() -> StableDiffusionGenerator:
    """Get or create Stable Diffusion generator."""
    global _sd_generator
    if _sd_generator is None:
        _sd_generator = StableDiffusionGenerator()
    return _sd_generator


def get_hybrid_generator() -> HybridGenerator:
    """Get or create hybrid generator."""
    global _hybrid_generator
    if _hybrid_generator is None:
        _hybrid_generator = HybridGenerator()
    return _hybrid_generator
