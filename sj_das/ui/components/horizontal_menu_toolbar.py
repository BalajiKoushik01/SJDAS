"""
Horizontal Menu Toolbar for SJ-DAS (Professional Design System).
Dropdown menus for tool categories at the top to maximize canvas space.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QMenu, QPushButton,
                             QWidget, QWidgetAction)

from sj_das.ui.design_system import *


class ToolMenuItem(QWidgetAction):
    """Custom widget action for tool menu items with icon and label."""

    tool_selected = pyqtSignal(str)

    def __init__(self, tool_id, icon, label, parent=None):
        super().__init__(parent)
        self.tool_id = tool_id

        # Create widget
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(
            SPACING_SMALL,
            SPACING_TINY,
            SPACING_SMALL,
            SPACING_TINY)
        layout.setSpacing(SPACING_SMALL)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", ICON_SIZE_MEDIUM))
        icon_label.setFixedWidth(ICON_SIZE_LARGE)
        layout.addWidget(icon_label)

        # Label
        text_label = QLabel(label)
        text_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_NORMAL))
        layout.addWidget(text_label)
        layout.addStretch()

        self.setDefaultWidget(widget)

        # Connect
        self.triggered.connect(lambda: self.tool_selected.emit(tool_id))


class HorizontalMenuToolbar(QFrame):
    """Horizontal menu bar with dropdown tool categories (Professional)."""

    tool_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HorizontalMenuToolbar")
        self.setFixedHeight(TOP_BAR_HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING_TINY, 0, SPACING_TINY, 0)
        layout.setSpacing(SPACING_TINY // 2)

        # Define tool categories
        self.create_tool_menus(layout)

        layout.addStretch()

        # Professional styling using design system
        self.setStyleSheet(f"""
            #HorizontalMenuToolbar {{
                background-color: {COLOR_BG_SECONDARY};
                border-bottom: {BORDER_WIDTH}px solid {COLOR_BORDER_PRIMARY};
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: {SPACING_SMALL}px {SPACING_MEDIUM}px;
                color: {COLOR_TEXT_PRIMARY};
                font-size: {FONT_SIZE_NORMAL}px;
                font-family: "{FONT_FAMILY_PRIMARY}";
                font-weight: {FONT_WEIGHT_NORMAL};
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BG_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BG_ACTIVE};
            }}
            QMenu {{
                background-color: {COLOR_BG_SECONDARY};
                border: {BORDER_WIDTH}px solid {COLOR_BORDER_PRIMARY};
                padding: {SPACING_TINY}px;
            }}
            QMenu::item {{
                padding: {SPACING_SMALL - 2}px {SPACING_LARGE}px {SPACING_SMALL - 2}px {SPACING_MEDIUM - 4}px;
                background-color: transparent;
            }}
            QMenu::item:selected {{
                background-color: {COLOR_BG_HOVER};
            }}
        """)

    def create_tool_menus(self, layout):
        """Create dropdown menus for each tool category."""

        # 1. Selection Menu
        selection_btn = QPushButton("Selection")
        selection_menu = QMenu(self)

        selection_tools = [
            ("rect_select", "□", "Rectangle Select"),
            ("ellipse_select", "○", "Ellipse Select"),
            ("lasso", "⚡", "Lasso"),
            ("polygon_lasso", "⬡", "Polygon Lasso"),
            ("wand", "🪄", "Magic Wand"),
        ]

        for tool_id, icon, label in selection_tools:
            action = ToolMenuItem(tool_id, icon, label, selection_menu)
            action.tool_selected.connect(self.tool_selected.emit)
            selection_menu.addAction(action)

        selection_btn.setMenu(selection_menu)
        layout.addWidget(selection_btn)

        # 2. Draw Menu
        draw_btn = QPushButton("Draw")
        draw_menu = QMenu(self)

        draw_tools = [
            ("brush", "🖌", "Brush"),
            ("pencil", "✏", "Pencil"),
            ("airbrush", "💨", "Airbrush"),
            ("eraser", "⌫", "Eraser"),
            ("clone", "📋", "Clone Stamp"),
        ]

        for tool_id, icon, label in draw_tools:
            action = ToolMenuItem(tool_id, icon, label, draw_menu)
            action.tool_selected.connect(self.tool_selected.emit)
            draw_menu.addAction(action)

        draw_btn.setMenu(draw_menu)
        layout.addWidget(draw_btn)

        # 3. Paint Menu
        paint_btn = QPushButton("Paint")
        paint_menu = QMenu(self)

        paint_tools = [
            ("fill", "🪣", "Fill/Bucket"),
            ("gradient", "🌈", "Gradient"),
            ("pattern", "◈", "Pattern Fill"),
            ("eyedropper", "💧", "Eyedropper"),
        ]

        for tool_id, icon, label in paint_tools:
            action = ToolMenuItem(tool_id, icon, label, paint_menu)
            action.tool_selected.connect(self.tool_selected.emit)
            paint_menu.addAction(action)

        paint_btn.setMenu(paint_menu)
        layout.addWidget(paint_btn)

        # 4. Shapes Menu
        shapes_btn = QPushButton("Shapes")
        shapes_menu = QMenu(self)

        shape_tools = [
            ("rectangle", "□", "Rectangle"),
            ("ellipse", "○", "Ellipse/Circle"),
            ("line", "─", "Line"),
        ]

        for tool_id, icon, label in shape_tools:
            action = ToolMenuItem(tool_id, icon, label, shapes_menu)
            action.tool_selected.connect(self.tool_selected.emit)
            shapes_menu.addAction(action)

        shapes_btn.setMenu(shapes_menu)
        layout.addWidget(shapes_btn)

        # 5. Transform Menu
        transform_btn = QPushButton("Transform")
        transform_menu = QMenu(self)

        transform_tools = [
            ("perspective", "⬚", "Perspective"),
            ("move", "✥", "Move"),
        ]

        for tool_id, icon, label in transform_tools:
            action = ToolMenuItem(tool_id, icon, label, transform_menu)
            action.tool_selected.connect(self.tool_selected.emit)
            transform_menu.addAction(action)

        transform_btn.setMenu(transform_menu)
        layout.addWidget(transform_btn)

        # 6. View Menu
        view_btn = QPushButton("View")
        view_menu = QMenu(self)

        view_tools = [
            ("zoom", "🔍", "Zoom"),
            ("pan", "✋", "Pan/Hand"),
        ]

        for tool_id, icon, label in view_tools:
            action = ToolMenuItem(tool_id, icon, label, view_menu)
            action.tool_selected.connect(self.tool_selected.emit)
            view_menu.addAction(action)

        view_btn.setMenu(view_menu)
        layout.addWidget(view_btn)
