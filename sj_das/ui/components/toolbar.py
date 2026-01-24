
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
        
        # Dynamic Glass Style via ThemeManager
        from sj_das.ui.theme_manager import ThemeManager
        tm = ThemeManager()
        c = tm.get_all_colors()
        
        self.setStyleSheet(f"""
            AcrylicToolbar {{
                background-color: {c['bg_secondary']}; /* Glass Base */
                border-right: 1px solid {c['border_subtle']};
                border-radius: 0px;
            }}
            QLabel {{
                color: {c['text_secondary']};
                font-size: 10px;
                font-weight: bold;
                margin-top: 10px;
                margin-bottom: 5px;
            }}
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 20, 5, 20)
        self.layout.setSpacing(8)
        self.layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Tools
        self._add_group("MAIN")
        self._add_tool("move", FIF.MOVE, "Move / Pan (H)") # Pan tool
        self._add_tool("picker", FIF.PALETTE, "Eyedropper (I)") # Picker

        self._add_group("DRAW")
        self._add_tool("brush", FIF.BRUSH, "Brush (B)")
        self._add_tool("eraser", FIF.DELETE, "Eraser (E)") 
        self._add_tool("fill", FIF.BACKGROUND_FILL, "Fill Bucket (G)")
        self._add_tool("clone", FIF.COPY, "Clone Stamp (S)")
        self._add_tool("smudge", FIF.EDIT, "Smudge Tool")

        self._add_group("SHAPE")
        self._add_tool("rect", FIF.CHECKBOX, "Rectangle (R)")
        self._add_tool("ellipse", FIF.SYNC, "Ellipse (O)") # Best approx
        self._add_tool("line", FIF.REMOVE, "Line Tool (U)") # REMOVE looks like a line? or MENU

        self._add_group("AI")
        self._add_tool("magic_wand", FIF.IOT, "Magic Wand (W)")
        self._add_tool("text", FIF.FONT_SIZE, "Text (T)")
        self._add_tool("upscale", FIF.ZOOM_IN, "Upscale 4x")
        self._add_tool("met", FIF.BOOK_SHELF, "Met Museum Inspiration")

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
