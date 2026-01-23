
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import PillToolButton, SearchLineEdit


class OmniBar(QFrame):
    """
    Floating Command Center for The Cortex.
    """
    command_entered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 60)
        self.setStyleSheet("""
            OmniBar {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 30px;
            }
        """)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10)

        # Brain Icon
        self.btn_brain = PillToolButton(FIF.IOT, self)
        self.btn_brain.setChecked(True)
        self.layout.addWidget(self.btn_brain)

        # Input
        self.search_input = SearchLineEdit(self)
        self.search_input.setPlaceholderText(
            "Ask Cortex (e.g. 'Make this floral', 'Search Met for Silk')")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self._on_enter)
        self.layout.addWidget(self.search_input)

        # Effect
        self._setup_shadow()

        # Check Brain Status
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, self._check_brain_status)

    def _check_brain_status(self):
        import requests
        try:
            requests.get("http://localhost:11434", timeout=0.2)
            self.btn_brain.setIcon(FIF.IOT)  # Keep default
            self.btn_brain.setToolTip(
                "Cortex: SUPERCHARGED (Local LLM Active)")
            # Maybe change color to green?
            # self.btn_brain.setStyleSheet("...")
        except BaseException:
            self.btn_brain.setIcon(FIF.QUESTION)
            self.btn_brain.setToolTip(
                "Cortex: Basic Mode (Install Ollama for Supercharge)")

    def _setup_shadow(self):
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(Qt.GlobalColor.gray)
        self.setGraphicsEffect(shadow)

    def _on_enter(self):
        text = self.search_input.text().strip()
        if text:
            self.command_entered.emit(text)
            self.search_input.clear()

    def set_status(self, text: str):
        self.search_input.setPlaceholderText(text)
