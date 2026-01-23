"""
Professional Image Filters with Live Preview Dialogs
Global Standard Implementation - Matches Photoshop/PSP
"""

import cv2
import numpy as np
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QGroupBox,
                             QHBoxLayout, QLabel, QSlider, QSpinBox,
                             QVBoxLayout)


class FilterDialog(QDialog):
    """Base class for filter dialogs with live preview."""

    preview_requested = pyqtSignal(dict)  # parameters

    def __init__(self, parent=None, title="Filter"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(400, 300)
        self.preview_enabled = True
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.emit_preview)

    def request_preview(self):
        """Debounced preview request."""
        if self.preview_enabled:
            self.debounce_timer.start(100)  # 100ms debounce

    def emit_preview(self):
        """Emit preview signal with current parameters."""
        self.preview_requested.emit(self.get_parameters())

    def get_parameters(self):
        """Override in subclass to return filter parameters."""
        return {}


class GaussianBlurDialog(FilterDialog):
    """Professional Gaussian Blur dialog with live preview."""

    def __init__(self, parent=None):
        super().__init__(parent, "Gaussian Blur")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Preview checkbox
        preview_layout = QHBoxLayout()
        self.chk_preview = QCheckBox("Live Preview")
        self.chk_preview.setChecked(True)
        self.chk_preview.toggled.connect(
            lambda checked: setattr(
                self, 'preview_enabled', checked))
        preview_layout.addWidget(self.chk_preview)
        preview_layout.addStretch()
        layout.addLayout(preview_layout)

        # Radius control
        radius_group = QGroupBox("Blur Radius")
        radius_layout = QVBoxLayout()

        slider_layout = QHBoxLayout()
        self.radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.radius_slider.setRange(1, 50)
        self.radius_slider.setValue(5)
        self.radius_slider.valueChanged.connect(self.on_radius_changed)
        slider_layout.addWidget(self.radius_slider)

        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 50)
        self.radius_spin.setValue(5)
        self.radius_spin.setSuffix(" px")
        self.radius_spin.valueChanged.connect(self.radius_slider.setValue)
        slider_layout.addWidget(self.radius_spin)

        radius_layout.addLayout(slider_layout)
        radius_group.setLayout(radius_layout)
        layout.addWidget(radius_group)

        # Info label
        info = QLabel(
            "Higher values create stronger blur effect.\nOdd numbers work best.")
        info.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info)

        layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Reset
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(
            QDialogButtonBox.StandardButton.Reset).clicked.connect(
            self.reset)
        layout.addWidget(buttons)

        # Initial preview
        self.request_preview()

    def on_radius_changed(self, value):
        self.radius_spin.setValue(value)
        self.request_preview()

    def reset(self):
        self.radius_slider.setValue(5)

    def get_parameters(self):
        return {'radius': self.radius_slider.value()}


class SharpenDialog(FilterDialog):
    """Professional Sharpen dialog with strength control."""

    def __init__(self, parent=None):
        super().__init__(parent, "Sharpen")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Preview checkbox
        preview_layout = QHBoxLayout()
        self.chk_preview = QCheckBox("Live Preview")
        self.chk_preview.setChecked(True)
        self.chk_preview.toggled.connect(
            lambda checked: setattr(
                self, 'preview_enabled', checked))
        preview_layout.addWidget(self.chk_preview)
        preview_layout.addStretch()
        layout.addLayout(preview_layout)

        # Strength control
        strength_group = QGroupBox("Sharpen Strength")
        strength_layout = QVBoxLayout()

        slider_layout = QHBoxLayout()
        self.strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.strength_slider.setRange(1, 200)
        self.strength_slider.setValue(100)
        self.strength_slider.valueChanged.connect(self.on_strength_changed)
        slider_layout.addWidget(self.strength_slider)

        self.strength_label = QLabel("100%")
        self.strength_label.setMinimumWidth(50)
        slider_layout.addWidget(self.strength_label)

        strength_layout.addLayout(slider_layout)
        strength_group.setLayout(strength_layout)
        layout.addWidget(strength_group)

        # Info
        info = QLabel("100% = Standard sharpening\n>100% = Stronger effect")
        info.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info)

        layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Reset
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(
            QDialogButtonBox.StandardButton.Reset).clicked.connect(
            self.reset)
        layout.addWidget(buttons)

        self.request_preview()

    def on_strength_changed(self, value):
        self.strength_label.setText(f"{value}%")
        self.request_preview()

    def reset(self):
        self.strength_slider.setValue(100)

    def get_parameters(self):
        return {'strength': self.strength_slider.value() / 100.0}


class ImageFilters:
    """Professional image filter implementations."""

    @staticmethod
    def gaussian_blur(image, radius=5):
        """Apply Gaussian blur."""
        # Ensure odd kernel size
        kernel_size = radius * 2 + 1 if radius % 2 == 0 else radius
        if kernel_size < 3:
            kernel_size = 3

        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    @staticmethod
    def sharpen(image, strength=1.0):
        """Apply sharpening filter."""
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ]) * strength

        return cv2.filter2D(image, -1, kernel)

    @staticmethod
    def emboss(image):
        """Apply emboss effect."""
        kernel = np.array([
            [-2, -1, 0],
            [-1, 1, 1],
            [0, 1, 2]
        ])

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        embossed = cv2.filter2D(gray, -1, kernel)

        # Add 128 to bring it to mid-gray
        embossed = np.clip(embossed.astype(int) + 128, 0, 255).astype(np.uint8)

        # Convert back to RGB
        return cv2.cvtColor(embossed, cv2.COLOR_GRAY2RGB)

    @staticmethod
    def edge_detect(image, low_threshold=50, high_threshold=150):
        """Apply Canny edge detection."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, low_threshold, high_threshold)

        # Convert to RGB
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    @staticmethod
    def unsharp_mask(image, radius=5, amount=1.0):
        """Professional unsharp mask."""
        blurred = ImageFilters.gaussian_blur(image, radius)
        sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
        return sharpened

    @staticmethod
    def add_noise(image, amount=0.1, noise_type='gaussian'):
        """Add noise to image."""
        if noise_type == 'gaussian':
            noise = np.random.normal(0, amount * 255, image.shape)
            noisy = np.clip(
                image.astype(float) +
                noise,
                0,
                255).astype(
                np.uint8)
        else:  # salt-pepper
            noisy = image.copy()
            num_pixels = int(amount * image.size)
            coords = [np.random.randint(0, i, num_pixels)
                      for i in image.shape[:2]]
            noisy[coords[0], coords[1], :] = 255

        return noisy

    @staticmethod
    def median_filter(image, kernel_size=5):
        """Apply median filter for noise reduction."""
        return cv2.medianBlur(image, kernel_size)

    @staticmethod
    def bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
        """Apply bilateral filter - edge-preserving smoothing."""
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)


class FilterDialogs:
    """Factory for creating filter dialogs."""

    @staticmethod
    def gaussian_blur_dialog(parent=None):
        return GaussianBlurDialog(parent)

    @staticmethod
    def sharpen_dialog(parent=None):
        return SharpenDialog(parent)
