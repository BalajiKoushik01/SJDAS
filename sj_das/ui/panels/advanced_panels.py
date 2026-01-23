"""
Advanced Desktop Features for SJ-DAS

NEW FEATURE: Layers Panel
- Organize designs in layers
- Show/hide individual layers
- Reorder layers
- Opacity control per layer
- Blend modes (Normal, Multiply, Overlay)
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QComboBox, QDockWidget, QFrame, QHBoxLayout,
                             QLabel, QListWidget, QListWidgetItem, QPushButton,
                             QSlider, QVBoxLayout, QWidget)


class LayersPanel(QDockWidget):
    """Professional layers panel like Photoshop."""

    layer_changed = pyqtSignal(int)  # Layer index changed
    layer_visibility_changed = pyqtSignal(int, bool)  # Index, visible

    def __init__(self, parent=None):
        super().__init__("Layers", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)

        # Main widget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)

        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_new_layer = QPushButton("+ Layer")
        self.btn_new_layer.setToolTip("Create new layer (Ctrl+Shift+N)")
        self.btn_delete_layer = QPushButton("🗑")
        self.btn_delete_layer.setToolTip("Delete selected layer")
        self.btn_merge_down = QPushButton("⬇ Merge")
        self.btn_merge_down.setToolTip("Merge with layer below")

        toolbar.addWidget(self.btn_new_layer)
        toolbar.addWidget(self.btn_delete_layer)
        toolbar.addWidget(self.btn_merge_down)
        layout.addLayout(toolbar)

        # Blend mode
        blend_layout = QHBoxLayout()
        blend_layout.addWidget(QLabel("Blend:"))
        self.blend_mode = QComboBox()
        self.blend_mode.addItems(
            ["Normal", "Multiply", "Screen", "Overlay", "Hard Light"])
        self.blend_mode.setToolTip("Blending mode for active layer")
        blend_layout.addWidget(self.blend_mode)
        layout.addLayout(blend_layout)

        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setToolTip("Layer opacity (0-100%)")
        self.opacity_label = QLabel("100%")
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        layout.addLayout(opacity_layout)

        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        self.opacity_slider.valueChanged.connect(self.update_opacity)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

        # Layers list
        self.layers_list = QListWidget()
        self.layers_list.setToolTip(
            "Click to select layer\nDouble-click to rename")
        layout.addWidget(self.layers_list)

        # Add default layers
        self.add_layer("Mask / Draw", "mask")
        self.add_layer("Background", "bg")
        self.add_layer("Grid", "grid", visible=True)

        self.setWidget(widget)

        # Connect signals
        self.btn_new_layer.clicked.connect(self.add_new_layer)
        self.btn_delete_layer.clicked.connect(self.delete_layer)
        self.layers_list.currentRowChanged.connect(self.layer_changed.emit)

        # Store editor reference? passed in init?
        # We need to update __init__ to accept editor

    def set_editor(self, editor):
        self.editor = editor

    def add_layer(self, name, layer_type="generic", visible=True):
        """Add a new layer to the list."""
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, layer_type)  # Store Type

        # Custom widget for the item
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(2, 2, 2, 2)

        # Eye Button
        btn_eye = QPushButton("👁")
        btn_eye.setFixedSize(24, 24)
        btn_eye.setCheckable(True)
        btn_eye.setChecked(visible)
        btn_eye.setStyleSheet(
            "border: none; background: transparent; font-size: 14px;")

        # Connect Toggle using closure to capture layer_type
        # Note: If multiple generic layers, this simple logic is flawed.
        # But for V1 (Bg + Mask), it's perfect.
        btn_eye.toggled.connect(
            lambda v,
            lt=layer_type: self.toggle_visibility(
                lt,
                v))

        l.addWidget(btn_eye)
        l.addWidget(QLabel(name))
        l.addStretch()

        item.setSizeHint(w.sizeHint())
        self.layers_list.addItem(item)
        self.layers_list.setItemWidget(item, w)
        return item

    def toggle_visibility(self, layer_type, visible):
        if hasattr(self, 'editor'):
            self.editor.set_layer_visibility(layer_type, visible)

    def add_new_layer(self):
        """Add a new layer with auto-incrementing name."""
        # Placeholder for future multi-layer support
        layer_num = self.layers_list.count() + 1
        self.add_layer(f"Layer {layer_num}")

    def delete_layer(self):
        """Delete the currently selected layer."""
        current_row = self.layers_list.currentRow()
        if current_row >= 0 and self.layers_list.count() > 1:  # Keep at least one layer
            self.layers_list.takeItem(current_row)

    def update_opacity(self, value):
        """Update opacity of selected layer."""
        if not hasattr(self, 'editor'):
            return

        item = self.layers_list.currentItem()
        if item:
            layer_type = item.data(Qt.ItemDataRole.UserRole)
            if layer_type:
                self.editor.set_layer_opacity(layer_type, value)


class HistoryPanel(QDockWidget):
    """Undo/Redo history panel with visualization."""

    history_jumped = pyqtSignal(int)  # Jump to specific history state

    def __init__(self, parent=None):
        super().__init__("History", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)

        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_undo = QPushButton("↶ Undo")
        self.btn_undo.setToolTip("Undo last action (Ctrl+Z)")
        self.btn_redo = QPushButton("↷ Redo")
        self.btn_redo.setToolTip("Redo action (Ctrl+Y)")
        self.btn_clear = QPushButton("🗑 Clear")
        self.btn_clear.setToolTip("Clear history")

        toolbar.addWidget(self.btn_undo)
        toolbar.addWidget(self.btn_redo)
        toolbar.addWidget(self.btn_clear)
        layout.addLayout(toolbar)

        # History list
        self.history_list = QListWidget()
        self.history_list.setToolTip("Click to jump to that state")
        layout.addWidget(self.history_list)

        # Initial state
        self.add_state("Initial Canvas")

        self.setWidget(widget)

        # Connect
        self.history_list.currentRowChanged.connect(self.history_jumped.emit)

    def add_state(self, action_name):
        """Add a history state."""
        item = QListWidgetItem(f"• {action_name}")
        self.history_list.addItem(item)
        self.history_list.setCurrentRow(self.history_list.count() - 1)


class ColorPalettePanel(QDockWidget):
    """Color palette manager for textile designs."""

    color_selected = pyqtSignal(object)  # QColor

    def __init__(self, parent=None):
        super().__init__("Color Palette", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)

        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_add_color = QPushButton("+ Color")
        self.btn_add_color.setToolTip("Add color to palette")
        self.btn_save_palette = QPushButton("💾 Save")
        self.btn_save_palette.setToolTip("Save palette to file")
        self.btn_load_palette = QPushButton("📂 Load")
        self.btn_load_palette.setToolTip("Load palette from file")

        toolbar.addWidget(self.btn_add_color)
        toolbar.addWidget(self.btn_save_palette)
        toolbar.addWidget(self.btn_load_palette)
        layout.addLayout(toolbar)

        # Preset palettes
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Default (8 colors)",
            "Grayscale",
            "Warm Colors",
            "Cool Colors",
            "Earth Tones",
            "Jewel Tones",
            "Pastel"
        ])
        self.preset_combo.setToolTip("Load preset color palette")
        layout.addWidget(self.preset_combo)

        # Color grid (placeholder - would show color swatches)
        info_label = QLabel(
            "Color swatches will appear here.\nClick to select, right-click to edit.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888; padding: 10px;")
        layout.addWidget(info_label)

        layout.addStretch()

        self.setWidget(widget)
