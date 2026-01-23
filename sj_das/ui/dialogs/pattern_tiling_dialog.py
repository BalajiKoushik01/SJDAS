
import cv2
import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (QComboBox, QDialog, QFrame, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QSlider, QVBoxLayout)
from qfluentwidgets import ComboBox, PrimaryPushButton, PushButton, Slider


class PatternTilingDialog(QDialog):
    """
    Dialog for creating seamless repeats (Tile Patterns).
    Supports: Grid, Brick, Half-Drop.
    """

    def __init__(self, source_image: np.ndarray, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pattern Tiling Tool")
        self.resize(1000, 700)

        self.source_image = source_image
        self.result_image = None

        self._init_ui()
        self.update_preview()

    def _init_ui(self):
        # Main Layout
        layout = QHBoxLayout(self)

        # --- Left: Controls ---
        controls_panel = QFrame()
        controls_panel.setFixedWidth(300)
        controls_panel.setStyleSheet(
            "background-color: #f9f9f9; border-right: 1px solid #ddd;")

        ctrl_layout = QVBoxLayout(controls_panel)
        ctrl_layout.setSpacing(20)

        # Title
        title = QLabel("Tiling Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        ctrl_layout.addWidget(title)

        # 1. Type
        ctrl_layout.addWidget(QLabel("Repeat Type:"))
        self.combo_type = ComboBox()
        self.combo_type.addItems(["Grid (Simple)",
                                  "Brick (Horizontal Offset)",
                                  "Half-Drop (Vertical Offset)"])
        self.combo_type.currentTextChanged.connect(self.update_preview)
        ctrl_layout.addWidget(self.combo_type)

        # 2. Repeats
        ctrl_layout.addWidget(QLabel("Repeats (X by Y):"))
        self.combo_repeats = ComboBox()
        self.combo_repeats.addItems(["2x2", "3x3", "4x4", "5x5"])
        self.combo_repeats.setCurrentIndex(1)  # 3x3 default
        self.combo_repeats.currentTextChanged.connect(self.update_preview)
        ctrl_layout.addWidget(self.combo_repeats)

        # 3. Overlap / Offset
        ctrl_layout.addWidget(QLabel("Offset Amount (%):"))
        self.slider_offset = Slider(Qt.Orientation.Horizontal)
        self.slider_offset.setRange(0, 100)
        self.slider_offset.setValue(50)  # Standard half-drop
        self.slider_offset.valueChanged.connect(self.update_preview)
        ctrl_layout.addWidget(self.slider_offset)

        ctrl_layout.addStretch()

        # Buttons
        self.btn_apply = PrimaryPushButton("Apply to Canvas")
        self.btn_apply.clicked.connect(self.accept)
        ctrl_layout.addWidget(self.btn_apply)

        self.btn_cancel = PushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        ctrl_layout.addWidget(self.btn_cancel)

        layout.addWidget(controls_panel)

        # --- Right: Preview ---
        preview_area = QScrollArea()
        preview_area.setWidgetResizable(True)
        preview_area.setStyleSheet("background-color: #333;")

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_area.setWidget(self.preview_label)

        layout.addWidget(preview_area)

    def update_preview(self):
        """Generate tiled pattern based on settings."""
        if self.source_image is None:
            return

        mode = self.combo_type.currentText()
        repeats_str = self.combo_repeats.currentText()
        repeats = int(repeats_str[0])  # '3x3' -> 3
        offset_pct = self.slider_offset.value() / 100.0

        h, w = self.source_image.shape[:2]

        # Calculate Canvas Size
        full_w = w * repeats
        full_h = h * repeats

        # Create Canvas
        canvas = np.zeros((full_h, full_w, 3), dtype=np.uint8)

        # Tiling Logic
        for y in range(repeats):
            for x in range(repeats):
                # Calculate Offset
                dx = 0
                dy = 0

                if "Brick" in mode:
                    # Offset X on odd rows
                    if y % 2 == 1:
                        dx = int(w * offset_pct)
                elif "Half-Drop" in mode:
                    # Offset Y on odd cols
                    if x % 2 == 1:
                        dy = int(h * offset_pct)

                # Base Position
                px = (x * w) + dx
                py = (y * h) + dy

                # Wrap around logic for offset
                # (Simplified: Just paste and crop overflow)

                # Paste (Safe slice)
                y1, y2 = py, py + h
                x1, x2 = px, px + w

                # Handling bounds (simple repeating wrapping is complex, let's
                # just clip for preview)
                if y1 >= full_h or x1 >= full_w:
                    continue

                # Adjust source/dest dimensions
                h_paste = min(h, full_h - y1)
                w_paste = min(w, full_w - x1)

                if h_paste <= 0 or w_paste <= 0:
                    continue

                canvas[y1:y1 + h_paste, x1:x1 +
                       w_paste] = self.source_image[:h_paste, :w_paste]

                # TODO: Handle wrap-around parts for true seamless check
                # For this MVP, we just show the layout logic

        self.result_image = canvas

        # Convert to QImage for display
        img_h, img_w, _ = canvas.shape
        bytes_per_line = 3 * img_w
        rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        qimg = QImage(
            rgb.data,
            img_w,
            img_h,
            bytes_per_line,
            QImage.Format.Format_RGB888)

        # Scale for preview if too huge
        if img_w > 1000 or img_h > 1000:
            qimg = qimg.scaled(
                1000,
                1000,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)

        self.preview_label.setPixmap(QPixmap.fromImage(qimg))

    def get_result(self) -> np.ndarray:
        return self.result_image
