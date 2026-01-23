"""
Context-sensitive properties panel for SJ-DAS.

Displays properties of the currently selected item (layer, tool, selection)
with live preview and preset management.
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QGroupBox, QHBoxLayout,
                             QLabel, QPushButton, QScrollArea, QSlider,
                             QSpinBox, QVBoxLayout, QWidget)

logger = logging.getLogger("SJ_DAS.PropertiesPanel")


class PropertiesPanel(QWidget):
    """
    Context-sensitive properties panel.

    Shows different properties based on what's selected:
    - Tool properties (brush size, opacity, etc.)
    - Layer properties (opacity, blend mode, etc.)
    - Selection properties (dimensions, position, etc.)
    """

    property_changed = pyqtSignal(str, object)  # (property_name, value)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_context = None
        self.setup_ui()

    def setup_ui(self):
        """Setup properties panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Title
        self.title_label = QLabel("Properties")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #E2E8F0;
                padding-bottom: 8px;
            }
        """)
        layout.addWidget(self.title_label)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)

        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)

        # Show default (no selection) state
        self.show_no_selection()

    def show_no_selection(self):
        """Show message when nothing is selected."""
        self.clear_properties()

        label = QLabel(
            "No selection\n\nSelect a layer, tool, or area\nto view properties")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #94A3B8; padding: 40px;")
        self.content_layout.addWidget(label)
        self.content_layout.addStretch()

    def show_tool_properties(self, tool_name: str, properties: dict):
        """
        Show properties for a tool.

        Args:
            tool_name: Name of the tool
            properties: Dictionary of property values
        """
        self.clear_properties()
        self.current_context = 'tool'
        self.title_label.setText(f"Tool: {tool_name}")

        # Brush Size
        if 'brush_size' in properties:
            size_group = self._create_slider_property(
                "Brush Size",
                properties['brush_size'],
                1, 200,
                lambda v: self.property_changed.emit('brush_size', v)
            )
            self.content_layout.addWidget(size_group)

        # Opacity
        if 'opacity' in properties:
            opacity_group = self._create_slider_property(
                "Opacity",
                int(properties['opacity'] * 100),
                0, 100,
                lambda v: self.property_changed.emit('opacity', v / 100.0),
                suffix="%"
            )
            self.content_layout.addWidget(opacity_group)

        # Hardness (for brush)
        if 'hardness' in properties:
            hardness_group = self._create_slider_property(
                "Hardness",
                int(properties['hardness'] * 100),
                0, 100,
                lambda v: self.property_changed.emit('hardness', v / 100.0),
                suffix="%"
            )
            self.content_layout.addWidget(hardness_group)

        self.content_layout.addStretch()

    def show_layer_properties(self, layer_name: str, properties: dict):
        """Show properties for a layer."""
        self.clear_properties()
        self.current_context = 'layer'
        self.title_label.setText(f"Layer: {layer_name}")

        # Layer opacity
        opacity_group = self._create_slider_property(
            "Opacity",
            int(properties.get('opacity', 1.0) * 100),
            0, 100,
            lambda v: self.property_changed.emit('layer_opacity', v / 100.0),
            suffix="%"
        )
        self.content_layout.addWidget(opacity_group)

        # Blend mode
        blend_group = QGroupBox("Blend Mode")
        blend_layout = QVBoxLayout(blend_group)

        blend_combo = QComboBox()
        blend_combo.addItems([
            "Normal", "Multiply", "Screen", "Overlay",
            "Darken", "Lighten", "Color Dodge", "Color Burn"
        ])
        blend_combo.setCurrentText(properties.get('blend_mode', 'Normal'))
        blend_combo.currentTextChanged.connect(
            lambda v: self.property_changed.emit('blend_mode', v)
        )
        blend_layout.addWidget(blend_combo)

        self.content_layout.addWidget(blend_group)

        # Visibility
        visible_check = QCheckBox("Visible")
        visible_check.setChecked(properties.get('visible', True))
        visible_check.toggled.connect(
            lambda v: self.property_changed.emit('visible', v)
        )
        self.content_layout.addWidget(visible_check)

        # Locked
        locked_check = QCheckBox("Locked")
        locked_check.setChecked(properties.get('locked', False))
        locked_check.toggled.connect(
            lambda v: self.property_changed.emit('locked', v)
        )
        self.content_layout.addWidget(locked_check)

        self.content_layout.addStretch()

    def show_selection_properties(self, properties: dict):
        """Show properties for a selection."""
        self.clear_properties()
        self.current_context = 'selection'
        self.title_label.setText("Selection")

        # Dimensions
        info_group = QGroupBox("Dimensions")
        info_layout = QVBoxLayout(info_group)

        width = properties.get('width', 0)
        height = properties.get('height', 0)
        x = properties.get('x', 0)
        y = properties.get('y', 0)

        info_layout.addWidget(QLabel(f"Width: {width}px"))
        info_layout.addWidget(QLabel(f"Height: {height}px"))
        info_layout.addWidget(QLabel(f"Position: ({x}, {y})"))
        info_layout.addWidget(QLabel(f"Area: {width * height}px²"))

        self.content_layout.addWidget(info_group)

        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)

        copy_btn = QPushButton("Copy Selection")
        copy_btn.clicked.connect(
            lambda: self.property_changed.emit(
                'action', 'copy'))
        actions_layout.addWidget(copy_btn)

        cut_btn = QPushButton("Cut Selection")
        cut_btn.clicked.connect(
            lambda: self.property_changed.emit(
                'action', 'cut'))
        actions_layout.addWidget(cut_btn)

        clear_btn = QPushButton("Clear Selection")
        clear_btn.clicked.connect(
            lambda: self.property_changed.emit(
                'action', 'clear'))
        actions_layout.addWidget(clear_btn)

        self.content_layout.addWidget(actions_group)
        self.content_layout.addStretch()

    def clear_properties(self):
        """Clear all property widgets."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _create_slider_property(
        self,
        label: str,
        value: int,
        min_val: int,
        max_val: int,
        callback,
        suffix: str = ""
    ) -> QGroupBox:
        """Create a slider property control."""
        group = QGroupBox(label)
        layout = QHBoxLayout(group)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(value)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #334155;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #6366F1;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
        """)

        spinbox = QSpinBox()
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setValue(value)
        spinbox.setSuffix(suffix)
        spinbox.setFixedWidth(80)

        # Connect both controls
        slider.valueChanged.connect(spinbox.setValue)
        spinbox.valueChanged.connect(slider.setValue)
        slider.valueChanged.connect(callback)

        layout.addWidget(slider, 1)
        layout.addWidget(spinbox)

        return group
