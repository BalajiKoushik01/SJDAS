
import logging

from PyQt6.QtCore import QObject, pyqtSignal

from sj_das.core.cortex.lobes import CreativeLobe, LogicLobe, VisionLobe
from sj_das.core.cortex.memory import CortexMemory

logger = logging.getLogger("SJ_DAS.Cortex.Brain")


class CortexOrchestrator(QObject):
    """
    The Brain (Mini-AGI).
    Orchestrates the collaboration between Logic, Vision, and Creative lobes.
    """
    _instance = None

    # Brain Output Signals
    action_required = pyqtSignal(str, dict)  # action_name, params
    thought_updated = pyqtSignal(str)  # "Thinking..."
    content_generated = pyqtSignal(object)  # QImage, Text, etc.

    def __init__(self):
        super().__init__()
        self.memory = CortexMemory()
        self.action_queue = []
        self.is_waiting_for_async = False

        # Initialize Lobes
        self.logic = LogicLobe()
        self.vision = VisionLobe()
        self.creative = CreativeLobe()

        # Wiring
        self.logic.intent_parsed.connect(self._receieve_plan)
        self.creative.finished.connect(self._on_async_content_ready)
        self.creative.error.connect(
            lambda e: self.thought_updated.emit(f"Error: {e}"))
        self.vision.finished.connect(self._on_async_content_ready)
        self.vision.error.connect(
            lambda e: self.thought_updated.emit(f"Vision Error: {e}"))

    @staticmethod
    def instance() -> 'CortexOrchestrator':
        if CortexOrchestrator._instance is None:
            CortexOrchestrator._instance = CortexOrchestrator()
        return CortexOrchestrator._instance

    def think(self, user_input: str):
        """
        Main Entry Point.
        User says something -> Brain processes it.
        """
        logger.info(f"Cortex received: {user_input}")
        self.memory.add_message("user", user_input)
        self.thought_updated.emit("Analyzing intent...")

        # 1. Logic Lobe parses intent
        self.logic.process_command(user_input)

    def _receieve_plan(self, plan):
        """Handle plan from LogicLobe."""
        if not plan:
            return

        if isinstance(plan, dict):
            self.action_queue = [plan]
        elif isinstance(plan, list):
            self.action_queue = plan

        self.is_waiting_for_async = False
        self._process_next_action()

    def _process_next_action(self):
        if not self.action_queue:
            self.thought_updated.emit("Ready")
            return

        if self.is_waiting_for_async:
            return

        action_item = self.action_queue.pop(0)
        action = action_item.get("action")
        params = action_item.get("params", {})

        logger.info(f"Cortex Executing: {action}")
        self.thought_updated.emit(f"Executing: {action}")
        self.memory.add_message("assistant", f"I am executing {action}.")

        # Check if async
        if action == "generate":
            self.is_waiting_for_async = True

        # Emit signal for UI/Controller to react
        self.action_required.emit(action, params)

        # If not async, proceed after short delay
        if not self.is_waiting_for_async:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1000, self._process_next_action)

    def _on_async_content_ready(self, content):
        """Async action finished, resume queue."""
        self.content_generated.emit(content)
        if self.is_waiting_for_async:
            self.is_waiting_for_async = False
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, self._process_next_action)

    def _execute_intent(self, intent: dict):
        # Legacy stub
        pass

    def get_context(self):
        return self.memory._context
