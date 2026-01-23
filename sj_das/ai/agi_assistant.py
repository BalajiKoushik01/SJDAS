"""
AGI Assistant Module.
A unified intelligent agent that interprets natural language commands
and orchestrates the application's AI capabilities.
"""

import random
import re
from typing import Any, Dict, Optional

from sj_das.ai.adaptive_memory import get_adaptive_memory
from sj_das.core.services.ai_service import AIService
from sj_das.utils.logger import logger


class AGIAssistant:
    """
    Expert System orchestrator ("The AGI").
    Interprets intent and executes complex workflows using the global AIService.
    Implementation follows robust Engineering standards.
    """

    def __init__(self) -> None:
        self.memory = get_adaptive_memory()
        self.ai_service = AIService.instance()
        self.context: Dict[str, Any] = {}

    def process_command(self, user_input: str) -> Dict[str, Any]:
        """
        Process natural language input and return an actionable response.

        Args:
            user_input: The raw command string from the user.

        Returns:
            Dict containing 'type', 'response', 'action', and 'data'.
        """
        cmd = user_input.lower().strip()
        self.memory.log_action("user_command", cmd)

        try:
            # 1. Intent Recognition (Priority Pipeline)
            if self._is_generation_intent(cmd):
                return self._handle_generation(cmd)

            if self._is_analysis_intent(cmd):
                return self._handle_analysis(cmd)

            if self._is_advice_intent(cmd):
                return self._handle_advice(cmd)

            if self._is_system_intent(cmd):
                return self._handle_system_intent(cmd)

            # Default / Chat Fallback
            return self._handle_chat_fallback(cmd)

        except Exception as e:
            logger.error(
                f"Error processing command '{cmd}': {e}",
                exc_info=True)
            return {
                "type": "error",
                "response": "I encountered an error processing that command.",
                "action": None
            }

    # --- Intent Classifiers ---

    def _is_generation_intent(self, cmd: str) -> bool:
        return any(w in cmd for w in ['generate', 'create', 'make', 'draw']) and \
            any(k in cmd for k in ['pattern',
                'texture', 'variation', 'design'])

    def _is_analysis_intent(self, cmd: str) -> bool:
        return any(w in cmd for w in ['analyze',
                   'check', 'scan', 'look', 'evaluate'])

    def _is_advice_intent(self, cmd: str) -> bool:
        return any(w in cmd for w in ['suggest',
                   'recommend', 'advice', 'idea'])

    def _is_system_intent(self, cmd: str) -> bool:
        return any(w in cmd for w in ['status', 'batch', 'export', 'loom'])

    # --- Handlers ---

    def _handle_generation(self, cmd: str) -> Dict[str, Any]:
        """Handle generation requests with context awareness."""
        seed = random.randint(0, 10000) if "random" in cmd else None

        # Check for memory preference
        fav_weave = self.memory.get_top_preference("weaves")
        response_text = "Generating a new seamless textile pattern..."

        if fav_weave and "kanc" in fav_weave.lower():
            response_text += f"\n(Optimizing for your preferred {fav_weave} style)"

        # In a real sync, we might trigger the AI service here directly,
        # but for the UI pattern, we return an action for the View to execute.
        return {
            "type": "action",
            "response": response_text,
            "action": "generate_pattern",
            "data": {"seed": seed, "optimize_seamless": True, "prompt": cmd}
        }

    def _handle_analysis(self, cmd: str) -> Dict[str, Any]:
        """Handle analysis requests triggering LLM analysis."""
        design_desc = cmd.replace(
            'analyze', '').replace(
            'design', '').strip() or "current design"

        # Trigger async analysis via Service (if View doesn't catch the action)
        # But properly we return an action instruction.
        return {
            "type": "action",
            "response": "Analyzing design structure and visual semantics...",
            "action": "run_analysis",  # The View listens for this
            "data": {"description": design_desc}
        }

    def _handle_advice(self, cmd: str) -> Dict[str, Any]:
        """Provide advice based on memory or LLM knowledge."""
        fav_color = self.memory.get_top_preference("colors") or "Blue"

        if "color" in cmd:
            rec = f"Based on your history, you use {fav_color} frequently."
            rec += " For high contrast, try a complementary Split-Complementary palette."
            return {
                "type": "chat",
                "response": rec,
                "action": "show_colors"
            }

        return {
            "type": "chat",
            "response": "I recommend checking the 'Smart Expert' panel for detailed quality checks.",
            "action": "open_expert"
        }

    def _handle_system_intent(self, cmd: str) -> Dict[str, Any]:
        """Handle system/batch operations."""
        if 'batch' in cmd or 'export' in cmd:
            return {
                "type": "action",
                "response": "Initiating batch Loom Export process...",
                "action": "batch_loom_export",
                "data": {}
            }
        if 'loom' in cmd:
            return {
                "type": "action",
                "response": "Running Manufacturing Integrity Check...",
                "action": "check_loom_readiness",
                "data": {}
            }

        # Fallback status
        summary = self.memory.get_context_summary()
        return {
            "type": "chat",
            "response": f"System Status: Online. Learning profile: {summary}",
            "action": None
        }

    def _handle_chat_fallback(self, cmd: str) -> Dict[str, Any]:
        """Fallback for unclassified inputs."""
        return {
            "type": "chat",
            "response": "I can help generate patterns, analyze designs, or verify loom readiness. Try 'Analyze this design'.",
            "action": None
        }


# Global Singleton
_agi: Optional[AGIAssistant] = None


def get_agi() -> AGIAssistant:
    global _agi
    if _agi is None:
        _agi = AGIAssistant()
    return _agi
