from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QScrollArea, QTextEdit, QVBoxLayout,
                             QWidget)
from qfluentwidgets import (CaptionLabel, LineEdit, PushButton,
                            StrongBodyLabel, TextEdit)

from sj_das.ai.agi_assistant import get_agi


class AIChatPanel(QWidget):
    """
    AGI Chat Interface.
    Allows user to converse with the Expert System.
    """
    action_requested = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.agi = get_agi()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        header = StrongBodyLabel("🧠 Design Expert")
        layout.addWidget(header)

        # Chat History
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                color: #E2E8F0;
            }
        """)
        layout.addWidget(self.chat_area)

        # Input Area
        input_layout = QHBoxLayout()

        self.input_field = LineEdit()
        self.input_field.setPlaceholderText(
            "Ask me anything (e.g., 'Generate blue pattern')...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        send_btn = PushButton("Send")
        send_btn.setFixedSize(60, 32)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

        # Initial greeting
        self.add_message(
            "System",
            "Hello! I am your AI Design Assistant. capabilities: Pattern Generation, Analysis, Recommendations.")

    def send_message(self):
        msg = self.input_field.text().strip()
        if not msg:
            return

        # User Message
        self.add_message("You", msg)
        self.input_field.clear()

        # Process with AGI
        response = self.agi.process_command(msg)

        # AI Response
        text = response.get("response", "I didn't understand that.")
        self.add_message("AI", text)

        # Handle Actions (Simple implementation)
        action = response.get("action")
        if action:
            self.handle_action(action, response.get("data", {}))

    def add_message(self, sender, text):
        color = "#6366F1" if sender == "AI" else "#94A3B8"
        if sender == "System":
            color = "#10B981"

        html = f'<div style="margin-bottom: 5px;"><b style="color:{color};">{sender}:</b> {text}</div>'
        self.chat_area.append(html)

    def handle_action(self, action, data):
        """Execute UI actions triggered by AI."""
        self.add_message("System", f"<i>Executing action: {action}...</i>")
        self.action_requested.emit(action, data)
