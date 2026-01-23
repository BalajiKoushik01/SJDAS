from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (QGraphicsOpacityEffect, QHBoxLayout, QLabel,
                             QPushButton, QWidget)


class AIAssistantOverlay(QWidget):
    """
    Non-intrusive 'Toast' / 'Pill' widget for AI Suggestions.
    """
    action_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.SubWindow |
                            Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 8, 15, 8)

        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: #2d2d30;
                border: 1px solid #0078d4;
                border-radius: 20px;
                color: white;
            }
        """)
        self.con_layout = QHBoxLayout(self.container)

        self.icon_label = QLabel("🤖")
        self.text_label = QLabel("AI Assistant Ready")
        self.text_label.setStyleSheet("font-weight: bold; margin-right: 10px;")

        self.btn_action = QPushButton("Do it")
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                border-radius: 12px;
                padding: 4px 12px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #106ebe; }
        """)
        self.btn_action.clicked.connect(self.on_action)
        self.btn_action.hide()

        self.con_layout.addWidget(self.icon_label)
        self.con_layout.addWidget(self.text_label)
        self.con_layout.addWidget(self.btn_action)

        self.layout.addWidget(self.container)

        # Animation
        self.fade = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.fade)
        self.timer = QTimer()
        self.timer.timeout.connect(self.hide_toast)

        self.current_action = None

    def show_suggestion(self, text, action_id=None):
        self.text_label.setText(text)
        self.current_action = action_id

        if action_id:
            self.btn_action.show()
            self.btn_action.setText(
                "Apply" if action_id != "segment" else "Auto-Segment")
        else:
            self.btn_action.hide()

        self.show()
        self.raise_()
        self.fade.setOpacity(1.0)
        self.timer.start(5000)  # Hide after 5s

    def on_action(self):
        if self.current_action:
            self.action_clicked.emit(self.current_action)
            self.hide()

    def hide_toast(self):
        self.hide()
