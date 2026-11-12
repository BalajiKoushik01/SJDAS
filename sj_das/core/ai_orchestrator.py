"""Intent routing facade for the SJ-DAS application.

This module returns a description of an intended action. It does not execute
hardware commands or automatically invoke a remote AI provider.
"""
from typing import Any, Dict


class AIOrchestrator:
    """Small, deterministic routing interface used by UI integrations."""

    def route(self, command: str) -> Dict[str, Any]:
        if not isinstance(command, str) or not command.strip():
            return {"type": "error", "action": None, "response": "Enter a command."}
        text = command.strip().lower()
        if any(term in text for term in ("analyze", "analyse", "inspect", "check")):
            action = "run_analysis"
        elif any(term in text for term in ("generate", "create", "draw")):
            action = "generate_pattern"
        elif any(term in text for term in ("export", "loom")):
            action = "review_export"
        else:
            action = None
        return {
            "type": "action" if action else "chat",
            "action": action,
            "response": ("Action requires user confirmation." if action else "No matching design action."),
            "data": {"command": command.strip()},
        }
