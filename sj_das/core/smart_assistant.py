from PyQt6.QtCore import QObject, pyqtSignal


class SmartAssistant(QObject):
    """
    Agentic Observer that monitors user context and suggests actions.
    Tailored for Silk Saree Designers.
    """
    suggestion_ready = pyqtSignal(str, str)  # title, action_id

    def __init__(self, designer_view):
        super().__init__()
        self.view = designer_view
        self.editor = designer_view.editor

        # Connect Signals
        self.editor.mask_updated.connect(self.check_floats_background)
        self.view.tool_group.buttonClicked.connect(self.on_tool_changed)

    def check_floats_background(self):
        # Rule: If mask updated, check for floats in background (non-blocking)
        # For prototype, we just emit a tip occasionally to avoid lag
        pass

    def on_image_loaded(self, width, height):
        self.suggestion_ready.emit("Design Loaded", "segment")

    def on_tool_changed(self, btn):
        # Context-Aware Tips
        self.view.tool_group.id(btn)

        if "Brush" in btn.text() and self.view.editor.brush_size > 50:
            self.suggestion_ready.emit("Large Brush Detected", "use_fill")

    def execute_action(self, action_id):
        if action_id == "segment":
            self.view.run_segmentation()
        elif action_id == "use_fill":
            self.view.btn_fill.click()
        elif action_id == "fix_floats":
            self.view.check_floats()
