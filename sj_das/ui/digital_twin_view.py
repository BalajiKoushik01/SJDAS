import time
import logging

try:
    import moderngl
    _MODERNGL_AVAILABLE = True
except Exception as e:
    logging.warning(f"DigitalTwin: moderngl not available: {e}")
    moderngl = None
    _MODERNGL_AVAILABLE = False

from PyQt6.QtCore import Qt
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QMessageBox,
                             QPushButton, QSlider, QSpinBox, QVBoxLayout, QWidget)

try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None

try:
    from sj_das.core.renderer import FabricRenderer
except Exception as e:
    logging.warning(f"DigitalTwin: FabricRenderer not available: {e}")
    FabricRenderer = None


class DigitalTwinWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.renderer = None
        self.start_time = time.time()
        self.image_path = None

    def initializeGL(self):
        try:
            self.ctx = moderngl.create_context()
            self.renderer = FabricRenderer(self.ctx)
            if self.image_path:
                self.renderer.update_texture(self.image_path)
        except Exception as e:
            print(f"OpenGL Initialization Failed: {e}")
            self.renderer = None

    def paintGL(self):
        if not self.renderer:
            return

        now = time.time()
        self.renderer.render(
            self.width(), self.height(), time=(
                now - self.start_time) * 0.5)
        self.update()  # Request next frame

    def set_image(self, path):
        self.image_path = path
        if self.renderer:
            self.renderer.update_texture(path)


class DigitalTwinView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)

        # 3D View
        self.gl_widget = DigitalTwinWidget()
        self.layout.addWidget(self.gl_widget, stretch=3)

        # Controls
        self.controls = QWidget()
        self.controls.setFixedWidth(250)
        control_layout = QVBoxLayout(self.controls)

        control_layout.addWidget(QLabel("<h2>Digital Twin Controls</h2>"))

        btn_load = QPushButton("Load Texture")
        btn_load.clicked.connect(self.load_texture)
        control_layout.addWidget(btn_load)

        control_layout.addWidget(QLabel("Metallic"))
        self.slider_metallic = QSlider(Qt.Orientation.Horizontal)
        control_layout.addWidget(self.slider_metallic)

        control_layout.addWidget(QLabel("Roughness"))
        self.slider_roughness = QSlider(Qt.Orientation.Horizontal)
        control_layout.addWidget(self.slider_roughness)

        control_layout.addStretch()

        # --- Analytics Section (New for Twin+) ---
        from PyQt6.QtWidgets import QGroupBox

        grp_analytics = QGroupBox("Fabric Analytics & Cost")
        analytics_layout = QVBoxLayout()

        btn_cost = QPushButton("Calculate Yarn Cost")
        btn_cost.clicked.connect(self.calculate_cost)
        analytics_layout.addWidget(btn_cost)

        self.lbl_cost_result = QLabel("Not calculated")
        self.lbl_cost_result.setWordWrap(True)
        self.lbl_cost_result.setStyleSheet("color: #aaa; font-size: 11px;")
        analytics_layout.addWidget(self.lbl_cost_result)

        # Price Input
        lbl_price = QLabel("Avg Yarn Price (₹/kg):")
        self.spin_price = QSpinBox()
        self.spin_price.setRange(100, 50000)
        self.spin_price.setValue(1200)  # Silk default
        self.spin_price.setSuffix(" ₹")
        analytics_layout.addWidget(lbl_price)
        analytics_layout.addWidget(self.spin_price)

        grp_analytics.setLayout(analytics_layout)
        control_layout.insertWidget(
            control_layout.count() - 1,
            grp_analytics)  # Insert before stretch

        self.layout.addWidget(self.controls)

    def load_texture(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Texture", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.gl_widget.set_image(file_name)
            self.current_image_path = file_name
            self.lbl_cost_result.setText("Image loaded. Ready to calc.")

    def calculate_cost(self):
        """Twin+ Feature: Detailed Cost Estimation"""
        if not hasattr(
                self, 'current_image_path') or not self.current_image_path:
            QMessageBox.warning(
                self, "No Image", "Please load a texture/design first.")
            return

        try:
            img = cv2.imread(self.current_image_path)
            if img is None:
                return

            h, w, c = img.shape
            total_pixels = h * w
            pixels = img.reshape(-1, 3)
            # Find unique colors (indices)
            unique_colors, counts = np.unique(
                pixels, axis=0, return_counts=True)

            report = "<b>Yarn Consumption Report:</b><br>"

            # Sort by frequency
            sorted_indices = np.argsort(counts)[::-1]

            for i in range(len(sorted_indices)):
                idx = sorted_indices[i]
                count = counts[idx]
                percent = (count / total_pixels) * 100

                # Estimate Weight (assuming 500g saree)
                weight_kg = (percent / 100) * 0.5

                # Cost Calculation
                unit_price = self.spin_price.value()
                cost = weight_kg * unit_price

                report += f"• Yarn {i+1}: <b>{percent:.1f}%</b> ({weight_kg*1000:.0f}g) -> <b>₹{cost:.2f}</b><br>"

            report += f"<br><b>Total Est. Yarn Cost: ₹{(0.5 * self.spin_price.value()):.2f}</b> (based on 500g Saree)"
            # Note: This total assumes uniform price. For competitive edge, ideally per-yarn price,
            # but average is standard for quick Est.

            self.lbl_cost_result.setText(report)
            QMessageBox.information(
                self,
                "Cost Analysis",
                f"Analysis Complete.\nUnique Yarns: {len(unique_colors)}\nEst. Cost: ₹{(0.5 * self.spin_price.value()):.2f}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
