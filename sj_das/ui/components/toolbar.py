
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import ToolTipFilter, TransparentToolButton


class AcrylicToolbar(QFrame):
    """
    Vertical Floating Toolbar with Glassmorphism.
    """
    tool_triggered = pyqtSignal(str)  # tool_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(60)
        self.setStyleSheet("""
            AcrylicToolbar {
                background-color: rgba(30, 30, 30, 0.85); /* Dark Glass */
                border-right: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 0px;
            }
            QLabel {
                color: rgba(255, 255, 255, 0.5);
                font-size: 10px;
                font-weight: bold;
                margin-top: 10px;
                margin-bottom: 5px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 20, 5, 20)
        self.layout.setSpacing(8)
        self.layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Tools
        self._add_group("CREATE")
        self._add_tool("magic_wand", FIF.MAGIC_WAND, "Magic Wand (AI)")
        self._add_tool("brush", FIF.BRUSH, "Brush")
        self._add_tool("text", FIF.FONT_SIZE, "Text")

        self._add_group("EDIT")
        self._add_tool("crop", FIF.CROP, "Crop")
        self._add_tool("move", FIF.MOVE, "Move")

        self._add_group("AI")
        self._add_tool("upscale", FIF.ZOOM_IN, "Upscale 4x")
        self._add_tool("met", FIF.LIBRARY, "Met Museum")

        self.layout.addStretch()

    def _add_group(self, title):
        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl)

    def _add_tool(self, tool_id, icon, tooltip):
        btn = TransparentToolButton(icon, self)
        btn.setFixedSize(40, 40)
        btn.setIconSize(QSize(20, 20))
        btn.setToolTip(tooltip)
        btn.installEventFilter(ToolTipFilter(btn, 0))  # Fluent Tooltip

        btn.clicked.connect(lambda: self.tool_triggered.emit(tool_id))
        self.layout.addWidget(btn)
