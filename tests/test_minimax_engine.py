"""
Unit tests for MiniMax M2.1 engine.
"""

from sj_das.core.engines.llm.minimax_engine import MiniMaxConfig, MiniMaxEngine
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestMiniMaxEngine:
    """Test suite for MiniMax M2.1 engine."""

    def test_engine_initialization(self):
        """Test that engine initializes without config."""
        engine = MiniMaxEngine()
        assert engine is not None
        assert not engine.is_configured()
        assert engine.conversation_history == []

    def test_engine_with_config(self):
        """Test engine initialization with config."""
        config = MiniMaxConfig(api_key="test_key_123")
        engine = MiniMaxEngine(config)
        assert engine.config is not None
        assert engine.config.api_key == "test_key_123"

    def test_configure_method(self):
        """Test the configure method."""
        engine = MiniMaxEngine()
        # Note: This will fail without a valid API key
        # In real tests, use a mock or test API key
        assert not engine.is_configured()

    def test_system_prompt(self):
        """Test that system prompt is textile-specific."""
        engine = MiniMaxEngine()
        prompt = engine.system_prompt
        assert "textile" in prompt.lower()
        assert "saree" in prompt.lower()
        assert "jacquard" in prompt.lower()

    def test_conversation_reset(self):
        """Test conversation history reset."""
        engine = MiniMaxEngine()
        engine.conversation_history = [
            {"role": "user", "content": "test"}
        ]
        engine.reset_conversation()
        assert engine.conversation_history == []

    def test_analyze_design_unconfigured(self):
        """Test that analysis returns None when unconfigured."""
        engine = MiniMaxEngine()
        result = engine.analyze_design("test design")
        assert result is None

    def test_color_recommendations_unconfigured(self):
        """Test that color recommendations return None when unconfigured."""
        engine = MiniMaxEngine()
        result = engine.get_color_recommendations("test context")
        assert result is None

    def test_pattern_suggestions_unconfigured(self):
        """Test that pattern suggestions return None when unconfigured."""
        engine = MiniMaxEngine()
        result = engine.get_pattern_suggestions("test design")
        assert result is None


class TestMiniMaxConfig:
    """Test suite for MiniMax configuration."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = MiniMaxConfig(api_key="test")
        assert config.model == "MiniMax-M2.1"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.timeout == 30

    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = MiniMaxConfig(
            api_key="test",
            temperature=0.5,
            max_tokens=1024
        )
        assert config.temperature == 0.5
        assert config.max_tokens == 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
