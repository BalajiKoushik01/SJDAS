"""
TOOL OPTIONS PANEL - Dynamic Settings Per Tool
Shows context-sensitive options for the active tool
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDockWidget, QFrame,
                             QHBoxLayout, QLabel, QSlider, QVBoxLayout,
                             QWidget)


class ToolOptionsPanel(QDockWidget):
    """Dynamic tool options panel like Paint Shop Pro."""

    options_changed = pyqtSignal(dict)  # Emit when options change

    def __init__(self, parent=None):
        super().__init__("Tool Options", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.TopDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea
        )

        # Main widget
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(8, 8, 8, 8)

        # Tool name label
        self.tool_label = QLabel("Select a tool")
        self.tool_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.main_layout.addWidget(self.tool_label)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        self.main_layout.addWidget(line)

        # Options container (dynamic content)
        self.options_container = QWidget()
        self.options_layout = QVBoxLayout(self.options_container)
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.options_container)

        self.main_layout.addStretch()

        self.setWidget(self.main_widget)

        # Current tool
        self.current_tool = None

    def set_tool(self, tool_name):
        """Update panel for the specified tool."""
        self.current_tool = tool_name
        self.tool_label.setText(f"{tool_name} Tool")

        # Clear existing options
        self.clear_options()

        # Add tool-specific options
        if tool_name == "Brush":
            self.add_brush_options()
        elif tool_name == "Eraser":
            self.add_eraser_options()
        elif tool_name == "Fill":
            self.add_fill_options()
        elif tool_name == "Gradient":
            self.add_gradient_options()
        elif tool_name == "Selection":
            self.add_selection_options()
        elif tool_name == "Magic Wand":
            self.add_magic_wand_options()
        elif tool_name == "Clone Stamp":
            self.add_clone_options()
        elif tool_name == "Text":
            self.add_text_options()
        else:
            self.add_default_options()

    def clear_options(self):
        """Clear all options from the panel."""
        while self.options_layout.count():
            child = self.options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add_brush_options(self):
        """Add brush-specific options."""
        # Size
        self.add_slider_option("Size:", 1, 200, 10, "px")

        # Opacity
        self.add_slider_option("Opacity:", 0, 100, 100, "%")

        # Hardness
        self.add_slider_option("Hardness:", 0, 100, 100, "%")

        # Spacing
        self.add_slider_option("Spacing:", 1, 200, 25, "%")

    def add_eraser_options(self):
        """Add eraser-specific options."""
        self.add_slider_option("Size:", 1, 200, 20, "px")
        self.add_slider_option("Opacity:", 0, 100, 100, "%")

    def add_fill_options(self):
        """Add fill tool options."""
        self.add_slider_option("Tolerance:", 0, 255, 32, "")
        self.add_checkbox_option("Contiguous", True)
        self.add_checkbox_option("Anti-alias", True)

    def add_gradient_options(self):
        """Add gradient options."""
        self.add_combo_option(
            "Type:", [
                "Linear", "Radial", "Angle", "Reflected"])
        self.add_checkbox_option("Reverse", False)
        self.add_slider_option("Opacity:", 0, 100, 100, "%")

    def add_selection_options(self):
        """Add selection options."""
        self.add_slider_option("Feather:", 0, 100, 0, "px")
        self.add_checkbox_option("Anti-alias", True)

    def add_magic_wand_options(self):
        """Add magic wand options."""
        self.add_slider_option("Tolerance:", 0, 255, 32, "")
        self.add_checkbox_option("Contiguous", True)
        self.add_checkbox_option("Sample All Layers", False)

    def add_clone_options(self):
        """Add clone stamp options."""
        self.add_slider_option("Size:", 1, 200, 50, "px")
        self.add_slider_option("Opacity:", 0, 100, 100, "%")
        self.add_checkbox_option("Aligned", True)

    def add_text_options(self):
        """Add text tool options."""
        self.add_label("Use Text Dialog for formatting")

    def add_default_options(self):
        """Add default options for unknown tools."""
        self.add_label("No options available for this tool")

    # Helper methods to add different option types

    def add_slider_option(self, label, min_val, max_val, default, unit):
        """Add a slider option."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 4, 0, 4)

        label_widget = QLabel(label)
        label_widget.setMinimumWidth(80)
        layout.addWidget(label_widget)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        layout.addWidget(slider)

        value_label = QLabel(f"{default}{unit}")
        value_label.setMinimumWidth(50)
        slider.valueChanged.connect(
            lambda v: value_label.setText(f"{v}{unit}")
        )
        layout.addWidget(value_label)

        self.options_layout.addWidget(container)

    def add_checkbox_option(self, label, default):
        """Add a checkbox option."""
        checkbox = QCheckBox(label)
        checkbox.setChecked(default)
        self.options_layout.addWidget(checkbox)

    def add_combo_option(self, label, items):
        """Add a combo box option."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 4, 0, 4)

        label_widget = QLabel(label)
        label_widget.setMinimumWidth(80)
        layout.addWidget(label_widget)

        combo = QComboBox()
        combo.addItems(items)
        layout.addWidget(combo)

        self.options_layout.addWidget(container)

    def add_label(self, text):
        """Add a simple label."""
        label = QLabel(text)
        label.setStyleSheet("color: #888; font-style: italic;")
        self.options_layout.addWidget(label)
