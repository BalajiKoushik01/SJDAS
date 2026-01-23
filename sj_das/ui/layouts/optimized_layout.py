"""
Optimized Layout System for SJ-DAS
Maximizes screen real estate with professional design
"""
from typing import List, Optional

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QSplitter, QStackedWidget, QToolBar,
                             QToolButton, QVBoxLayout, QWidget)

from sj_das.ui.theme.premium_theme import PremiumTheme


class CollapsiblePanel(QFrame):
    """
    Collapsible panel for efficient space usage.
    Can be expanded/collapsed to show/hide content.
    """

    # Emits True when expanded, False when collapsed
    toggled = pyqtSignal(bool)

    def __init__(self, title: str, parent=None):
        """
        Initialize collapsible panel.

        Args:
            title: Panel title
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.is_expanded = True

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Setup panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.header = QPushButton(self.title)
        self.header.setCheckable(True)
        self.header.setChecked(True)
        self.header.clicked.connect(self.toggle)
        self.header.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: {PremiumTheme.SPACING['sm']}px;
                background-color: {PremiumTheme.COLORS['bg_elevated']};
                border: none;
                border-bottom: 1px solid {PremiumTheme.COLORS['border_subtle']};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PremiumTheme.COLORS['bg_hover']};
            }}
        """)
        layout.addWidget(self.header)

        # Content container
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(
            PremiumTheme.SPACING['sm'],
            PremiumTheme.SPACING['sm'],
            PremiumTheme.SPACING['sm'],
            PremiumTheme.SPACING['sm']
        )
        layout.addWidget(self.content_widget)

    def add_widget(self, widget: QWidget):
        """Add widget to panel content."""
        self.content_layout.addWidget(widget)

    def toggle(self):
        """Toggle panel expansion."""
        self.is_expanded = not self.is_expanded
        self.content_widget.setVisible(self.is_expanded)
        self.toggled.emit(self.is_expanded)

    def expand(self):
        """Expand panel."""
        if not self.is_expanded:
            self.toggle()

    def collapse(self):
        """Collapse panel."""
        if self.is_expanded:
            self.toggle()


class VerticalToolbar(QToolBar):
    """
    Vertical icon-only toolbar for space efficiency.
    Shows tooltips with keyboard shortcuts.
    """

    def __init__(self, parent=None):
        """Initialize vertical toolbar."""
        super().__init__(parent)
        self.setOrientation(Qt.Orientation.Vertical)
        self.setMovable(False)
        self.setIconSize(QSize(32, 32))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        # Style
        self.setStyleSheet(f"""
            QToolBar {{
                background-color: {PremiumTheme.COLORS['bg_secondary']};
                border-right: 1px solid {PremiumTheme.COLORS['border_subtle']};
                spacing: {PremiumTheme.SPACING['xs']}px;
                padding: {PremiumTheme.SPACING['sm']}px;
            }}

            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: {PremiumTheme.RADIUS['sm']}px;
                padding: {PremiumTheme.SPACING['sm']}px;
                min-width: 40px;
                min-height: 40px;
            }}

            QToolButton:hover {{
                background-color: {PremiumTheme.COLORS['bg_hover']};
            }}

            QToolButton:pressed {{
                background-color: {PremiumTheme.COLORS['bg_active']};
            }}

            QToolButton:checked {{
                background-color: {PremiumTheme.COLORS['accent_blue']};
            }}
        """)


