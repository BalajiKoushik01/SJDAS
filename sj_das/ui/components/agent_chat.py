from PyQt6.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPalette
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QScrollArea, QTextEdit, QVBoxLayout,
                             QWidget)


class AgentWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, engine, text):
        super().__init__()
        self.engine = engine
        self.text = text

    def run(self):
        res = self.engine.chat(self.text)
        self.finished.emit(res)


class ChatBubble(QWidget):
    def __init__(self, text, is_user=False):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {'#2563EB' if is_user else '#374151'};
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
            }}
        """)

        if is_user:
            self.layout.addStretch()
            self.layout.addWidget(lbl)
        else:
            self.layout.addWidget(lbl)
            self.layout.addStretch()


class AgentChatWidget(QWidget):
    action_requested = pyqtSignal(str, dict)  # action_name, params

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = None
        self.setFixedWidth(350)
        self.setStyleSheet(
            "background-color: rgba(30, 30, 30, 240); border-left: 1px solid #444;")

        self.init_ui()

    def init_ui(self):
        vlay = QVBoxLayout(self)

        # Header
        lbl_head = QLabel("✨ SJ-DAS Copilot")
        lbl_head.setStyleSheet(
            "color: white; font-weight: bold; font-size: 16px; padding: 10px;")
        lbl_head.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vlay.addWidget(lbl_head)

        # Chat Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.chat_container = QWidget()
        self.chat_lay = QVBoxLayout(self.chat_container)
        self.chat_lay.addStretch()
        self.scroll.setWidget(self.chat_container)
        vlay.addWidget(self.scroll)

        # Input Area
        hlay = QHBoxLayout()
        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText("Ask me anything...")
        self.txt_input.setStyleSheet("""
            QLineEdit {
                background-color: #4B5563;
                color: white;
                border-radius: 15px;
                padding: 8px 15px;
                border: 1px solid #6B7280;
            }
        """)
        self.txt_input.returnPressed.connect(self.send_message)

        btn_send = QPushButton("➤")
        btn_send.setFixedSize(35, 35)
        btn_send.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border-radius: 17px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1D4ED8; }
        """)
        btn_send.clicked.connect(self.send_message)

        hlay.addWidget(self.txt_input)
        hlay.addWidget(btn_send)
        vlay.addLayout(hlay)

        # Async Init
        self.add_message("Initializing Neural Engine...", False)

    def set_engine(self):
        if self.engine is None:
            try:
                from sj_das.core.agent_engine import AgentEngine
                self.engine = AgentEngine()
                self.add_message(
                    "Hello! I am ready. How can I help you design today?", False)
            except Exception:
                self.add_message("Failed to load Agent Engine.", False)

    def add_message(self, text, is_user):
        bubble = ChatBubble(text, is_user)
        self.chat_lay.addWidget(bubble)
        # Scroll to bottom
        QThread.msleep(10)  # UI update tick
        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum())

    def send_message(self):
        text = self.txt_input.text().strip()
        if not text:
            return

        if self.engine is None:
            self.set_engine()

        self.add_message(text, True)
        self.txt_input.clear()

        # Disable input
        self.txt_input.setDisabled(True)

        # Worker
        self.worker = AgentWorker(self.engine, text)
        self.worker.finished.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, res):
        self.txt_input.setDisabled(False)
        self.txt_input.setFocus()

        text = res.get('text', '')
        action = res.get('action')

        if text:
            # Clean text if it contains JSON block (simple heuristic)
            if "{" in text and "}" in text:
                import re
                text = re.sub(r'\{.*\}', '', text, flags=re.DOTALL).strip()
                if not text:
                    text = "Executing command..."

            self.add_message(text, False)

        if action:
            act_name = action.get('action')
            params = action.get('params', {})
            self.action_requested.emit(act_name, params)
            self.add_message(f"🛠️ Tool Used: {act_name}", False)
