"""
Integration test for MiniMax M2.1 in SJ-DAS application.
Tests the full integration including UI, AGI assistant, and model manager.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestMiniMaxIntegration:
    """Test MiniMax integration with application components."""

    def test_imports(self):
        """Test that all MiniMax modules can be imported."""
        from sj_das.ai.prompt_templates import PromptTemplates
        from sj_das.core.ai_config import AIConfigManager, get_ai_config
        from sj_das.core.engines.llm.minimax_engine import (MiniMaxEngine,
                                                            get_minimax_engine)

        assert MiniMaxEngine is not None
        assert get_minimax_engine is not None
        assert AIConfigManager is not None
        assert get_ai_config is not None
        assert PromptTemplates is not None

    def test_ai_config_initialization(self):
        """Test AI configuration manager initialization."""
        from sj_das.core.ai_config import get_ai_config

        config = get_ai_config()
        assert config is not None
        assert config.config_dir.exists()

        # Check default providers
        providers = config.providers
        assert 'minimax' in providers
        assert 'gemini' in providers
        assert 'huggingface' in providers
        assert 'pollinations' in providers

    def test_minimax_engine_initialization(self):
        """Test MiniMax engine initialization."""
        from sj_das.core.engines.llm.minimax_engine import get_minimax_engine

        engine = get_minimax_engine()
        assert engine is not None
        assert hasattr(engine, 'configure')
        assert hasattr(engine, 'analyze_design')
        assert hasattr(engine, 'get_color_recommendations')
        assert hasattr(engine, 'get_pattern_suggestions')

    def test_model_manager_integration(self):
        """Test MiniMax integration with ModelManager."""
        from sj_das.ai.model_manager import ModelManager

        manager = ModelManager()
        assert manager is not None
        assert hasattr(manager, 'load_minimax')
        assert hasattr(manager, 'get_minimax')
        assert hasattr(manager, 'analyze_design_with_llm')
        assert hasattr(manager, 'get_design_suggestions')

    def test_agi_assistant_integration(self):
        """Test MiniMax integration with AGI Assistant."""
        from sj_das.ai.agi_assistant import get_agi

        agi = get_agi()
        assert agi is not None
        assert hasattr(agi, 'process_command')
        assert hasattr(agi, '_handle_design_analysis')

        # Test that AGI can process commands
        response = agi.process_command("test")
        assert isinstance(response, dict)
        assert 'type' in response
        assert 'response' in response

    def test_prompt_templates(self):
        """Test prompt template functionality."""
        from sj_das.ai.prompt_templates import PromptTemplates

        # Test design analysis template
        prompt = PromptTemplates.format_design_analysis(
            "Test design",
            "Test analysis"
        )
        assert "Test design" in prompt
        assert "Test analysis" in prompt

        # Test color recommendations template
        prompt = PromptTemplates.format_color_recommendations("Test context")
        assert "Test context" in prompt

        # Test pattern suggestions template
        prompt = PromptTemplates.format_pattern_suggestions(
            "Current design",
            "Preferences"
        )
        assert "Current design" in prompt
        assert "Preferences" in prompt

    def test_ui_components_import(self):
        """Test that UI components with MiniMax can be imported."""
        try:
            from sj_das.ui.components.ai_chat_panel import AIChatPanel
            from sj_das.ui.dialogs.ai_settings_dialog import AISettingsDialog

            assert AIChatPanel is not None
            assert AISettingsDialog is not None
        except ImportError as e:
            pytest.skip(f"UI components not available: {e}")

    def test_configuration_persistence(self):
        """Test that configuration can be saved and loaded."""
        from sj_das.core.ai_config import get_ai_config

        config = get_ai_config()

        # Set a test API key
        test_key = "test_key_12345"
        config.set_api_key('minimax', test_key)

        # Verify it was saved
        retrieved_key = config.get_api_key('minimax')
        assert retrieved_key == test_key

        # Clean up
        config.set_api_key('minimax', '')

    def test_provider_priority(self):
        """Test provider priority management."""
        from sj_das.core.ai_config import get_ai_config

        config = get_ai_config()

        # Set priority
        config.set_provider_priority('minimax', 1)

        # Get enabled providers (should be sorted by priority)
        providers = config.get_enabled_providers()
        assert isinstance(providers, list)

    def test_minimax_unconfigured_behavior(self):
        """Test that MiniMax handles unconfigured state gracefully."""
        from sj_das.core.engines.llm.minimax_engine import MiniMaxEngine

        engine = MiniMaxEngine()

        # Should not be configured without API key
        assert not engine.is_configured()

        # Should return None for operations when unconfigured
        result = engine.analyze_design("Test design")
        assert result is None

        result = engine.get_color_recommendations("Test context")
        assert result is None


class TestMiniMaxFeatures:
    """Test specific MiniMax features."""

    def test_textile_system_prompt(self):
        """Test that textile-specific system prompt is set."""
        from sj_das.core.engines.llm.minimax_engine import MiniMaxEngine

        engine = MiniMaxEngine()
        prompt = engine.system_prompt

        # Check for textile-specific keywords
        assert "textile" in prompt.lower()
        assert "saree" in prompt.lower()
        assert "jacquard" in prompt.lower() or "weave" in prompt.lower()

    def test_conversation_management(self):
        """Test conversation history management."""
        from sj_das.core.engines.llm.minimax_engine import MiniMaxEngine

        engine = MiniMaxEngine()

        # Initially empty
        assert len(engine.conversation_history) == 0

        # Add to history (simulated)
        engine.conversation_history.append({"role": "user", "content": "test"})
        assert len(engine.conversation_history) == 1

        # Reset
        engine.reset_conversation()
        assert len(engine.conversation_history) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
