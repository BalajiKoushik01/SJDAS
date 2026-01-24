"""
Local LLM Engine for SJ-DAS.

A generic wrapper around llama-cpp-python to support various GGUF models
(Llama 3, GLM-4, Phi-3) with automatic chat templating.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("SJ_DAS.LocalLLMEngine")


@dataclass
class LLMConfig:
    """Configuration for Local LLM Engine."""
    model_path: str
    n_ctx: int = 4096  # GLM-4 supports long context
    n_gpu_layers: int = -1  # -1 = All layers to GPU
    temperature: float = 0.7
    max_tokens: int = 1024
    chat_format: Optional[str] = None  # Allow auto-detection


class LocalLLMEngine:
    """
    Unified Local AI Engine.
    Supports GLM-4, Llama 3, and Phi-3 via GGUF.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config
        self.llm = None
        self.model_name = "Unknown"
        self.system_prompt = self._get_textile_system_prompt()
        self.conversation_history = []

    def configure(self, model_path: str = "") -> bool:
        """
        Configure and load the LLM model.
        Auto-detects best available model if path is empty.
        """
        try:
            # Model Discovery
            if not model_path:
                model_path = self._auto_discover_model()
                if not model_path:
                    return False

            if not os.path.exists(model_path):
                logger.error(f"Model not found at {model_path}")
                return False

            self.config = LLMConfig(model_path=model_path)
            
            # Detect model type for logging
            filename = os.path.basename(model_path).lower()
            if "glm-4" in filename:
                self.model_name = "GLM-4"
                # GLM-4 specific tweaks if needed
                self.config.n_ctx = 8192 
            elif "llama-3" in filename:
                self.model_name = "Llama 3"
            elif "phi-3" in filename:
                self.model_name = "Phi-3"
            
            logger.info(f"Initializing {self.model_name} from {model_path}...")

            try:
                from llama_cpp import Llama

                self.llm = Llama(
                    model_path=self.config.model_path,
                    n_ctx=self.config.n_ctx,
                    n_gpu_layers=self.config.n_gpu_layers,
                    verbose=True,
                    chat_format=self.config.chat_format # Allow auto-detection
                )

                logger.info(f"{self.model_name} loaded successfully (GPU Layers: {self.config.n_gpu_layers})")
                return True

            except ImportError:
                logger.error(
                    "llama-cpp-python not installed. Run: pip install llama-cpp-python")
                return False
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                return False

        except Exception as e:
            logger.error(f"Configuration error: {e}")
            return False

    def _auto_discover_model(self) -> Optional[str]:
        """Find the best available model in assets."""
        base_dir = Path(os.getcwd()) / "sj_das" / "assets" / "models" / "llm"
        
        # Priority List
        priorities = [
            "Qwen*.gguf",       # 1. Qwen (Best for Coding)
            "glm-4*.gguf",      # 2. GLM-4 (Best for Reasoning)
            "Llama-3.2*.gguf",  # 3. Llama 3.2
            "Phi-3.5*.gguf",    # 4. Phi-3
            "*.gguf"            # 5. Any other
        ]

        for pattern in priorities:
            found = next(base_dir.glob(pattern), None)
            if found:
                logger.info(f"Auto-selected model: {found.name}")
                return str(found)
        
        logger.error("No GGUF models found in assets/models/llm")
        return None

    def is_configured(self) -> bool:
        return self.llm is not None

    def _get_textile_system_prompt(self) -> str:
        return """You are an expert textile designer specializing in Indian saree design (Kanjivaram, Banarasi) and Jacquard weaving.
Your goal is to provide technical, artistic, and manufacturing advice for textile designs.
Analyze patterns, suggest traditional color palettes, and ensure loom compatibility."""

    def generate(self, prompt: str, reset_conversation: bool = False) -> Optional[str]:
        """
        Generate response using Chat Completion API.
        Handles message formatting automatically.
        """
        if not self.is_configured():
            return None

        try:
            if reset_conversation:
                self.conversation_history = []
                # Re-inject system prompt if needed, though usually handled by messages structure

            # Build Messages
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add History (Simplified context management)
            # For specific tasks, we might just want the current turn
            # But let's support basic history
            for turn in self.conversation_history[-4:]: # Keep last 4 turns
                messages.append({"role": "user", "content": turn["user"]})
                messages.append({"role": "assistant", "content": turn["assistant"]})
            
            # Current Prompt
            messages.append({"role": "user", "content": prompt})

            # Generate
            output = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stop=["User:", "System:", "<|user|>", "<|observation|>"] # Safety stops
            )

            response_text = output['choices'][0]['message']['content'].strip()
            
            # Update History
            self.conversation_history.append(
                {"user": prompt, "assistant": response_text})

            return response_text

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return None

    def analyze_design(self, description: str) -> Optional[str]:
        return self.generate(f"Analyze this design description: {description}")

    def get_color_recommendations(self, context: str) -> Optional[str]:
        return self.generate(
            f"Suggest 3 traditional color palettes for this context: {context}")


# Global Instance
_local_llm_engine = None


def get_local_llm_engine() -> LocalLLMEngine:
    global _local_llm_engine
    if _local_llm_engine is None:
        _local_llm_engine = LocalLLMEngine()
    return _local_llm_engine
