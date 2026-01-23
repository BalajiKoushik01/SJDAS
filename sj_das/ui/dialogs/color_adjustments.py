"""
PHASE 2: COLOR ADJUSTMENTS - Professional Image Editing
Implements Brightness/Contrast, Hue/Saturation, Levels, Curves
Like Paint Shop Pro and Photoshop
"""

import cv2
import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QGroupBox, QHBoxLayout, QLabel,
                             QPushButton, QSlider, QVBoxLayout)


class BrightnessContrastDialog(QDialog):
    """Adjust brightness and contrast like PSP."""

    adjustment_changed = pyqtSignal(int, int)  # brightness, contrast

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Brightness / Contrast")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Brightness
        bright_group = QGroupBox("Brightness")
        bright_layout = QVBoxLayout()

        self.bright_slider = QSlider(Qt.Orientation.Horizontal)
        self.bright_slider.setRange(-100, 100)
        self.bright_slider.setValue(0)
        self.bright_label = QLabel("0")

        bright_layout.addWidget(self.bright_slider)
        bright_layout.addWidget(self.bright_label)
        bright_group.setLayout(bright_layout)
        layout.addWidget(bright_group)

        # Contrast
        contrast_group = QGroupBox("Contrast")
        contrast_layout = QVBoxLayout()

        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_label = QLabel("0")

        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_label)
        contrast_group.setLayout(contrast_layout)
        layout.addWidget(contrast_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_reset = QPushButton("Reset")
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")

        btn_reset.clicked.connect(self.reset_values)
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        # Connect signals
        self.bright_slider.valueChanged.connect(
            lambda v: self.bright_label.setText(str(v))
        )
        self.contrast_slider.valueChanged.connect(
            lambda v: self.contrast_label.setText(str(v))
        )

        self.bright_slider.valueChanged.connect(self.emit_changes)
        self.contrast_slider.valueChanged.connect(self.emit_changes)

    def emit_changes(self):
        """Emit current values."""
        self.adjustment_changed.emit(
            self.bright_slider.value(),
            self.contrast_slider.value()
        )

    def reset_values(self):
        """Reset to defaults."""
        self.bright_slider.setValue(0)
        self.contrast_slider.setValue(0)

    def get_values(self):
        """Get brightness and contrast values."""
        return self.bright_slider.value(), self.contrast_slider.value()


class HueSaturationDialog(QDialog):
    """Adjust hue, saturation, lightness like PSP."""

    adjustment_changed = pyqtSignal(
        int, int, int)  # hue, saturation, lightness

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hue / Saturation / Lightness")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Hue
        hue_group = QGroupBox("Hue")
        hue_layout = QVBoxLayout()
        self.hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.hue_slider.setRange(-180, 180)
        self.hue_slider.setValue(0)
        self.hue_label = QLabel("0°")
        hue_layout.addWidget(self.hue_slider)
        hue_layout.addWidget(self.hue_label)
        hue_group.setLayout(hue_layout)
        layout.addWidget(hue_group)

        # Saturation
        sat_group = QGroupBox("Saturation")
        sat_layout = QVBoxLayout()
        self.sat_slider = QSlider(Qt.Orientation.Horizontal)
        self.sat_slider.setRange(-100, 100)
        self.sat_slider.setValue(0)
        self.sat_label = QLabel("0")
        sat_layout.addWidget(self.sat_slider)
        sat_layout.addWidget(self.sat_label)
        sat_group.setLayout(sat_layout)
        layout.addWidget(sat_group)

        # Lightness
        light_group = QGroupBox("Lightness")
        light_layout = QVBoxLayout()
        self.light_slider = QSlider(Qt.Orientation.Horizontal)
        self.light_slider.setRange(-100, 100)
        self.light_slider.setValue(0)
        self.light_label = QLabel("0")
        light_layout.addWidget(self.light_slider)
        light_layout.addWidget(self.light_label)
        light_group.setLayout(light_layout)
        layout.addWidget(light_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_reset = QPushButton("Reset")
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")

        btn_reset.clicked.connect(self.reset_values)
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        # Connect signals
        self.hue_slider.valueChanged.connect(
            lambda v: self.hue_label.setText(f"{v}°")
        )
        self.sat_slider.valueChanged.connect(
            lambda v: self.sat_label.setText(str(v))
        )
        self.light_slider.valueChanged.connect(
            lambda v: self.light_label.setText(str(v))
        )

    def reset_values(self):
        """Reset to defaults."""
        self.hue_slider.setValue(0)
        self.sat_slider.setValue(0)
        self.light_slider.setValue(0)

    def get_values(self):
        """Get HSL values."""
        return (
            self.hue_slider.value(),
            self.sat_slider.value(),
            self.light_slider.value()
        )


class ColorAdjustments:
    """Applies color adjustments to images."""

    @staticmethod
    def adjust_brightness_contrast(image, brightness=0, contrast=0):
        """
        Adjust brightness and contrast.

        Args:
            image: numpy array or QImage
            brightness: -100 to 100
            contrast: -100 to 100

        Returns:
            Adjusted image (same type as input)
        """
        # Convert to numpy if needed
        is_qimage = isinstance(image, QImage)
        img = qimage_to_numpy(image) if is_qimage else image.copy()

        # Apply brightness
        if brightness != 0:
            img = np.clip(
                img.astype(int) +
                brightness,
                0,
                255).astype(
                np.uint8)

        # Apply contrast
        if contrast != 0:
            factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
            img = np.clip(factor * (img.astype(int) - 128) +
                          128, 0, 255).astype(np.uint8)

        # Convert back if needed
        if is_qimage:
            return numpy_to_qimage(img)
        return img

    @staticmethod
    def adjust_hue_saturation(image, hue=0, saturation=0, lightness=0):
        """
        Adjust hue, saturation, lightness.

        Args:
            image: numpy array or QImage
            hue: -180 to 180 degrees
            saturation: -100 to 100
            lightness: -100 to 100

        Returns:
            Adjusted image (same type as input)
        """
        # Convert to numpy if needed
        is_qimage = isinstance(image, QImage)
        img = qimage_to_numpy(image) if is_qimage else image.copy()

        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(float)

        # Adjust hue
        if hue != 0:
            hsv[:, :, 0] = (hsv[:, :, 0] + hue) % 180

        # Adjust saturation
        if saturation != 0:
            hsv[:, :, 1] = np.clip(
                hsv[:, :, 1] * (1 + saturation / 100.0), 0, 255)

        # Adjust lightness (value in HSV)
        if lightness != 0:
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] + lightness, 0, 255)

        # Convert back to RGB
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

        # Convert back if needed
        if is_qimage:
            return numpy_to_qimage(result)
        return result


# Helper functions

def qimage_to_numpy(qimage):
    """Convert QImage to numpy array."""
    width = qimage.width()
    height = qimage.height()
    ptr = qimage.bits()
    ptr.setsize(qimage.sizeInBytes())
    arr = np.array(ptr).reshape(height, width, 4)
    return arr[:, :, :3].copy()  # RGB only


def numpy_to_qimage(arr):
    """Convert numpy array to QImage."""
    height, width = arr.shape[:2]
    if len(arr.shape) == 2:
        arr = np.stack([arr, arr, arr], axis=2)

    # Add alpha channel
    alpha = np.full((height, width, 1), 255, dtype=np.uint8)
    arr_rgba = np.concatenate([arr, alpha], axis=2)

    qimage = QImage(
        arr_rgba.data, width, height,
        arr_rgba.strides[0],
        QImage.Format.Format_RGBA8888
    )
    return qimage.copy()
