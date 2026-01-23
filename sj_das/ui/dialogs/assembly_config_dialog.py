"""Assembly Configuration Dialog for Multi-Component Saree Design.

Handles Border|Body|Border assembly with Khali (repeats) and Locking (overlap).
Based on dataset analysis requirements.
"""

import logging

import cv2
from PyQt6.QtWidgets import (QComboBox, QDialog, QFileDialog, QFormLayout,
                             QGroupBox, QHBoxLayout, QLabel, QMessageBox,
                             QPushButton, QSpinBox, QVBoxLayout)

logger = logging.getLogger(__name__)


class AssemblyConfigDialog(QDialog):
    """
    Professional assembly configuration for jacquard sarees.

    Features from dataset:
    - Multi-component: Border|Body|Border
    - Khali repeats: 3-32x
    - Locking overlap
    - Total dimension calculation
    - Broket pattern support
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.components = {}  # Store loaded components
        self.setWindowTitle("Saree Assembly Configuration")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)

        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        # Component loading section
        comp_group = QGroupBox("Load Components")
        comp_layout = QVBoxLayout(comp_group)

        # Border
        border_layout = QHBoxLayout()
        border_layout.addWidget(QLabel("Border BMP:"))
        self.lbl_border = QLabel("Not loaded")
        self.lbl_border.setStyleSheet("color: #888;")
        border_layout.addWidget(self.lbl_border)
        border_layout.addStretch()
        btn_load_border = QPushButton("Load Border")
        btn_load_border.clicked.connect(lambda: self._load_component('border'))
        border_layout.addWidget(btn_load_border)
        comp_layout.addLayout(border_layout)

        # Body
        body_layout = QHBoxLayout()
        body_layout.addWidget(QLabel("Body BMP:"))
        self.lbl_body = QLabel("Not loaded")
        self.lbl_body.setStyleSheet("color: #888;")
        body_layout.addWidget(self.lbl_body)
        body_layout.addStretch()
        btn_load_body = QPushButton("Load Body")
        btn_load_body.clicked.connect(lambda: self._load_component('body'))
        body_layout.addWidget(btn_load_body)
        comp_layout.addLayout(body_layout)

        # Pallu (optional)
        pallu_layout = QHBoxLayout()
        pallu_layout.addWidget(QLabel("Pallu BMP (optional):"))
        self.lbl_pallu = QLabel("Not loaded")
        self.lbl_pallu.setStyleSheet("color: #888;")
        pallu_layout.addWidget(self.lbl_pallu)
        pallu_layout.addStretch()
        btn_load_pallu = QPushButton("Load Pallu")
        btn_load_pallu.clicked.connect(lambda: self._load_component('pallu'))
        pallu_layout.addWidget(btn_load_pallu)
        comp_layout.addLayout(pallu_layout)

        layout.addWidget(comp_group)

        # Assembly configuration
        config_group = QGroupBox("Assembly Configuration")
        config_layout = QFormLayout(config_group)

        # Assembly type
        self.combo_assembly = QComboBox()
        self.combo_assembly.addItems([
            "Border | Body | Border",
            "Body Only",
            "Body | Pallu",
            "Border | Body | Pallu | Body | Border"
        ])
        config_layout.addRow("Assembly Type:", self.combo_assembly)

        # Khali (repeats) - CRITICAL from dataset
        self.spin_khali = QSpinBox()
        self.spin_khali.setRange(1, 32)
        self.spin_khali.setValue(8)  # Default 8 (common)
        self.spin_khali.setSuffix(" repeats")
        self.spin_khali.setToolTip("Pattern repetitions (3-32 from dataset)")
        self.spin_khali.valueChanged.connect(self._update_calculations)
        config_layout.addRow("Khali (Repeats):", self.spin_khali)

        # Locking (overlap)
        self.spin_locking = QSpinBox()
        self.spin_locking.setRange(0, 100)
        self.spin_locking.setValue(0)
        self.spin_locking.setSuffix(" pixels")
        self.spin_locking.setToolTip(
            "Overlap between repeats for seamless join")
        self.spin_locking.valueChanged.connect(self._update_calculations)
        config_layout.addRow("Locking (Overlap):", self.spin_locking)

        # Reed
        self.spin_reed = QSpinBox()
        self.spin_reed.setRange(80, 120)
        self.spin_reed.setValue(100)
        self.spin_reed.setSuffix(" reed")
        config_layout.addRow("Reed Count:", self.spin_reed)

        # Pattern type
        self.combo_pattern = QComboBox()
        self.combo_pattern.addItems([
            "Standard Weave",
            "Broket (Brocade)",
            "Jeri (Metallic/Gold)",
            "Broket Jeri"
        ])
        config_layout.addRow("Pattern Type:", self.combo_pattern)

        layout.addWidget(config_group)

        # Calculations display
        calc_group = QGroupBox("Calculated Dimensions")
        calc_layout = QFormLayout(calc_group)

        self.lbl_total_hooks = QLabel("0")
        self.lbl_total_hooks.setStyleSheet(
            "font-weight: bold; color: #0078d4;")
        calc_layout.addRow("Total Hooks:", self.lbl_total_hooks)

        self.lbl_total_picks = QLabel("0")
        self.lbl_total_picks.setStyleSheet(
            "font-weight: bold; color: #0078d4;")
        calc_layout.addRow("Total Picks:", self.lbl_total_picks)

        self.lbl_file_size = QLabel("0 KB")
        calc_layout.addRow("Est. File Size:", self.lbl_file_size)

        layout.addWidget(calc_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_assemble = QPushButton("Assemble & Export")
        btn_assemble.setProperty("class", "primary")
        btn_assemble.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(btn_assemble)

        layout.addLayout(btn_layout)

    def _load_component(self, component_type: str):
        """Load a component BMP file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            f"Load {component_type.capitalize()} BMP",
            "",
            "BMP Files (*.bmp);;All Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not path:
            return

        try:
            # Load image
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is None:
                raise ValueError("Failed to load image")

            # Store component
            self.components[component_type] = {
                'path': path,
                'image': img,
                'width': img.shape[1],
                'height': img.shape[0]
            }

            # Update label
            label = getattr(self, f'lbl_{component_type}')
            label.setText(
                f"{img.shape[1]}×{img.shape[0]} ({path.split('/')[-1]})")
            label.setStyleSheet("color: #16a085; font-weight: bold;")

            # Update calculations
            self._update_calculations()

            logger.info(
                f"Loaded {component_type}: {img.shape[1]}×{img.shape[0]}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load {component_type}:\n{str(e)}")

    def _update_calculations(self):
        """Update calculated dimensions."""
        assembly_type = self.combo_assembly.currentText()
        khali = self.spin_khali.value()
        locking = self.spin_locking.value()

        total_hooks = 0
        total_picks = 0

        # Calculate based on assembly type
        if "Border | Body | Border" in assembly_type:
            if 'border' in self.components and 'body' in self.components:
                border_w = self.components['border']['width']
                body_w = self.components['body']['width']

                # Formula: (Border×2 + Body) × Khali
                base_width = (border_w * 2) + body_w
                total_hooks = base_width * khali - (locking * (khali - 1))

                # Height from body
                total_picks = self.components['body']['height']

        elif "Body Only" in assembly_type and 'body' in self.components:
            total_hooks = self.components['body']['width'] * \
                khali - (locking * (khali - 1))
            total_picks = self.components['body']['height']

        # Update labels
        self.lbl_total_hooks.setText(f"{total_hooks} hooks")
        self.lbl_total_picks.setText(f"{total_picks} picks")

        # Estimate file size (BMP = width × height × 3 + header)
        if total_hooks > 0 and total_picks > 0:
            file_size = (total_hooks * total_picks * 3 + 1024) / 1024
            self.lbl_file_size.setText(f"{file_size:.1f} KB")

    def _validate_and_accept(self):
        """Validate configuration and accept."""
        if not self.components:
            QMessageBox.warning(
                self,
                "No Components",
                "Please load at least one component")
            return

        assembly_type = self.combo_assembly.currentText()

        # Validate required components
        if "Border | Body | Border" in assembly_type:
            if 'border' not in self.components or 'body' not in self.components:
                QMessageBox.warning(self, "Missing Components",
                                    "Border|Body|Border requires both Border and Body components")
                return

        self.accept()

    def get_assembly_config(self) -> dict:
        """
        Get complete assembly configuration.

        Returns:
            Dictionary with assembly settings
        """
        return {
            'assembly_type': self.combo_assembly.currentText(),
            'khali': self.spin_khali.value(),
            'locking': self.spin_locking.value(),
            'reed': self.spin_reed.value(),
            'pattern_type': self.combo_pattern.currentText(),
            'components': self.components
        }
