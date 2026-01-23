import cv2
import numpy as np
from PyQt6.QtGui import QColor, QImage
from PyQt6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                             QSpinBox, QVBoxLayout)


class GeometricGenerator:
    """
    Module for generating geometric textile patterns.
    Integrated via Composition.
    """

    def __init__(self, editor):
        self.editor = editor

    def show_generator_dialog(self):
        """Shows the main generator UI"""
        dialog = GeometricDialog(self.editor)
        if dialog.exec():
            params = dialog.get_params()
            self.generate_pattern(params)

    def generate_pattern(self, params):
        """Dispatch based on type"""
        ptype = params['type']

        if ptype == 'Stripes':
            self._draw_stripes(params)
        elif ptype == 'Checks':
            self._draw_checks(params)
        elif ptype == 'Dots':
            self._draw_dots(params)

    def _draw_stripes(self, params):
        w, h = self.editor.canvas_width, self.editor.canvas_height
        img = np.zeros((h, w, 3), dtype=np.uint8)
        # Background color
        bg = params['bg_color']
        img[:] = (bg.blue(), bg.green(), bg.red())

        fg = params['fg_color']
        fg_tuple = (fg.blue(), fg.green(), fg.red())

        thickness = params['size']
        spacing = params['spacing']
        vertical = params['orientation'] == 'Vertical'

        step = thickness + spacing

        if vertical:
            for x in range(0, w, step):
                cv2.rectangle(img, (x, 0), (x + thickness, h), fg_tuple, -1)
        else:
            for y in range(0, h, step):
                cv2.rectangle(img, (0, y), (w, y + thickness), fg_tuple, -1)

        self._update_editor(img)

    def _draw_checks(self, params):
        w, h = self.editor.canvas_width, self.editor.canvas_height
        img = np.zeros((h, w, 3), dtype=np.uint8)
        bg = params['bg_color']
        img[:] = (bg.blue(), bg.green(), bg.red())

        fg = params['fg_color']
        fg_tuple = (fg.blue(), fg.green(), fg.red())

        size = params['size']  # Check size

        for y in range(0, h, size * 2):
            for x in range(0, w, size * 2):
                # Draw checkerboard pattern
                cv2.rectangle(img, (x, y), (x + size, y + size), fg_tuple, -1)
                cv2.rectangle(img, (x + size, y + size),
                              (x + size * 2, y + size * 2), fg_tuple, -1)

        self._update_editor(img)

    def _draw_dots(self, params):
        w, h = self.editor.canvas_width, self.editor.canvas_height
        img = np.zeros((h, w, 3), dtype=np.uint8)
        bg = params['bg_color']
        img[:] = (bg.blue(), bg.green(), bg.red())

        fg = params['fg_color']
        fg_tuple = (fg.blue(), fg.green(), fg.red())

        radius = params['size']
        spacing = params['spacing']

        step = (radius * 2) + spacing

        for y in range(radius, h, step):
            for x in range(radius, w, step):
                cv2.circle(img, (x, y), radius, fg_tuple, -1)

        self._update_editor(img)

    def _update_editor(self, cv_img):
        # Convert BGR to RGB
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line,
                      QImage.Format.Format_RGB888).copy()

        self.editor.set_image(qimg)
        self.editor.mask_updated.emit()


class GeometricDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pattern Generator")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.cmb_type = QComboBox()
        self.cmb_type.addItems(['Stripes', 'Checks', 'Dots'])
        form.addRow("Pattern Type:", self.cmb_type)

        self.spin_size = QSpinBox()
        self.spin_size.setRange(1, 500)
        self.spin_size.setValue(20)
        form.addRow("Size / Thickness:", self.spin_size)

        self.spin_spacing = QSpinBox()
        self.spin_spacing.setRange(0, 500)
        self.spin_spacing.setValue(20)
        form.addRow("Spacing:", self.spin_spacing)

        self.cmb_orient = QComboBox()
        self.cmb_orient.addItems(['Vertical', 'Horizontal'])
        form.addRow("Orientation (Stripes):", self.cmb_orient)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Default colors
        self.bg_color = QColor(255, 255, 255)
        self.fg_color = QColor(0, 0, 0)

    def get_params(self):
        return {
            'type': self.cmb_type.currentText(),
            'size': self.spin_size.value(),
            'spacing': self.spin_spacing.value(),
            'orientation': self.cmb_orient.currentText(),
            'bg_color': self.bg_color,
            'fg_color': self.fg_color
        }
