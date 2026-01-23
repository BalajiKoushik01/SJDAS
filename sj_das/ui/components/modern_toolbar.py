"""
Modern Toolbar Component.
A professional, Photoshop-style vertical toolbar.
"""

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import QButtonGroup, QFrame, QPushButton, QVBoxLayout

from sj_das.resources.icons import DASIcons


class ModernToolBar(QFrame):
    """
    Vertical Toolbar with group exclusivity and modern styling.
    """
    tool_selected = pyqtSignal(str)  # Emits tool_id (e.g., "pen", "eraser")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(54)  # Little wider for breathing room
        self.setObjectName("ModernToolBar")

        # Base Style
        self.setStyleSheet("""
            #ModernToolBar {
                background-color: #2D2D2D;
                border-right: 1px solid #111;
            }
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
                border: 1px solid #555;
            }
            QPushButton:checked {
                background-color: #1e1e1e;
                border: 1px solid #6C5CE7; /* Accent Color */
                border-left: 3px solid #6C5CE7;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 10, 4, 10)
        self.layout.setSpacing(6)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        # Default Tools Configuration
        self.tools = [
            ("select", "cursor_arrow", "Move / Select (V)", "V"),
            ("pen", "pen", "Pencil Tool (B)", "B"),
            ("eraser", "eraser", "Eraser (E)", "E"),
            ("fill", "paint_bucket", "Fill Bucket (G)", "G"),
            ("shapes", "shape_rect", "Rectangle (U)", "U"),
            ("magic_wand", "magic_wand", "Magic Wand (W)", "W"),
            ("text", "text_tool", "Text Tool (T)", "T"),  # New
            ("eyedropper", "eyedropper", "Eyedropper (I)", "I"),
            ("stamp", "clone_stamp", "Stamp / Pattern (S)", "S"),
            ("zoom", "search", "Zoom (Z)", "Z"),
            ("hand", "hand", "Hand / Pan (H)", "H"),
        ]

        self._init_tools()

    def _init_tools(self):
        """Create buttons for all tools."""
        for tool_id, icon_name, tooltip, shortcut in self.tools:
            btn = QPushButton()
            btn.setFixedSize(44, 44)
            btn.setCheckable(True)
            btn.setToolTip(f"{tooltip}")
            btn.setProperty("tool_id", tool_id)
            btn.setIcon(DASIcons.get_icon(icon_name))
            btn.setIconSize(QSize(24, 24))

            # Shortcut handling is usually done by Action or Window,
            # but we can set it here for display/simple triggering
            btn.setShortcut(shortcut)

            btn.clicked.connect(
                lambda checked,
                t=tool_id: self.tool_selected.emit(t))

            self.layout.addWidget(btn)
            self.btn_group.addButton(btn)

            # Store reference
            setattr(self, f"btn_{tool_id}", btn)

    def set_active_tool(self, tool_id):
        """Programmatically set active tool."""
        # Find button with this property
        for btn in self.btn_group.buttons():
            if btn.property("tool_id") == tool_id:
                btn.setChecked(True)
                break
