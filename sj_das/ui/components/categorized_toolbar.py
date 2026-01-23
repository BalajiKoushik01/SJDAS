"""
Categorized Toolbar Component for SJ-DAS.
Professional vertical toolbar with expandable tool groups and proper icons.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QButtonGroup, QFrame, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QVBoxLayout, QWidget)


class ToolButton(QPushButton):
    """Individual tool button with icon and label."""

    def __init__(self, tool_id, icon, label, tooltip="", parent=None):
        super().__init__(parent)
        self.tool_id = tool_id
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setMinimumWidth(80)

        # Layout: Icon on left, label on right
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Icon label (Unicode symbol)
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedWidth(24)
        layout.addWidget(icon_label)

        # Text label
        text_label = QLabel(label)
        text_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(text_label)
        layout.addStretch()

        self.setToolTip(tooltip or label)
        self.setStyleSheet("""
            ToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                text-align: left;
            }
            ToolButton:hover {
                background-color: #3D3D3D;
                border: 1px solid #555;
            }
            ToolButton:checked {
                background-color: #1e1e1e;
                border: 1px solid #6C5CE7;
                border-left: 3px solid #6C5CE7;
            }
        """)


class ToolGroup(QFrame):
    """Expandable group of related tools."""

    tool_selected = pyqtSignal(str)

    def __init__(self, title, tools, parent=None):
        super().__init__(parent)
        self.title = title
        self.tools = tools
        self.is_expanded = True

        self.setObjectName("ToolGroup")
        self.setStyleSheet("""
            #ToolGroup {
                background-color: #2D2D2D;
                border: none;
                border-bottom: 1px solid #1a1a1a;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header (clickable to expand/collapse)
        self.header = QPushButton(f"▼ {title}")
        self.header.setCheckable(False)
        self.header.setFixedHeight(32)
        self.header.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                border: none;
                text-align: left;
                padding-left: 12px;
                font-weight: bold;
                font-size: 10px;
                color: #AAA;
            }
            QPushButton:hover {
                background-color: #2D2D2D;
                color: #FFF;
            }
        """)
        self.header.clicked.connect(self.toggle_expand)
        layout.addWidget(self.header)

        # Tools container
        self.tools_container = QWidget()
        self.tools_layout = QVBoxLayout(self.tools_container)
        self.tools_layout.setContentsMargins(4, 4, 4, 4)
        self.tools_layout.setSpacing(2)

        # Button group for exclusivity
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        # Add tool buttons
        for tool_id, icon, label, tooltip in tools:
            btn = ToolButton(tool_id, icon, label, tooltip)
            btn.clicked.connect(lambda checked,
                                tid=tool_id: self.tool_selected.emit(tid))
            self.tools_layout.addWidget(btn)
            self.btn_group.addButton(btn)

        layout.addWidget(self.tools_container)

    def toggle_expand(self):
        """Toggle expand/collapse state."""
        self.is_expanded = not self.is_expanded
        self.tools_container.setVisible(self.is_expanded)
        self.header.setText(f"{'▼' if self.is_expanded else '▶'} {self.title}")

    def set_active_tool(self, tool_id):
        """Set active tool in this group."""
        for btn in self.btn_group.buttons():
            if btn.tool_id == tool_id:
                btn.setChecked(True)
                return True
        return False


class CategorizedToolbar(QScrollArea):
    """Main categorized toolbar with expandable groups."""

    tool_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Main container
        container = QWidget()
        self.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Define tool categories with Unicode icons
        self.groups = []

        # 1. Selection Tools
        selection_tools = [
            ("rect_select", "□", "Rectangle", "Rectangle Select (M)"),
            ("ellipse_select", "○", "Ellipse", "Ellipse Select"),
            ("lasso", "⚡", "Lasso", "Lasso Select (L)"),
            ("polygon_lasso", "⬡", "Polygon", "Polygon Lasso"),
            ("wand", "🪄", "Magic Wand", "Magic Wand (W)"),
        ]
        select_group = ToolGroup("SELECTION", selection_tools)
        select_group.tool_selected.connect(self.tool_selected.emit)
        layout.addWidget(select_group)
        self.groups.append(select_group)

        # 2. Drawing Tools
        draw_tools = [
            ("brush", "🖌", "Brush", "Brush Tool (B)"),
            ("pencil", "✏", "Pencil", "Pencil Tool (P)"),
            ("airbrush", "💨", "Airbrush", "Airbrush Tool"),
            ("eraser", "⌫", "Eraser", "Eraser Tool (E)"),
            ("clone", "📋", "Clone Stamp", "Clone Stamp (S)"),
        ]
        draw_group = ToolGroup("DRAW", draw_tools)
        draw_group.tool_selected.connect(self.tool_selected.emit)
        layout.addWidget(draw_group)
        self.groups.append(draw_group)

        # 3. Paint Tools
        paint_tools = [
            ("fill", "🪣", "Fill", "Fill/Bucket Tool (G)"),
            ("gradient", "🌈", "Gradient", "Gradient Tool"),
            ("pattern", "◈", "Pattern", "Pattern Fill"),
            ("eyedropper", "💧", "Eyedropper", "Eyedropper (I)"),
        ]
        paint_group = ToolGroup("PAINT", paint_tools)
        paint_group.tool_selected.connect(self.tool_selected.emit)
        layout.addWidget(paint_group)
        self.groups.append(paint_group)

        # 4. Shape Tools
        shape_tools = [
            ("rectangle", "□", "Rectangle", "Rectangle Shape (U)"),
            ("ellipse", "○", "Ellipse", "Ellipse/Circle Shape"),
            ("line", "─", "Line", "Line Tool"),
        ]
        shape_group = ToolGroup("SHAPES", shape_tools)
        shape_group.tool_selected.connect(self.tool_selected.emit)
        layout.addWidget(shape_group)
        self.groups.append(shape_group)

        # 5. Transform Tools
        transform_tools = [
            ("perspective", "⬚", "Perspective", "Perspective Transform"),
            ("move", "✥", "Move", "Move Tool (V)"),
        ]
        transform_group = ToolGroup("TRANSFORM", transform_tools)
        transform_group.tool_selected.connect(self.tool_selected.emit)
        layout.addWidget(transform_group)
        self.groups.append(transform_group)

        # 6. View Tools
        view_tools = [
            ("zoom", "🔍", "Zoom", "Zoom Tool (Z)"),
            ("pan", "✋", "Pan", "Pan/Hand Tool (H)"),
        ]
        view_group = ToolGroup("VIEW", view_tools)
        view_group.tool_selected.connect(self.tool_selected.emit)
        layout.addWidget(view_group)
        self.groups.append(view_group)

        # Style
        self.setStyleSheet("""
            QScrollArea {
                background-color: #2D2D2D;
                border: none;
                border-right: 1px solid #111;
            }
        """)

    def set_active_tool(self, tool_id):
        """Set active tool across all groups."""
        for group in self.groups:
            if group.set_active_tool(tool_id):
                return
