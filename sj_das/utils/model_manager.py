"""
AI Model Manager for SJ-DAS
Implements lazy loading and lifecycle management for AI models
"""
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from sj_das.utils.enhanced_logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """
    Manages AI model lifecycle with lazy loading.

    Features:
    - On-demand model loading
    - Automatic unloading of unused models
    - Model lifecycle tracking
    - Memory-efficient loading
    """

    def __init__(self, timeout: int = 300, max_models: int = 3):
        """
        Initialize model manager.

        Args:
            timeout: Seconds before unloading unused model (default 5 min)
            max_models: Maximum models to keep loaded
        """
        self.timeout = timeout
        self.max_models = max_models

        self.loaded_models: Dict[str, Any] = {}
        self.last_used: Dict[str, float] = {}
        self.model_loaders: Dict[str, Callable] = {}
        self.loading_lock = threading.Lock()

        logger.info(
            f"ModelManager initialized (timeout={timeout}s, max_models={max_models})")

    def register_loader(self, model_name: str, loader_func: Callable):
        """
        Register a loader function for a model.

        Args:
            model_name: Name of the model
            loader_func: Function that loads and returns the model
        """
        self.model_loaders[model_name] = loader_func
        logger.debug(f"Registered loader for {model_name}")

    def get_model(self, model_name: str) -> Any:
        """
        Get model, loading if necessary.

        Args:
            model_name: Name of the model

        Returns:
            Loaded model instance
        """
        with self.loading_lock:
            # Check if already loaded
            if model_name in self.loaded_models:
                self.last_used[model_name] = time.time()
                logger.debug(f"Using cached model: {model_name}")
                return self.loaded_models[model_name]

            # Load model
            if model_name not in self.model_loaders:
                raise ValueError(f"No loader registered for {model_name}")

            logger.info(f"Loading model: {model_name}")
            start_time = time.time()

            # Check if we need to unload old models
            if len(self.loaded_models) >= self.max_models:
                self._unload_oldest()

            # Load the model
            loader = self.model_loaders[model_name]
            model = loader()

            # Cache it
            self.loaded_models[model_name] = model
            self.last_used[model_name] = time.time()

            elapsed = time.time() - start_time
            logger.info(f"Model {model_name} loaded in {elapsed:.2f}s")

            return model

    def _unload_oldest(self):
        """Unload the least recently used model."""
        if not self.last_used:
            return

        # Find oldest model
        oldest_name = min(self.last_used, key=self.last_used.get)
        self.unload_model(oldest_name)

    def unload_model(self, model_name: str):
        """
        Unload a specific model.

        Args:
            model_name: Name of model to unload
        """
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            del self.last_used[model_name]
            logger.info(f"Unloaded model: {model_name}")

    def cleanup_unused(self):
        """Unload models not used recently."""
        now = time.time()
        to_unload = []

        for name, last_use in self.last_used.items():
            if now - last_use > self.timeout:
                to_unload.append(name)

        for name in to_unload:
            self.unload_model(name)

        if to_unload:
            logger.info(f"Cleaned up {len(to_unload)} unused models")

    def unload_all(self):
        """Unload all models."""
        count = len(self.loaded_models)
        self.loaded_models.clear()
        self.last_used.clear()
        logger.info(f"Unloaded all {count} models")

    def get_stats(self) -> dict:
        """
        Get model manager statistics.

        Returns:
            Dictionary with metrics
        """
        return {
            'loaded_models': len(self.loaded_models),
            'registered_loaders': len(self.model_loaders),
            'max_models': self.max_models,
            'timeout': self.timeout,
            'model_names': list(self.loaded_models.keys())
        }

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"ModelManager(loaded={stats['loaded_models']}/{stats['max_models']})"


# Global model manager instance
_global_model_manager: Optional[ModelManager] = None


def get_model_manager(timeout: int = 300, max_models: int = 3) -> ModelManager:
    """
    Get global model manager instance.

    Args:
        timeout: Timeout in seconds (only used on first call)
        max_models: Max models to keep loaded (only used on first call)

    Returns:
        Global ModelManager instance
    """
    global _global_model_manager
    if _global_model_manager is None:
        _global_model_manager = ModelManager(timeout, max_models)
    return _global_model_manager


# Example loader functions for common models
def create_sam_loader():
    """Create loader for SAM model."""
    def load_sam():
        from sj_das.core import SAMEngine
        return SAMEngine()
    return load_sam


def create_clip_loader():
    """Create loader for CLIP model."""
    def load_clip():
        from sj_das.core import CLIPEngine
        return CLIPEngine()
    return load_clip


def create_controlnet_loader():
    """Create loader for ControlNet model."""
    def load_controlnet():
        from sj_das.core import ControlNetEngine
        return ControlNetEngine()
    return load_controlnet


def register_default_loaders(manager: ModelManager):
    """
    Register default model loaders.

    Args:
        manager: ModelManager instance
    """
    manager.register_loader('sam', create_sam_loader())
    manager.register_loader('clip', create_clip_loader())
    manager.register_loader('controlnet', create_controlnet_loader())

    logger.info("Registered default model loaders")
