
import json
import logging
import os
from typing import Dict

logger = logging.getLogger("SJ_DAS.Core.Features")


class FeatureFlagManager:
    """
    Manages application feature toggles.
    Allows safe rollout of new features (Dark Launching).
    """
    _instance = None

    DEFAULT_FLAGS = {
        "AI_VOICE_COMMANDS": False,
        "EXPERIMENTAL_RENDERER": False,
        "CLOUD_SYNC": False,
        "STRICT_MODE": True
    }

    def __init__(self):
        self._flags: Dict[str, bool] = self.DEFAULT_FLAGS.copy()
        self._config_path = os.path.join(
            os.path.expanduser("~"),
            ".gemini",
            "sj_das_features.json")
        self.load_config()

    @classmethod
    def instance(cls) -> 'FeatureFlagManager':
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def is_enabled(self, feature_key: str) -> bool:
        """Check if a feature is enabled."""
        return self._flags.get(feature_key, False)

    def enable(self, feature_key: str):
        """Enable a feature."""
        self._flags[feature_key] = True
        self.save_config()
        logger.info(f"Feature Enabled: {feature_key}")

    def disable(self, feature_key: str):
        """Disable a feature."""
        self._flags[feature_key] = False
        self.save_config()
        logger.info(f"Feature Disabled: {feature_key}")

    def load_config(self):
        """Load flags from disk."""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    saved_flags = json.load(f)
                    self._flags.update(saved_flags)
            except Exception as e:
                logger.error(f"Failed to load feature flags: {e}")

    def save_config(self):
        """Save flags to disk."""
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, 'w') as f:
                json.dump(self._flags, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save feature flags: {e}")
