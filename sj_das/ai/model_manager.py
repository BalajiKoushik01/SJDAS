"""
AI Model Manager for SJ-DAS.

Handles loading, caching, and managing AI models including
the trained StyleGAN for textile generation.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import cv2
    import numpy as np
    import torch
    _AI_LIBS_AVAILABLE = True
except Exception as e:
    logging.warning(f"ModelManager: Core AI libraries (torch/cv2/numpy) unavailable: {e}")
    cv2 = None
    np = None
    torch = None
    _AI_LIBS_AVAILABLE = False

from PyQt6.QtCore import QObject, pyqtSignal

try:
    from sj_das.core.ai_config import get_ai_config
    from sj_das.core.engines.llm.local_llm_engine import get_local_llm_engine
    from sj_das.core.engines.vision.sam_engine import SAMEngine
except Exception as e:
    logging.warning(f"ModelManager: Engine import error: {e}")
    get_local_llm_engine = None
    get_ai_config = None
    SAMEngine = None

logger = logging.getLogger("SJ_DAS.ModelManager")


class ModelManager(QObject):
    """
    Manages AI model lifecycle.

    Features:
        - Lazy loading (load on first use)
        - Model caching
        - GPU/CPU detection
        - Seamless post-processing
    """

    model_loaded = pyqtSignal(str)  # Model name
    model_error = pyqtSignal(str)   # Error message

    def __init__(self):
        super().__init__()
        self.models = {}
        self.device = self._detect_device()
        self.base_path = Path(__file__).parent.parent.parent

        # Initialize AI config
        self.ai_config = get_ai_config() if get_ai_config else None
        self.llm_engine = None
        self.sam_engine = None

        logger.info(f"Using device: {self.device}")

    def _detect_device(self) -> str:
        """Detect best available device."""
        if torch and torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def load_stylegan(self, model_path: str = None) -> bool:
        """
        Load StyleGAN model.

        Args:
            model_path: Path to model weights

        Returns:
            True if loaded successfully
        """
        if not torch:
            logger.error("Torch unavailable, cannot load StyleGAN")
            return False

        try:
            if "stylegan" in self.models:
                return True

            if model_path is None:
                # Auto-discover optimized model
                model_dir = self.base_path / "sj_das/models/stylegan_advanced"
                model_path = model_dir / "stylegan_final.pth"

            path_obj = Path(model_path)
            if not path_obj.exists():
                logger.error(f"Model file not found: {path_obj}")
                return False

            # Import model class dynamically to avoid circular imports
            import sys
            if str(self.base_path) not in sys.path:
                sys.path.append(str(self.base_path))

            from stylegan_model import StyleGenerator

            # Create and load model
            model = StyleGenerator(
                z_dim=128,
                w_dim=128,
                resolution=512,
                num_classes=2)

            checkpoint = torch.load(path_obj, map_location=self.device)

            # Robust loading logic
            state_dict = checkpoint
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                # Filter discriminator
                state_dict = {
                    k.replace('module.', ''): v 
                    for k, v in checkpoint['model_state_dict'].items() 
                    if 'discriminator' not in k
                }
            elif isinstance(checkpoint, dict) and 'g_ema' in checkpoint:
                state_dict = checkpoint['g_ema']

            model.load_state_dict(state_dict, strict=False)
            model.to(self.device).eval()

            # Cache model
            self.models["stylegan"] = model

            logger.info(f"StyleGAN loaded from {path_obj}")
            self.model_loaded.emit("stylegan")
            return True

        except Exception as e:
            error_msg = f"Failed to load StyleGAN: {e}"
            logger.error(error_msg)
            self.model_error.emit(error_msg)
            return False

    def get_stylegan(self):
        """Get loaded StyleGAN model."""
        if "stylegan" not in self.models:
            self.load_stylegan()
        return self.models.get("stylegan")

    def generate_textile(
            self, seed: Optional[int] = None, optimize_seamless: bool = True) -> 'np.ndarray':
        """
        Generate textile pattern using StyleGAN.
        """
        if not torch or not np:
            raise RuntimeError("AI Libraries unavailable")

        model = self.get_stylegan()
        if model is None:
            raise RuntimeError("StyleGAN not loaded")

        # Set seed if provided
        if seed is not None:
            torch.manual_seed(seed)
            if self.device == 'cuda':
                torch.cuda.manual_seed(seed)

        # Generate
        with torch.no_grad():
            z = torch.randn(1, 128).to(self.device)
            # Default to class 1 (Graph/Pattern) for richer textures
            labels = torch.tensor([1], device=self.device)

            # Inference
            generated_tensor = model(z, labels)

            # To Numpy [0, 255]
            img = (generated_tensor.squeeze().permute(1, 2, 0).cpu().numpy() + 1) * 127.5
            img = np.clip(img, 0, 255).astype(np.uint8)

            if optimize_seamless:
                img = self._make_seamless(img)

        return img

    def _make_seamless(self, image: 'np.ndarray',
                       overlap: int = 48) -> 'np.ndarray':
        """
        Advanced post-processing to enforce seamless tiling.
        """
        if not np: return image
        result = image.copy().astype(float)
        h, w = result.shape[:2]

        # Vertical Blend
        for i in range(overlap):
            alpha = (overlap - i) / overlap
            pass_strength = 0.5 * alpha
            top_row = result[i, :, :]
            bottom_row = result[h - 1 - i, :, :]
            new_top = top_row * (1 - pass_strength) + bottom_row * pass_strength
            new_bottom = bottom_row * (1 - pass_strength) + top_row * pass_strength
            result[i, :, :] = new_top
            result[h - 1 - i, :, :] = new_bottom

        # Horizontal Blend
        for i in range(overlap):
            alpha = (overlap - i) / overlap
            pass_strength = 0.5 * alpha
            left_col = result[:, i, :]
            right_col = result[:, w - 1 - i, :]
            new_left = left_col * (1 - pass_strength) + right_col * pass_strength
            new_right = right_col * (1 - pass_strength) + left_col * pass_strength
            result[:, i, :] = new_left
            result[:, w - 1 - i, :] = new_right

        return np.clip(result, 0, 255).astype(np.uint8)

    def analyze_design_with_llm(self, design_description: str,
                                image_analysis: Optional[str] = None) -> Optional[str]:
        """
        Analyze a textile design using Local LLM.
        """
        llm = self.get_llm()
        if llm and hasattr(llm, 'is_configured') and llm.is_configured():
            prompt = f"{design_description}\nImage Analysis: {image_analysis or 'N/A'}"
            return llm.analyze_design(prompt)

        logger.warning("LLM engine not configured, cannot analyze design")
        return None

    def get_design_suggestions(self, context: str,
                                suggestion_type: str = "color") -> Optional[str]:
        """
        Get intelligent design suggestions using Local LLM.
        """
        llm = self.get_llm()
        if llm and hasattr(llm, 'is_configured') and llm.is_configured():
            if suggestion_type == "color":
                return llm.get_color_recommendations(context)
            else:
                return llm.generate(f"Suggest {suggestion_type} for: {context}")

        logger.warning("LLM engine not configured, cannot get suggestions")
        return None

    def load_llm(self, model_path: Optional[str] = None) -> bool:
        """Load and configure Local LLM engine."""
        if get_local_llm_engine is None:
            logger.warning("Local LLM engine code not available")
            return False

        try:
            self.llm_engine = get_local_llm_engine()
            if not self.llm_engine: return False

            # Default path check
            if model_path is None:
                success = self.llm_engine.configure("")
            else:
                success = self.llm_engine.configure(model_path)

            if success:
                self.model_loaded.emit("llm")
                return True
            return False

        except Exception as e:
            error_msg = f"Failed to load LLM: {e}"
            logger.error(error_msg)
            self.model_error.emit(error_msg)
            return False

    def get_llm(self):
        """Get loaded LLM engine."""
        if self.llm_engine is None:
            self.load_llm()
        return self.llm_engine

    def load_sam(self) -> bool:
        """Load Segment Anything Model."""
        if SAMEngine is None:
            logger.warning("SAM Engine code not available")
            return False

        try:
            if self.sam_engine is not None:
                return True

            self.sam_engine = SAMEngine()
            if self.sam_engine.load_model():
                self.model_loaded.emit("sam")
                return True
            else:
                self.sam_engine = None
                return False

        except Exception as e:
            error_msg = f"Failed to load SAM: {e}"
            logger.error(error_msg)
            self.model_error.emit(error_msg)
            return False

    def get_sam(self):
        """Get loaded SAM engine."""
        if self.sam_engine is None:
            self.load_sam()
        return self.sam_engine


# Global Instance
_model_manager = None


def get_model_manager() -> ModelManager:
    """Get global ModelManager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
