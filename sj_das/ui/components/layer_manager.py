"""
Layer Management System for SJ-DAS.
Provides Photoshop-like layer functionality.
"""

import cv2
import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QPushButton, QVBoxLayout,
                             QWidget)


class Layer:
    """Represents a single layer."""

    def __init__(self, name="Layer", image=None, visible=True, opacity=100):
        self.name = name
        self.image = image  # QImage
        self.visible = visible
        self.opacity = opacity  # 0-100

    def to_numpy(self):
        """Convert layer image to numpy array."""
        if not self.image:
            return None

        width = self.image.width()
        height = self.image.height()
        ptr = self.image.constBits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        return arr


class LayerManager(QWidget):
    """Layer management panel."""

    layers_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = []
        self.current_layer_index = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("<b>Layers</b>")
        layout.addWidget(title)

        # Layer list
        self.layer_list = QListWidget()
        self.layer_list.currentRowChanged.connect(self.on_layer_selected)
        layout.addWidget(self.layer_list)

        # Buttons
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("+ Add")
        self.btn_add.clicked.connect(self.add_layer)
        btn_layout.addWidget(self.btn_add)

        self.btn_delete = QPushButton("- Delete")
        self.btn_delete.clicked.connect(self.delete_layer)
        btn_layout.addWidget(self.btn_delete)

        self.btn_merge = QPushButton("Merge")
        self.btn_merge.clicked.connect(self.merge_down)
        btn_layout.addWidget(self.btn_merge)

        layout.addLayout(btn_layout)

        # Move buttons
        move_layout = QHBoxLayout()

        self.btn_up = QPushButton("↑ Up")
        self.btn_up.clicked.connect(self.move_up)
        move_layout.addWidget(self.btn_up)

        self.btn_down = QPushButton("↓ Down")
        self.btn_down.clicked.connect(self.move_down)
        move_layout.addWidget(self.btn_down)

        layout.addLayout(move_layout)

        # Initialize with one layer
        self.add_layer("Background")

    def add_layer(self, name=None):
        """Add a new layer."""
        if name is None:
            name = f"Layer {len(self.layers) + 1}"

        layer = Layer(name=name)
        self.layers.append(layer)

        # Add to list widget
        item = QListWidgetItem(name)
        item.setCheckState(Qt.CheckState.Checked)  # Visible by default
        self.layer_list.addItem(item)

        self.layers_changed.emit()

    def delete_layer(self):
        """Delete current layer."""
        if len(self.layers) <= 1:
            return  # Keep at least one layer

        index = self.layer_list.currentRow()
        if index >= 0:
            del self.layers[index]
            self.layer_list.takeItem(index)
            self.layers_changed.emit()

    def move_up(self):
        """Move layer up in stack."""
        index = self.layer_list.currentRow()
        if index > 0:
            # Swap in list
            self.layers[index], self.layers[index -
                                            1] = self.layers[index - 1], self.layers[index]

            # Swap in widget
            item = self.layer_list.takeItem(index)
            self.layer_list.insertItem(index - 1, item)
            self.layer_list.setCurrentRow(index - 1)

            self.layers_changed.emit()

    def move_down(self):
        """Move layer down in stack."""
        index = self.layer_list.currentRow()
        if index < len(self.layers) - 1:
            # Swap in list
            self.layers[index], self.layers[index +
                                            1] = self.layers[index + 1], self.layers[index]

            # Swap in widget
            item = self.layer_list.takeItem(index)
            self.layer_list.insertItem(index + 1, item)
            self.layer_list.setCurrentRow(index + 1)

            self.layers_changed.emit()

    def merge_down(self):
        """Merge current layer with layer below."""
        index = self.layer_list.currentRow()
        if index >= len(self.layers) - 1:
            return  # Can't merge bottom layer

        # Merge images
        current = self.layers[index]
        below = self.layers[index + 1]

        if current.image and below.image:
            # Composite current onto below
            merged = self._composite_layers(
                below.image, current.image, current.opacity)
            below.image = merged

        # Remove current layer
        del self.layers[index]
        self.layer_list.takeItem(index)

        self.layers_changed.emit()

    def _composite_layers(self, bottom, top, opacity):
        """Composite two layers."""
        # Convert to numpy
        bottom_arr = self._qimage_to_numpy(bottom)
        top_arr = self._qimage_to_numpy(top)

        # Apply opacity
        alpha = opacity / 100.0

        # Blend
        result = cv2.addWeighted(bottom_arr, 1 - alpha, top_arr, alpha, 0)

        # Convert back
        return self._numpy_to_qimage(result)

    def _qimage_to_numpy(self, qimage):
        """Convert QImage to numpy."""
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.constBits()
        ptr.setsize(height * width * 4)
        return np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

    def _numpy_to_qimage(self, arr):
        """Convert numpy to QImage."""
        height, width, channel = arr.shape
        bytes_per_line = 4 * width
        return QImage(arr.data, width, height, bytes_per_line,
                      QImage.Format.Format_RGBA8888).copy()

    def on_layer_selected(self, index):
        """Handle layer selection."""
        if index >= 0:
            self.current_layer_index = index

    def get_composite_image(self):
        """Get final composited image."""
        if not self.layers:
            return None

        # Start with bottom layer
        result = None

        for i in range(len(self.layers) - 1, -1, -1):
            layer = self.layers[i]

            # Check visibility
            item = self.layer_list.item(i)
            if item.checkState() != Qt.CheckState.Checked:
                continue

            if not layer.image:
                continue

            if result is None:
                result = layer.image.copy()
            else:
                result = self._composite_layers(
                    result, layer.image, layer.opacity)

        return result

    def set_layer_image(self, index, qimage):
        """Set image for a specific layer."""
        if 0 <= index < len(self.layers):
            self.layers[index].image = qimage
            self.layers_changed.emit()

    def get_current_layer(self):
        """Get currently selected layer."""
        if 0 <= self.current_layer_index < len(self.layers):
            return self.layers[self.current_layer_index]
        return None
