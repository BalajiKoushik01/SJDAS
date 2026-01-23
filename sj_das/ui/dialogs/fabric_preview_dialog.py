
import logging

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QImage, QPixmap
from PyQt6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QToolBar, QVBoxLayout,
                             QWidget)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import PrimaryPushButton

logger = logging.getLogger("SJ_DAS.FabricPreviewDialog")


class FabricPreviewDialog(QDialog):
    """
    Dialog to preview high-quality fabric simulation.
    Includes Zoom and Save controls.
    """

    def __init__(self, fabric_image: QImage, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fabric Reality Preview")
        self.resize(1000, 800)

        self.original_image = fabric_image
        self.current_zoom = 1.0

        self.init_ui()
        self.update_view()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- Toolbar ---
        toolbar = QWidget()
        toolbar.setStyleSheet(
            "background-color: #1E293B; border-bottom: 1px solid #334155;")
        tb_layout = QHBoxLayout(toolbar)

        lbl_title = QLabel("Virtual Loom Output (2.5D)")
        lbl_title.setStyleSheet(
            "color: white; font-weight: bold; font-size: 14px;")
        tb_layout.addWidget(lbl_title)

        tb_layout.addStretch()

        btn_zoom_out = QPushButton("-")
        btn_zoom_out.setFixedSize(32, 32)
        btn_zoom_out.clicked.connect(self.zoom_out)
        tb_layout.addWidget(btn_zoom_out)

        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setStyleSheet(
            "color: white; min-width: 50px; text-align: center;")
        tb_layout.addWidget(self.lbl_zoom)

        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setFixedSize(32, 32)
        btn_zoom_in.clicked.connect(self.zoom_in)
        tb_layout.addWidget(btn_zoom_in)

        tb_layout.addSpacing(20)

        btn_save = PrimaryPushButton("Save Image")
        btn_save.setIcon(FIF.SAVE)
        btn_save.clicked.connect(self.save_image)
        tb_layout.addWidget(btn_save)

        layout.addWidget(toolbar)

        # --- Canvas ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet(
            "background-color: #0F172A; border: none;")
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_label)

        layout.addWidget(self.scroll_area)

    def update_view(self):
        if self.original_image.isNull():
            return

        w = int(self.original_image.width() * self.current_zoom)
        h = int(self.original_image.height() * self.current_zoom)

        # Fast scaling for preview
        scaled = self.original_image.scaled(
            w, h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(QPixmap.fromImage(scaled))
        self.image_label.resize(w, h)

        self.lbl_zoom.setText(f"{int(self.current_zoom * 100)}%")

    def zoom_in(self):
        self.current_zoom = min(4.0, self.current_zoom + 0.25)
        self.update_view()

    def zoom_out(self):
        self.current_zoom = max(0.1, self.current_zoom - 0.25)
        self.update_view()

    def save_image(self):
        f, _ = QFileDialog.getSaveFileName(
            self, "Save Simulation", "", "PNG Images (*.png);;JPEG Images (*.jpg)")
        if f:
            self.original_image.save(f)
