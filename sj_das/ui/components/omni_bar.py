
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
        self.is_minimized = False
        self.is_manually_moved = False
        self.old_pos = None

        self.setStyleSheet("""
            OmniBar {
                background-color: rgba(30, 30, 30, 0.90);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 30px;
            }
            QLabel {
                color: #FFFFFF !important;
                background: transparent;
                border: none;
                font-size: 14px;
                font-family: "Inter", "Segoe UI", sans-serif;
            }
            QLineEdit {
                color: #FFFFFF !important;
                background: transparent;
                border: none;
                font-size: 14px;
                font-family: "Inter", "Segoe UI", sans-serif;
                selection-background-color: #6366F1;
                selection-color: white;
            }
            QToolButton {
                background: transparent;
                border: none;
                color: #FFFFFF !important;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
        """)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10) # More grab space
        self.setCursor(Qt.CursorShape.SizeAllCursor) # Indicate draggable

        # Brain Icon (Draggable Handle essentially)
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

        # Collapse Button
        self.btn_collapse = PillToolButton(FIF.CHEVRON_RIGHT, self)
        self.btn_collapse.setToolTip("Minimize")
        self.btn_collapse.clicked.connect(self.toggle_minimize)
        self.layout.addWidget(self.btn_collapse)

        # Effect
        self._setup_shadow()

        # Check Brain Status
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, self._check_brain_status)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            self.is_manually_moved = True
            event.accept()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def toggle_minimize(self):
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect

        self.is_minimized = not self.is_minimized
        
        start_rect = self.geometry()
        
        if self.is_minimized:
            # Collapse
            self.search_input.hide()
            self.btn_collapse.setIcon(FIF.CHEVRON_LEFT)
            end_width = 120 # Icon + Btn
        else:
            # Expand
            self.search_input.show()
            self.btn_collapse.setIcon(FIF.CHEVRON_RIGHT)
            end_width = 600

        # Animate Width
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(QRect(start_rect.x(), start_rect.y(), end_width, 60))
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

    def _check_brain_status(self):
        import requests
        try:
            requests.get("http://localhost:11434", timeout=0.2)
            self.btn_brain.setIcon(FIF.IOT)  # Keep default
            self.btn_brain.setToolTip(
                "Cortex: SUPERCHARGED (Local LLM Active)")
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
