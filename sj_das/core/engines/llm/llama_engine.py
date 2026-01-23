"""
Llama Engine for SJ-DAS.

Integrates local Llama models (via llama-cpp-python) for privacy-focused,
offline intelligent design analysis and recommendations.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("SJ_DAS.LlamaEngine")


@dataclass
class LlamaConfig:
    """Configuration for Local Llama Engine."""
    model_path: str
    n_ctx: int = 2048
    n_gpu_layers: int = 35  # Attempt to offload to GPU
    temperature: float = 0.7
    max_tokens: int = 512


class LlamaEngine:
    """
    Local Llama AI Engine.

    Features:
        - Offline design analysis
        - Privacy-first processing (no cloud API)
        - Supports GGUF models
    """

    def __init__(self, config: Optional[LlamaConfig] = None):
        self.config = config
        self.llm = None
        self.system_prompt = self._get_textile_system_prompt()
        self.conversation_history = []

    def configure(self, model_path: str) -> bool:
        """
        Configure and load the Llama model.

        Args:
            model_path: Path to the .gguf model file.

        Returns:
            True if loaded successfully.
        """
        try:
            # Model Discovery
            if not model_path:
                # Search for known models
                base_dir = Path(os.getcwd()) / "sj_das" / \
                    "assets" / "models" / "llm"

                # Priorities:
                # 1. Phi-3.5 (Microsoft Copilot) - User Request
                phi_path = next(base_dir.glob("Phi-3.5*.gguf"), None)

                # 2. Llama 3.2
                llama_path = next(base_dir.glob("Llama-3.2*.gguf"), None)

                if phi_path and phi_path.exists():
                    model_path = str(phi_path)
                    logger.info(
                        f"Auto-selected 'Microsoft Copilot' (Phi-3): {model_path}")
                elif llama_path and llama_path.exists():
                    model_path = str(llama_path)
                    logger.info(f"Auto-selected Llama 3.2: {model_path}")
                else:
                    logger.error(
                        "No compatible GGUF models found in assets/models/llm")
                    return False

            if not os.path.exists(model_path):
                logger.error(f"Llama model not found at {model_path}")
                return False

            self.config = LlamaConfig(model_path=model_path)

            try:
                from llama_cpp import Llama

                logger.info(f"Loading AI Model from {model_path}...")
                self.llm = Llama(
                    model_path=self.config.model_path,
                    n_ctx=self.config.n_ctx,  # High context for design docs
                    n_gpu_layers=self.config.n_gpu_layers,
                    verbose=True
                )

                logger.info("Llama model loaded successfully")
                return True

            except ImportError:
                logger.error(
                    "llama-cpp-python not installed. Run: pip install llama-cpp-python")
                return False
            except Exception as e:
                logger.error(f"Failed to load Llama model: {e}")
                return False

        except Exception as e:
            logger.error(f"Configuration error: {e}")
            return False

    def is_configured(self) -> bool:
        return self.llm is not None

    def _get_textile_system_prompt(self) -> str:
        return """You are an expert textile designer specializing in Indian saree design (Kanjivaram, Banarasi) and Jacquard weaving.
Your goal is to provide technical, artistic, and manufacturing advice for textile designs.
Analyze patterns, suggest traditional color palettes, and ensure loom compatibility."""

    def generate(self, prompt: str,
                 reset_conversation: bool = False) -> Optional[str]:
        """Generate response from Llama."""
        if not self.is_configured():
            logger.warning("Llama not configured")
            return None

        try:
            if reset_conversation:
                self.conversation_history = []

            # Construct prompt for Llama (ChatML style or similar)
            # This is a simplified prompting strategy
            full_prompt = f"System: {self.system_prompt}\n\nUser: {prompt}\n\nAssistant:"

            output = self.llm(
                full_prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stop=["User:", "System:"]
            )

            response_text = output['choices'][0]['text'].strip()
            self.conversation_history.append(
                {"user": prompt, "assistant": response_text})

            return response_text

        except Exception as e:
            logger.error(f"Llama generation error: {e}")
            return None

    def analyze_design(self, description: str) -> Optional[str]:
        return self.generate(f"Analyze this design description: {description}")

    def get_color_recommendations(self, context: str) -> Optional[str]:
        return self.generate(
            f"Suggest 3 traditional color palettes for this context: {context}")


# Global Instance
_llama_engine = None


def get_llama_engine() -> LlamaEngine:
    global _llama_engine
    if _llama_engine is None:
        _llama_engine = LlamaEngine()
    return _llama_engine
