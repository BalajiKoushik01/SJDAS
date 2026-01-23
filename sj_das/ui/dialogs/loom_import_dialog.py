"""Enhanced Loom Import Dialog.

Professional dialog for importing images with precise loom specifications.
Auto-detects parameters from filename and allows manual configuration.
"""

import logging
import re
from pathlib import Path

from PyQt6.QtWidgets import (QComboBox, QDialog, QFileDialog, QFormLayout,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QSpinBox, QVBoxLayout)

logger = logging.getLogger(__name__)


class LoomImportDialog(QDialog):
    """
    Professional import dialog with loom specifications.

    Features:
    - Auto-detection from filename
    - Manual override controls
    - Live preview with dimensions
    - Validation before accept
    """

    def __init__(self, image_path: str = None, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle("Import for Loom - Specifications")
        self.setModal(True)
        self.setMinimumWidth(500)

        self._init_ui()

        if image_path:
            self._auto_detect_specs()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        # File selection
        file_group = QGroupBox("Image File")
        file_layout = QHBoxLayout(file_group)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #888;")
        file_layout.addWidget(self.file_label)

        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_file)
        file_layout.addWidget(btn_browse)

        layout.addWidget(file_group)

        # Loom specifications
        specs_group = QGroupBox("Loom Specifications")
        specs_layout = QFormLayout(specs_group)

        # Hooks (Width)
        self.spin_hooks = QSpinBox()
        self.spin_hooks.setRange(100, 4800)
        self.spin_hooks.setValue(480)
        self.spin_hooks.setSuffix(" hooks")
        self.spin_hooks.setToolTip("Total warp threads (width)")
        specs_layout.addRow("Hooks (Width):", self.spin_hooks)

        # Reed count
        self.spin_reed = QSpinBox()
        self.spin_reed.setRange(50, 150)
        self.spin_reed.setValue(100)
        self.spin_reed.setSuffix(" reed")
        self.spin_reed.setToolTip("Threads per inch density")
        specs_layout.addRow("Reed Count:", self.spin_reed)

        # Component type
        self.combo_component = QComboBox()
        self.combo_component.addItems(
            ["Body", "Border", "Pallu", "Full Saree"])
        self.combo_component.setToolTip("Design component type")
        specs_layout.addRow("Component:", self.combo_component)

        # Color count (for quantization)
        self.spin_colors = QSpinBox()
        self.spin_colors.setRange(2, 32)
        # Default 3 yarns (typical for most designs)
        self.spin_colors.setValue(3)
        self.spin_colors.setSuffix(" yarns")
        self.spin_colors.setToolTip(
            "Maximum yarn colors (2-3 typical, 4-8 advanced)")
        specs_layout.addRow("Colors:", self.spin_colors)

        layout.addWidget(specs_group)

        # Preview info
        preview_group = QGroupBox("Processing Preview")
        preview_layout = QFormLayout(preview_group)

        self.lbl_original = QLabel("—")
        preview_layout.addRow("Original Size:", self.lbl_original)

        self.lbl_target = QLabel("—")
        preview_layout.addRow("Target Size:", self.lbl_target)

        self.lbl_scaling = QLabel("—")
        preview_layout.addRow("Scaling:", self.lbl_scaling)

        layout.addWidget(preview_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_import = QPushButton("Import")
        btn_import.setProperty("class", "primary")
        btn_import.clicked.connect(self.accept)
        btn_layout.addWidget(btn_import)

        layout.addLayout(btn_layout)

        # Connect signals
        self.spin_hooks.valueChanged.connect(self._update_preview)

    def _browse_file(self):
        """Open file browser."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )

        if filename:
            self.image_path = filename
            self.file_label.setText(Path(filename).name)
            self.file_label.setStyleSheet("color: #FFF;")
            self._auto_detect_specs()
            self._update_preview()

    def _auto_detect_specs(self):
        """Auto-detect specifications from filename."""
        if not self.image_path:
            return

        filename = Path(self.image_path).stem

        # Pattern: extract hooks, reed, component
        # Example: "3 960 Body 106 Reed"

        # Find hooks (3-4 digits)
        hooks_match = re.search(
            r'\b(4[0-9]{2}|[5-9][0-9]{2}|[1-3][0-9]{3}|4[0-7][0-9]{2}|48[0-7][0-9])\b',
            filename)
        if hooks_match:
            hooks = int(hooks_match.group(1))
            if 100 <= hooks <= 4800:
                self.spin_hooks.setValue(hooks)
                logger.info(f"Auto-detected hooks: {hooks}")

        # Find reed (2-3 digits after "Reed")
        reed_match = re.search(r'(\d{2,3})\s*Reed', filename, re.IGNORECASE)
        if reed_match:
            reed = int(reed_match.group(1))
            if 50 <= reed <= 150:
                self.spin_reed.setValue(reed)
                logger.info(f"Auto-detected reed: {reed}")

        # Detect component type
        filename_lower = filename.lower()
        if 'body' in filename_lower:
            self.combo_component.setCurrentText("Body")
        elif 'border' in filename_lower or 'boder' in filename_lower:
            self.combo_component.setCurrentText("Border")
        elif 'pallu' in filename_lower:
            self.combo_component.setCurrentText("Pallu")

    def _update_preview(self):
        """Update preview information."""
        if not self.image_path:
            return

        try:
            from PIL import Image
            img = Image.open(self.image_path)
            orig_w, orig_h = img.size

            self.lbl_original.setText(f"{orig_w} × {orig_h} pixels")

            target_w = self.spin_hooks.value()
            # Maintain aspect ratio
            target_h = int(orig_h * (target_w / orig_w))

            self.lbl_target.setText(f"{target_w} × {target_h} pixels")

            scale_factor = target_w / orig_w
            if scale_factor > 1:
                self.lbl_scaling.setText(f"Upscale {scale_factor:.2f}×")
                self.lbl_scaling.setStyleSheet("color: #FFA500;")  # Orange
            elif scale_factor < 1:
                self.lbl_scaling.setText(f"Downscale {scale_factor:.2f}×")
                self.lbl_scaling.setStyleSheet("color: #4CAF50;")  # Green
            else:
                self.lbl_scaling.setText("No scaling (1:1)")
                self.lbl_scaling.setStyleSheet("color: #2196F3;")  # Blue

        except Exception as e:
            logger.error(f"Failed to update preview: {e}")

    def get_specifications(self) -> dict:
        """
        Get configured loom specifications.

        Returns:
            Dictionary with hooks, reed, component, colors, and path
        """
        return {
            "image_path": self.image_path,
            "hooks": self.spin_hooks.value(),
            "reed": self.spin_reed.value(),
            "component": self.combo_component.currentText(),
            "colors": self.spin_colors.value(),
        }
