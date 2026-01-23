from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
                             QPushButton, QVBoxLayout, QWidget)
from qfluentwidgets import CheckBox
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import Slider


class LayerItemWidget(QWidget):
    """Custom widget for layer item in list."""
    visibility_toggled = pyqtSignal(bool)

    def __init__(self, name, layer_id, parent=None):
        super().__init__(parent)
        self.layer_id = layer_id

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Visibility Checkbox (Eye)
        self.chk_visible = CheckBox("")
        self.chk_visible.setChecked(True)
        self.chk_visible.stateChanged.connect(
            lambda s: self.visibility_toggled.emit(
                s == Qt.CheckState.Checked.value)
        )
        layout.addWidget(self.chk_visible)

        # Icon
        self.icon_label = QLabel()
        if "Mask" in name:
            # Fix: Use correct method to get pixmap from FluentIcon
            self.icon_label.setPixmap(
                FIF.EDIT.icon(
                    color=Qt.GlobalColor.white).pixmap(
                    16, 16))
        else:
            self.icon_label.setPixmap(
                FIF.PHOTO.icon(
                    color=Qt.GlobalColor.white).pixmap(
                    16, 16))
        layout.addWidget(self.icon_label)

        # Name
        self.lbl_name = QLabel(name)
        self.lbl_name.setFont(QFont("Segoe UI", 10))
        self.lbl_name.setStyleSheet("color: white;")
        layout.addWidget(self.lbl_name)

        layout.addStretch()


class LayersPanel(QWidget):
    """
    Professional Layers Panel (PaintShop Pro Style).
    Manages visibility and opacity of multiple layers.
    """
    layer_visibility_changed = pyqtSignal(str, bool)  # layer_id, visible
    layer_opacity_changed = pyqtSignal(str, int)  # layer_id, opacity 0-100

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_layer_id = "mask"  # Default active
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Header
        header = QLabel("Layers")
        header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(header)

        # Opacity Control for Selected Layer
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = Slider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self._on_opacity_change)
        opacity_layout.addWidget(self.opacity_slider)
        self.lbl_opacity = QLabel("100%")
        opacity_layout.addWidget(self.lbl_opacity)
        layout.addLayout(opacity_layout)

        # Layer List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #202020;
                border: 1px solid #3E3E42;
                border-radius: 4px;
            }
            QListWidget::item {
                height: 40px;
                border-bottom: 1px solid #2D2D30;
            }
            QListWidget::item:selected {
                background-color: #3E3E42;
            }
        """)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

        # Toolbar (New Layer, Delete, etc. - Phase 2)
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("+")
        btn_new.setFixedSize(24, 24)
        btn_new.setToolTip("New Layer (Coming Soon)")
        btn_new.setEnabled(False)
        btn_layout.addWidget(btn_new)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Initialize Default Layers
        self.add_layer("Drawing / Mask", "mask")
        self.add_layer("Original Image", "bg")

    def add_layer(self, name, layer_id):
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(item.sizeHint())

        widget = LayerItemWidget(name, layer_id)
        widget.visibility_toggled.connect(
            lambda v: self.layer_visibility_changed.emit(
                layer_id, v))

        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

        # Store ID in item data
        item.setData(Qt.ItemDataRole.UserRole, layer_id)

        # Select first layer
        if self.list_widget.count() == 1:
            self.list_widget.setCurrentItem(item)
            self.current_layer_id = layer_id

    def _on_opacity_change(self, value):
        self.lbl_opacity.setText(f"{value}%")
        if self.current_layer_id:
            self.layer_opacity_changed.emit(self.current_layer_id, value)

    def _on_item_clicked(self, item):
        self.current_layer_id = item.data(Qt.ItemDataRole.UserRole)
        # Reset opacity slider value would require storing state per layer.
        # For MVP, we assume 100% or query the view.
        # Ideally, we query the view model.
        pass
