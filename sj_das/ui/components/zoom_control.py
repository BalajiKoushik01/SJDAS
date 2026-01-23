"""
Premium Zoom Control Widget
Modern zoom controls for canvas with smooth animations
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QWidget


class ZoomControl(QWidget):
    """Premium zoom control widget"""

    zoom_changed = pyqtSignal(float)  # Emit zoom level (1.0 = 100%)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_zoom = 1.0
        self.init_ui()

    def init_ui(self):
        """Initialize the zoom control UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Zoom out button
        self.btn_zoom_out = QPushButton("−")
        self.btn_zoom_out.setFixedSize(32, 32)
        self.btn_zoom_out.setToolTip("Zoom Out (Ctrl+-)")
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        layout.addWidget(self.btn_zoom_out)

        # Zoom slider
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(10)  # 10%
        self.zoom_slider.setMaximum(400)  # 400%
        self.zoom_slider.setValue(100)  # 100%
        self.zoom_slider.setFixedWidth(120)
        self.zoom_slider.setToolTip("Zoom Level")
        self.zoom_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.zoom_slider)

        # Zoom in button
        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setFixedSize(32, 32)
        self.btn_zoom_in.setToolTip("Zoom In (Ctrl++)")
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        layout.addWidget(self.btn_zoom_in)

        # Zoom percentage label
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        font.setWeight(QFont.Weight.Medium)
        self.zoom_label.setFont(font)
        layout.addWidget(self.zoom_label)

        # Fit to screen button
        self.btn_fit = QPushButton("Fit")
        self.btn_fit.setFixedSize(50, 32)
        self.btn_fit.setToolTip("Fit to Screen (Ctrl+0)")
        self.btn_fit.clicked.connect(self.fit_to_screen)
        layout.addWidget(self.btn_fit)

        # Style
        self.setStyleSheet("""
            ZoomControl {
                background-color: #252233;
                border: 1px solid #3730A3;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #312E44;
                color: #E2E8F0;
                border: 1px solid #3730A3;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6366F1;
                border-color: #818CF8;
            }
            QLabel {
                color: #E2E8F0;
                background-color: transparent;
            }
        """)

    def zoom_in(self):
        """Zoom in by 10%"""
        new_value = min(400, self.zoom_slider.value() + 10)
        self.zoom_slider.setValue(new_value)

    def zoom_out(self):
        """Zoom out by 10%"""
        new_value = max(10, self.zoom_slider.value() - 10)
        self.zoom_slider.setValue(new_value)

    def fit_to_screen(self):
        """Fit to screen (100%)"""
        self.zoom_slider.setValue(100)

    def on_slider_changed(self, value):
        """Handle slider value change"""
        self.current_zoom = value / 100.0
        self.zoom_label.setText(f"{value}%")
        self.zoom_changed.emit(self.current_zoom)

    def set_zoom(self, zoom_level):
        """Set zoom level programmatically"""
        value = int(zoom_level * 100)
        self.zoom_slider.setValue(value)
