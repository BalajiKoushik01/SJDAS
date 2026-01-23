"""
Compact Toolbar for SJ-DAS (Professional Design System).
Clean, modern text-only interface without outdated icons.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QButtonGroup, QFrame, QPushButton, QVBoxLayout

from sj_das.ui.design_system import *


class CompactIconToolbar(QFrame):
    """Compact toolbar with clean text labels (Professional)."""

    tool_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CompactIconToolbar")
        self.setFixedWidth(TOOLBAR_WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            SPACING_TINY,
            SPACING_SMALL,
            SPACING_TINY,
            SPACING_SMALL)
        layout.setSpacing(SPACING_TINY)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Button group for exclusivity
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        # Define tools with clean text labels (NO ICONS)
        tools = [
            ("rect_select", "Select", "Rectangle Select (M)"),
            ("brush", "Brush", "Brush Tool (B)"),
            ("eraser", "Eraser", "Eraser (E)"),
            ("fill", "Fill", "Fill/Bucket (G)"),
            ("eyedropper", "Picker", "Eyedropper (I)"),
            ("wand", "Wand", "Magic Wand (W)"),
            ("rectangle", "Rect", "Rectangle Shape"),
            ("ellipse", "Circle", "Ellipse Shape"),
            ("line", "Line", "Line Tool"),
            ("pan", "Pan", "Pan/Hand (H)"),
            ("zoom", "Zoom", "Zoom Tool (Z)"),
        ]

        for tool_id, label, tooltip in tools:
            btn = self.create_tool_button(tool_id, label, tooltip)
            layout.addWidget(btn)
            self.btn_group.addButton(btn)

        # Professional styling using design system
        self.setStyleSheet(f"""
            #CompactIconToolbar {{
                background-color: {COLOR_BG_TERTIARY};
                border-right: {BORDER_WIDTH}px solid {COLOR_BORDER_PRIMARY};
            }}
            QPushButton {{
                background-color: transparent;
                border: {BORDER_WIDTH}px solid transparent;
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {SPACING_SMALL}px {SPACING_TINY}px;
                color: {COLOR_TEXT_SECONDARY};
                text-align: center;
                font-size: {FONT_SIZE_SMALL}px;
                font-family: "{FONT_FAMILY_PRIMARY}";
                font-weight: {FONT_WEIGHT_SEMIBOLD};
            }}
            QPushButton:hover {{
                background-color: {COLOR_BG_HOVER};
                border-color: {COLOR_BORDER_PRIMARY};
                color: {COLOR_TEXT_PRIMARY};
            }}
            QPushButton:checked {{
                background-color: {COLOR_BG_ACTIVE};
                border-color: {COLOR_ACCENT};
                border-left-width: 3px;
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)

    def create_tool_button(self, tool_id, label, tooltip):
        """Create a clean text-only tool button."""
        btn = QPushButton(label)
        btn.setFixedSize(TOOL_BUTTON_SIZE, BUTTON_HEIGHT)  # 64x32
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
