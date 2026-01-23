"""
Premium Modern Tool Strip for SJ-DAS.
Clean, professional design with proper spacing.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QButtonGroup, QFrame, QPushButton, QVBoxLayout


class ModernToolStrip(QFrame):
    """Premium modern tool strip with clean design."""

    tool_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ModernToolStrip")
        self.setFixedWidth(72)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Button group for exclusivity
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        # Essential tools with clean names
        tools = [
            ("rect_select", "V", "Select", "Select Tool (V)"),
            ("brush", "B", "Brush", "Brush Tool (B)"),
            ("eraser", "E", "Eraser", "Eraser Tool (E)"),
            ("fill", "G", "Fill", "Fill Tool (G)"),
            ("pan", "H", "Pan", "Pan Tool (H)"),
            ("zoom", "Z", "Zoom", "Zoom Tool (Z)"),
        ]

        for tool_id, letter, name, tooltip in tools:
            btn = self.create_tool_button(tool_id, letter, name, tooltip)
            layout.addWidget(btn)
            self.btn_group.addButton(btn)

        layout.addStretch()

        # Premium styling (using direct color values)
        self.setStyleSheet("""
            #ModernToolStrip {
                background-color: #FFFFFF;
                border-right: 1px solid #3730A3;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: #94A3B8;
                font-size: 10px;
                font-family: "Inter", "Segoe UI", sans-serif;
                font-weight: 500;
                padding: 8px 4px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                color: #1A1A1A;
            }
            QPushButton:checked {
                background-color: #EEF2FF;
                color: #6366F1;
                border-left: 3px solid #6366F1;
            }
        """)

    def create_tool_button(self, tool_id, letter, name, tooltip):
        """Create premium tool button with letter and name."""
        btn = QPushButton(f"{letter}\n{name}")
        btn.setFixedSize(56, 64)
        btn.setCheckable(True)
        btn.setToolTip(tooltip)
        btn.setProperty("tool_id", tool_id)
        btn.clicked.connect(lambda: self.tool_selected.emit(tool_id))
        return btn

    def set_active_tool(self, tool_id):
        """Set active tool."""
        for btn in self.btn_group.buttons():
            if btn.property("tool_id") == tool_id:
                btn.setChecked(True)
                return
