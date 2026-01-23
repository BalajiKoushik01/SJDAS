"""
Channel Split Dialog.
UI for splitting design into Jari/Meena channels.
"""

import cv2
import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (QDialog, QFileDialog, QFrame, QHBoxLayout, QLabel,
                             QMessageBox, QPushButton, QScrollArea, QSlider,
                             QVBoxLayout)
from qfluentwidgets import CaptionLabel, Slider, StrongBodyLabel

from sj_das.weaves.channel_splitter import ChannelSplitter


class ChannelSplitDialog(QDialog):
    def __init__(self, image: np.ndarray, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manufacturing Channel Splitter")
        self.resize(1000, 700)

        self.original_image = image
        # Resize for preview performance
        h, w = image.shape[:2]
        self.scale = 1.0
        if w > 1000:
            self.scale = 1000 / w
            image = cv2.resize(image, (0, 0), fx=self.scale, fy=self.scale)
        self.preview_image = image

        self.splitter = ChannelSplitter()
        self.masks = {}

        self.init_ui()
        self.update_preview()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # Left: Controls
        controls = QFrame()
        controls.setFixedWidth(320)
        ctrl_layout = QVBoxLayout(controls)
        ctrl_layout.setSpacing(10)

        ctrl_layout.addWidget(StrongBodyLabel("Jari Detection (Gold)"))

        # Hue Range
        self.lbl_hue = CaptionLabel("Hue Tolerance")
        ctrl_layout.addWidget(self.lbl_hue)
        self.slider_hue = Slider(Qt.Orientation.Horizontal)
        self.slider_hue.setRange(5, 60)
        self.slider_hue.setValue(30)
        self.slider_hue.valueChanged.connect(self.schedule_update)
        ctrl_layout.addWidget(self.slider_hue)

        # Saturation Min
        self.lbl_sat = CaptionLabel("Min Saturation")
        ctrl_layout.addWidget(self.lbl_sat)
        self.slider_sat = Slider(Qt.Orientation.Horizontal)
        self.slider_sat.setRange(0, 255)
        self.slider_sat.setValue(100)
        self.slider_sat.valueChanged.connect(self.schedule_update)
        ctrl_layout.addWidget(self.slider_sat)

        # Value Min
        self.lbl_val = CaptionLabel("Min Brightness")
        ctrl_layout.addWidget(self.lbl_val)
        self.slider_val = Slider(Qt.Orientation.Horizontal)
        self.slider_val.setRange(0, 255)
        self.slider_val.setValue(100)
        self.slider_val.valueChanged.connect(self.schedule_update)
        ctrl_layout.addWidget(self.slider_val)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        ctrl_layout.addWidget(line)

        # Loom Settings
        ctrl_layout.addWidget(StrongBodyLabel("Loom Config"))

        # Hooks Input
        from qfluentwidgets import SpinBox
        self.spin_hooks = SpinBox()
        self.spin_hooks.setRange(400, 9600)
        self.spin_hooks.setValue(2400)  # Standard Kanchipuram
        self.spin_hooks.setPrefix("Hooks: ")
        ctrl_layout.addWidget(self.spin_hooks)

        ctrl_layout.addStretch()

        # Actions
        from qfluentwidgets import PrimaryPushButton, PushButton

        btn_mask_export = PushButton("Export Masks (PNG)")
        btn_mask_export.clicked.connect(self.export_masks)
        ctrl_layout.addWidget(btn_mask_export)

        btn_loom_export = PrimaryPushButton("🏭 Export for Loom")
        # Primary button already has nice style in Fluent
        btn_loom_export.clicked.connect(self.export_for_loom)
        ctrl_layout.addWidget(btn_loom_export)

        layout.addWidget(controls)

        # Right: Previews
        preview_area = QScrollArea()
        preview_widget = QFrame()
        self.p_layout = QVBoxLayout(preview_widget)

        self.lbl_jari = QLabel()
        self.lbl_meena = QLabel()
        self.lbl_body = QLabel()

        self._add_preview_section("Jari (Gold Mask)", self.lbl_jari)
        self._add_preview_section("Meena (Silk Mask)", self.lbl_meena)
        self._add_preview_section("Body (Background)", self.lbl_body)

        preview_area.setWidget(preview_widget)
        preview_area.setWidgetResizable(True)
        layout.addWidget(preview_area)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.update_preview)

    def _add_preview_section(self, title, label):
        self.p_layout.addWidget(StrongBodyLabel(title))
        label.setScaledContents(True)
        label.setFixedSize(600, 200)
        label.setStyleSheet("border: 1px solid #333; background: #000;")
        self.p_layout.addWidget(label)

    def schedule_update(self):
        self.timer.start(200)  # Debounce

    def update_preview(self):
        # Update Thresholds
        h_tol = self.slider_hue.value()
        s_min = self.slider_sat.value()
        v_min = self.slider_val.value()

        # Yellow/Gold is around Hue 30 (0-180 scale in OpenCV)
        lower = np.array([max(0, 25 - h_tol // 2), s_min, v_min])
        upper = np.array([min(180, 25 + h_tol // 2), 255, 255])

        self.splitter.set_jari_range(lower, upper)

        # Process
        self.masks = self.splitter.split_channels(self.preview_image)

        # Display
        self._show_mask(self.lbl_jari, self.masks.get("jari"))
        self._show_mask(self.lbl_meena, self.masks.get("meena"))
        self._show_mask(self.lbl_body, self.masks.get("body"))

    def _show_mask(self, label, mask):
        if mask is None:
            return

        # Convert to RGB for display (White on Black)
        display = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

        h, w, ch = display.shape
        bytes_per_line = ch * w
        qimg = QImage(
            display.data,
            w,
            h,
            bytes_per_line,
            QImage.Format.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(qimg))

    def export_masks(self):
        self._export_process(False)

    def export_for_loom(self):
        self._export_process(True)

    def _export_process(self, is_loom_format: bool):
        # Update Thresholds
        h_tol = self.slider_hue.value()
        s_min = self.slider_sat.value()
        v_min = self.slider_val.value()
        lower = np.array([max(0, 25 - h_tol // 2), s_min, v_min])
        upper = np.array([min(180, 25 + h_tol // 2), 255, 255])

        self.splitter.set_jari_range(lower, upper)

        full_masks = self.splitter.split_channels(self.original_image)

        if is_loom_format:
            # LOOM EXPORT
            from sj_das.weaves.loom_exporter import LoomExporter
            exporter = LoomExporter()

            path, _ = QFileDialog.getSaveFileName(
                self, "Export Loom File", "design_export.bmp", "BMP Image (*.bmp)")
            if not path:
                return

            hooks = self.spin_hooks.value()

            # Export Jari Channel (Primary)
            # Ideally we export both. For now export Jari.
            exporter.export_bmp(full_masks["jari"], path, hooks)

            # Export Meena separately if needed
            if np.any(full_masks["meena"]):
                base = path.replace(".bmp", "")
                exporter.export_bmp(
                    full_masks["meena"], f"{base}_meena.bmp", hooks)

            QMessageBox.information(
                self,
                "Loom Export",
                f"Files saved to {path}\n(Resized to {hooks} hooks)")

        else:
            # MASK EXPORT
            path, _ = QFileDialog.getSaveFileName(
                self, "Export Channels", "channels_export", "PNG Images (*.png)")
            if not path:
                return

            base = path.replace(".png", "")
            for name, mask in full_masks.items():
                cv2.imwrite(f"{base}_{name}.png", mask)

            QMessageBox.information(
                self, "Export Complete", f"Saved masks to {base}_*.png")

        self.accept()
