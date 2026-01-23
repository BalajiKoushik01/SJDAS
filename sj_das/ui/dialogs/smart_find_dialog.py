
import logging

import cv2
import numpy as np
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QPushButton,
                             QSplitter, QVBoxLayout)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar, LineEdit, PrimaryPushButton

logger = logging.getLogger("SJ_DAS.SmartFindDialog")


class SmartFindDialog(QDialog):
    """
    Dialog for Zero-Shot Object Detection (Owl-ViT).
    Allows user to type "flower", "border" and select results.
    """

    def __init__(self, image: np.ndarray, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Find (Owl-ViT)")
        self.resize(1000, 700)

        self.original_image = image  # BGR
        self.detections = []  # List of dicts

        self.init_ui()
        self.update_preview()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- Search Bar ---
        search_layout = QHBoxLayout()
        self.txt_query = LineEdit()
        self.txt_query.setPlaceholderText(
            "Describe objects to find (e.g., 'red flower', 'bird motif')")
        self.txt_query.returnPressed.connect(self.start_search)
        search_layout.addWidget(self.txt_query)

        btn_search = PrimaryPushButton("Find Objects")
        btn_search.setIcon(FIF.SEARCH)
        btn_search.clicked.connect(self.start_search)
        search_layout.addWidget(btn_search)

        layout.addLayout(search_layout)

        # --- Splitter (Preview | Results) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Image Preview
        self.lbl_preview = QLabel()
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setStyleSheet(
            "background-color: #0F172A; border: 1px solid #334155;")
        splitter.addWidget(self.lbl_preview)

        # Right: Results List
        right_panel = QDialog()  # Container
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.list_results = QListWidget()
        self.list_results.itemChanged.connect(self.on_item_check_changed)
        right_layout.addWidget(self.list_results)

        btn_select_all = QPushButton("Select All")
        btn_select_all.clicked.connect(self.select_all)
        right_layout.addWidget(btn_select_all)

        splitter.addWidget(right_panel)
        splitter.setSizes([700, 300])

        layout.addWidget(splitter)

        # --- Bottom ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_apply = PrimaryPushButton("Create Selection Mask")
        self.btn_apply.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_apply)

        layout.addLayout(btn_layout)

    def start_search(self):
        query = self.txt_query.text().strip()
        if not query:
            return

        # Call AIService
        from sj_das.core.services.ai_service import AIService
        ai = AIService.instance()

        # Connect signals
        try:
            ai.search_completed.disconnect()
        except BaseException:
            pass

        ai.search_completed.connect(self.on_search_results)
        ai.search_object(self.original_image, query)

        # Disable UI
        self.txt_query.setEnabled(False)
        self.lbl_preview.setText("Searching... (Loading AI Model)")

    def on_search_results(self, detections):
        self.txt_query.setEnabled(True)
        self.detections = detections

        self.list_results.clear()

        if not detections:
            InfoBar.warning(
                title="No Objects Found",
                content="Try a different description or lower threshold.",
                parent=self
            )
            self.update_preview()
            return

        for i, det in enumerate(detections):
            score = det['score']
            label = f"{det['label']} ({int(score*100)}%)"
            item = QListWidgetItem(label)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, i)  # Store index
            self.list_results.addItem(item)

        self.update_preview()

    def update_preview(self):
        # Draw boxes on image
        img_h, img_w, _ = self.original_image.shape

        # Convert to QImage for drawing
        rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, img_w, img_h, 3 * img_w,
                      QImage.Format.Format_RGB888).copy()

        painter = QPainter(qimg)
        pen = QPen(QColor("#10B981"), 3)  # Emerald Green

        # Draw selected boxes
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)

        count = self.list_results.count()
        for i in range(count):
            item = self.list_results.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                idx = item.data(Qt.ItemDataRole.UserRole)
                det = self.detections[idx]
                x1, y1, x2, y2 = det['box']

                painter.setPen(pen)
                painter.drawRect(x1, y1, x2 - x1, y2 - y1)

                # Draw Label Background
                # painter.fillRect(x1, y1-20, 100, 20, QColor(0,0,0,150))
                # painter.setPen(Qt.GlobalColor.white)
                # painter.drawText(x1+5, y1-5, f"{int(det['score']*100)}%")

        painter.end()

        # Scale for display
        scaled = qimg.scaled(
            self.lbl_preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.lbl_preview.setPixmap(QPixmap.fromImage(scaled))

    def on_item_check_changed(self, item):
        self.update_preview()

    def select_all(self):
        for i in range(self.list_results.count()):
            self.list_results.item(i).setCheckState(Qt.CheckState.Checked)
        self.update_preview()

    def get_selection_mask(self) -> np.ndarray:
        """Returns binary mask of selected boxes."""
        h, w, _ = self.original_image.shape
        mask = np.zeros((h, w), dtype=np.uint8)

        count = self.list_results.count()
        for i in range(count):
            item = self.list_results.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                idx = item.data(Qt.ItemDataRole.UserRole)
                x1, y1, x2, y2 = self.detections[idx]['box']
                # Draw filled rectangle on mask
                cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)

        return mask
