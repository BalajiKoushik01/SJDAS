
from typing import Any, Dict, List

from PyQt6.QtCore import QObject, pyqtSignal


class CortexMemory(QObject):
    """
    Short-term working memory for the AI Agent.
    Stores context about the current design, user intent, and conversation history.
    """
    state_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._context: Dict[str, Any] = {
            "current_action": None,
            "last_user_prompt": "",
            "active_layer": "background",
            "style_preferences": [],
            "conversation_history": []
        }

    def update(self, key: str, value: Any):
        self._context[key] = value
        self.state_changed.emit()

    def get(self, key: str, default=None):
        return self._context.get(key, default)

    def add_message(self, role: str, content: str):
        self._context["conversation_history"].append(
            {"role": role, "content": content})
        # Keep history short (last 10 turns)
        if len(self._context["conversation_history"]) > 10:
            self._context["conversation_history"].pop(0)

    def clear(self):
        self._context["conversation_history"] = []
