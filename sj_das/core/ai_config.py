"""
AI Configuration Module for SJ-DAS.

Handles secure storage and retrieval of API keys and AI provider settings.
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("SJ_DAS.AIConfig")


@dataclass
class AIProviderConfig:
    """Configuration for an AI provider."""
    name: str
    api_key: str = ""
    endpoint: str = ""
    enabled: bool = True
    priority: int = 0  # Lower number = higher priority


class AIConfigManager:
    """
    Manages AI provider configurations and API keys.

    Features:
        - Secure API key storage
        - Provider priority management
        - Configuration persistence
        - Fallback configuration
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize AI configuration manager.

        Args:
            config_dir: Directory for config files (defaults to user's app data)
        """
        if config_dir is None:
            # Use application data directory
            config_dir = Path.home() / ".sj_das" / "config"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.config_dir / "ai_providers.json"
        self.providers: Dict[str, AIProviderConfig] = {}

        # Load existing configuration
        self._load_config()

        # Initialize default providers if not exists
        self._init_default_providers()

    def _init_default_providers(self):
        """Initialize default provider configurations."""
        defaults = {
            "minimax": AIProviderConfig(
                name="MiniMax M2.1",
                endpoint="https://api.minimax.io/v1/text/chatcompletion_v2",
                enabled=False,
                priority=1
            ),
            "gemini": AIProviderConfig(
                name="Google Gemini",
                endpoint="",
                enabled=False,
                priority=2
            ),
            "huggingface": AIProviderConfig(
                name="HuggingFace",
                endpoint="https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
                enabled=False,
                priority=3
            ),
            "pollinations": AIProviderConfig(
                name="Pollinations.ai",
                endpoint="https://pollinations.ai/p/",
                enabled=True,  # Always enabled as fallback
                priority=99
            )
        }

        # Add defaults if they don't exist
        for key, config in defaults.items():
            if key not in self.providers:
                self.providers[key] = config

        # Save updated config
        self._save_config()

    def set_api_key(self, provider: str, api_key: str) -> bool:
        """
        Set API key for a provider.

        Args:
            provider: Provider identifier (e.g., 'minimax', 'gemini')
            api_key: API key to set

        Returns:
            True if successful
        """
        try:
            if provider not in self.providers:
                logger.error(f"Unknown provider: {provider}")
                return False

            self.providers[provider].api_key = api_key
            self.providers[provider].enabled = bool(api_key)

            self._save_config()
            logger.info(f"API key set for {provider}")
            return True

        except Exception as e:
            logger.error(f"Failed to set API key for {provider}: {e}")
            return False

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider.

        Args:
            provider: Provider identifier

        Returns:
            API key or None if not set
        """
        if provider in self.providers:
            return self.providers[provider].api_key or None
        return None

    def get_provider_config(self, provider: str) -> Optional[AIProviderConfig]:
        """
        Get full configuration for a provider.

        Args:
            provider: Provider identifier

        Returns:
            Provider configuration or None
        """
        return self.providers.get(provider)

    def get_enabled_providers(self) -> list[str]:
        """
        Get list of enabled providers sorted by priority.

        Returns:
            List of provider identifiers
        """
        enabled = [
            (key, config) for key, config in self.providers.items()
            if config.enabled
        ]

        # Sort by priority (lower number = higher priority)
        enabled.sort(key=lambda x: x[1].priority)

        return [key for key, _ in enabled]

    def set_provider_priority(self, provider: str, priority: int) -> bool:
        """
        Set priority for a provider.

        Args:
            provider: Provider identifier
            priority: Priority value (lower = higher priority)

        Returns:
            True if successful
        """
        if provider in self.providers:
            self.providers[provider].priority = priority
            self._save_config()
            return True
        return False

    def enable_provider(self, provider: str, enabled: bool = True) -> bool:
        """
        Enable or disable a provider.

        Args:
            provider: Provider identifier
            enabled: Whether to enable the provider

        Returns:
            True if successful
        """
        if provider in self.providers:
            self.providers[provider].enabled = enabled
            self._save_config()
            return True
        return False

    def _load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)

                # Convert dict to AIProviderConfig objects
                for key, value in data.items():
                    self.providers[key] = AIProviderConfig(**value)

                logger.info(f"Loaded AI configuration from {self.config_file}")
            else:
                logger.info(
                    "No existing AI configuration found, using defaults")

        except Exception as e:
            logger.error(f"Failed to load AI configuration: {e}")

    def _save_config(self):
        """Save configuration to file."""
        try:
            # Convert AIProviderConfig objects to dicts
            data = {
                key: asdict(config) for key, config in self.providers.items()
            }

            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved AI configuration to {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to save AI configuration: {e}")


# Global instance
_ai_config_manager = None


def get_ai_config() -> AIConfigManager:
    """Get the global AI configuration manager instance."""
    global _ai_config_manager
    if _ai_config_manager is None:
        _ai_config_manager = AIConfigManager()
    return _ai_config_manager
