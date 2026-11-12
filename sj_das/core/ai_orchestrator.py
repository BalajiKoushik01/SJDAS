"""Command routing facade. No model inference or machine action on construction."""
from typing import Any, Dict


class AIOrchestrator:
    def route(self, command: str) -> Dict[str, Any]:
        if not isinstance(command, str) or not command.strip():
            return {
                "type": "error",
                "response": "Please describe the design task.",
                "action": None,
            }
        from sj_das.ai.agi_assistant import get_agi
        return get_agi().process_command(command)