class PropertiesPanel(QWidget):
    """
    Tabbed properties panel for tool settings.
    Efficient use of vertical space.
    """

    def __init__(self, parent=None):
        """Initialize properties panel."""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab bar (custom)
        tab_container = QWidget()
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)

        self.tabs = {}
        for tab_name in ['Tool', 'Layer', 'History']:
            btn = QPushButton(tab_name)
            btn.setCheckable(True)
            btn.clicked.connect(
                lambda checked,
                name=tab_name: self.switch_tab(name))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PremiumTheme.COLORS['bg_secondary']};
                    border: none;
                    border-bottom: 2px solid transparent;
                    padding: {PremiumTheme.SPACING['sm']}px;
                }}
                QPushButton:checked {{
                    background-color: {PremiumTheme.COLORS['bg_primary']};
                    border-bottom: 2px solid {PremiumTheme.COLORS['accent_blue']};
                }}
                QPushButton:hover {{
                    background-color: {PremiumTheme.COLORS['bg_hover']};
                }}
            """)
            tab_layout.addWidget(btn)
            self.tabs[tab_name] = btn

        layout.addWidget(tab_container)

        # Content area
        self.content = QStackedWidget()
        layout.addWidget(self.content)

        # Set first tab active
        self.tabs['Tool'].setChecked(True)

    def switch_tab(self, tab_name: str):
        """Switch to specified tab."""
        for name, btn in self.tabs.items():
            btn.setChecked(name == tab_name)


class OptimizedMainLayout(QWidget):
    """
    Optimized main layout for maximum screen utilization.

    Layout structure:
    ┌─────────────────────────────────────────┐
    │ [Toolbar] │ Canvas Area                 │
    │  (60px)   │  (Maximized)                │
    │           │                             │
    │           ├─────────────────────────────┤
    │           │ Properties Panel (280px)    │
    └───────────┴─────────────────────────────┘
    """

    def __init__(self, canvas_widget: QWidget, parent=None):
        """
        Initialize optimized layout.

        Args:
            canvas_widget: Main canvas/editor widget
            parent: Parent widget
        """
        super().__init__(parent)
        self.canvas_widget = canvas_widget
        self._setup_ui()

    def _setup_ui(self):
        """Setup main layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Vertical toolbar (left)
        self.toolbar = VerticalToolbar()
        layout.addWidget(self.toolbar)

        # Main splitter (canvas + properties)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(1)
        self.main_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {PremiumTheme.COLORS['border_subtle']};
            }}
            QSplitter::handle:hover {{
                background-color: {PremiumTheme.COLORS['accent_blue']};
            }}
        """)

        # Canvas area (maximized)
        canvas_container = QFrame()
        canvas_container.setStyleSheet(f"""
            QFrame {{
                background-color: {PremiumTheme.COLORS['canvas_bg']};
                border: none;
            }}
        """)
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.addWidget(self.canvas_widget)

        # Properties panel (right)
        self.properties = PropertiesPanel()
        self.properties.setMinimumWidth(280)
        self.properties.setMaximumWidth(400)

        # Add to splitter
        self.main_splitter.addWidget(canvas_container)
        self.main_splitter.addWidget(self.properties)

        # Set initial sizes (canvas gets most space)
        self.main_splitter.setStretchFactor(0, 4)  # Canvas: 80%
        self.main_splitter.setStretchFactor(1, 1)  # Properties: 20%

        layout.addWidget(self.main_splitter)

    def toggle_properties(self):
        """Toggle properties panel visibility."""
        self.properties.setVisible(not self.properties.isVisible())

    def enter_zen_mode(self):
        """Enter zen mode (canvas only)."""
        self.toolbar.setVisible(False)
        self.properties.setVisible(False)

    def exit_zen_mode(self):
        """Exit zen mode."""
        self.toolbar.setVisible(True)
        self.properties.setVisible(True)


class StatusBarWidget(QWidget):
    """
    Modern status bar with useful information.
    """

    def __init__(self, parent=None):
        """Initialize status bar."""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            PremiumTheme.SPACING['sm'],
            PremiumTheme.SPACING['xs'],
            PremiumTheme.SPACING['sm'],
            PremiumTheme.SPACING['xs']
        )

        # Style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {PremiumTheme.COLORS['bg_secondary']};
                border-top: 1px solid {PremiumTheme.COLORS['border_subtle']};
            }}
            QLabel {{
                color: {PremiumTheme.COLORS['text_secondary']};
                font-size: {PremiumTheme.FONT_SIZES['small']}px;
            }}
        """)

        # Status items
        self.tool_label = QLabel("Tool: None")
        self.size_label = QLabel("Size: 0x0")
        self.zoom_label = QLabel("Zoom: 100%")
        self.memory_label = QLabel("Memory: 0MB")

        layout.addWidget(self.tool_label)
        layout.addStretch()
        layout.addWidget(self.size_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.zoom_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.memory_label)

    def update_tool(self, tool_name: str):
        """Update current tool display."""
        self.tool_label.setText(f"Tool: {tool_name}")

    def update_size(self, width: int, height: int):
        """Update image size display."""
        self.size_label.setText(f"Size: {width}x{height}")

    def update_zoom(self, zoom: float):
        """Update zoom level display."""
        self.zoom_label.setText(f"Zoom: {zoom:.0f}%")

    def update_memory(self, memory_mb: float):
        """Update memory usage display."""
        self.memory_label.setText(f"Memory: {memory_mb:.1f}MB")


# Helper function to create optimized layout
def create_optimized_layout(canvas_widget: QWidget) -> OptimizedMainLayout:
    """
    Create optimized main layout.

    Args:
        canvas_widget: Main canvas/editor widget

    Returns:
        Configured OptimizedMainLayout instance
    """
    return OptimizedMainLayout(canvas_widget)
