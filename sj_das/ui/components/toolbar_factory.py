
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QFrame, QPushButton, QVBoxLayout

# Use PixelEditorWidget for constants if needed, or define own map
from sj_das.ui.editor_widget import PixelEditorWidget

COLORS = {
    'bg_primary': '#0F172A',
    'bg_secondary': '#1E293B',
    'bg_elevated': '#334155',
    'bg_hover': '#475569',
    'border_subtle': '#334155',
    'text_primary': '#E2E8F0',
    'accent_primary': '#6366F1',
}


class ToolbarFactory:
    """
    Factory for the Left Tool Strip.
    """

    def __init__(self, view):
        self.view = view

    def create_tool_strip(self) -> QFrame:
        """Create professional scrollable tool strip with full names"""
        from PyQt6.QtWidgets import QScrollArea

        # Main container
        container = QFrame()
        container.setObjectName("toolStripContainer")
        container.setMinimumWidth(48)  # Icon-only mode
        container.setMaximumWidth(200)  # Full width

        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Tool strip content
        tool_strip = QFrame()
        tool_strip.setObjectName("toolStrip")

        # Glass theme styling
        container.setStyleSheet(f"""
            QFrame#toolStripContainer {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(16, 18, 28, 0.95),
                    stop:1 rgba(13, 14, 21, 0.9));
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QFrame#toolStrip {{
                background: transparent;
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(26, 29, 41, 0.7),
                    stop:1 rgba(22, 25, 37, 0.6));
                color: #E0E6ED;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-top: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                min-height: 48px;
                padding: 8px 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 34, 56, 0.85),
                    stop:1 rgba(26, 30, 48, 0.75));
                border: 1px solid rgba(0, 240, 255, 0.4);
                color: #00F0FF;
            }}
            QPushButton:checked {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 240, 255, 0.3),
                    stop:1 rgba(0, 240, 255, 0.2));
                color: #00F0FF;
                border: 1px solid #00F0FF;
                font-weight: bold;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(0, 240, 255, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(0, 240, 255, 0.5);
            }}
        """)

        layout = QVBoxLayout(tool_strip)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(12)  # Better spacing between tools

        # Professional tools with full names
        tools = [
            ("🔲", "Select", "select"),
            ("⬚", "Marquee", "marquee"),
            ("🔗", "Lasso", "lasso"),
            ("✨", "Magic Wand", "magic_wand"),
            ("✂️", "Crop", "crop"),
            ("💧", "Eyedropper", "eyedropper"),
            ("🩹", "Healing", "heal"),
            ("🖌️", "Brush", "brush"),
            ("📋", "Clone", "clone"),
            ("⏱️", "History", "history"),
            ("🧹", "Eraser", "eraser"),
            ("🌈", "Gradient", "gradient"),
            ("☀️", "Dodge/Burn", "dodge"),
            ("🖊️", "Pen", "pen"),
            ("📝", "Text", "text"),
            ("📍", "Path Select", "path_select"),
            ("⬟", "Shape", "shape"),
            ("✋", "Hand", "pan"),
            ("🔍", "Zoom", "zoom"),
        ]

        self.view.tool_buttons = {}
        for icon, name, tool_id in tools:
            btn = QPushButton(f"{icon}  {name}")
            btn.setCheckable(True)
            btn.setToolTip(f"{name} Tool")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            # Connect to view's handler
            btn.clicked.connect(lambda checked,
                                tid=tool_id: self.view.on_tool_selected(tid))
            layout.addWidget(btn)
            self.view.tool_buttons[tool_id] = btn

        # Set first tool as active default
        if "select" in self.view.tool_buttons:
            self.view.tool_buttons["select"].setChecked(True)

        layout.addStretch()

        # Assemble scrollable structure
        scroll.setWidget(tool_strip)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll)

        return container

    @staticmethod
    def get_editor_tool_id(ui_tool_id: str):
        """Maps UI tool references to Editor engine constants."""
        tool_mapping = {
            "select": PixelEditorWidget.TOOL_SELECT_RECT,  # Basic
            "marquee": "marquee_rect",  # Pro
            "lasso": PixelEditorWidget.TOOL_LASSO,
            "magic_wand": PixelEditorWidget.TOOL_MAGIC_WAND,
            "crop": "crop",
            "eyedropper": PixelEditorWidget.TOOL_PICKER,
            "heal": "spot_healing",
            "brush": PixelEditorWidget.TOOL_BRUSH,
            "clone": PixelEditorWidget.TOOL_CLONE,
            "history": "history_brush",
            "eraser": PixelEditorWidget.TOOL_ERASER,
            "gradient": "gradient_fill",
            "fill": PixelEditorWidget.TOOL_FILL,
            "dodge": "dodge_burn",
            "pen": "pen_tool",
            "text": "text_tool",
            "path_select": "path_select",
            "shape": "shape_tool",  # Generic shape tool
            "rectangle": PixelEditorWidget.TOOL_RECT,
            "ellipse": PixelEditorWidget.TOOL_ELLIPSE,
            "line": PixelEditorWidget.TOOL_LINE,
            "pan": PixelEditorWidget.TOOL_PAN,
            "zoom": "zoom_tool"
        }
        return tool_mapping.get(ui_tool_id)
