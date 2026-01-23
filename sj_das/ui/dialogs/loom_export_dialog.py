"""Loom Export Dialog with Weave Mapping.

Professional export dialog for generating loom-ready BMP files with
complete metadata embedding and weave pattern assignments.
"""

import logging

from PyQt6.QtWidgets import (QComboBox, QDialog, QFormLayout, QGroupBox,
                             QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QSpinBox, QTableWidget,
                             QVBoxLayout)

logger = logging.getLogger(__name__)


class LoomExportDialog(QDialog):
    """
    Professional export dialog for loom-ready BMP generation.

    Features:
    - Weave pattern assignment per color
    - Metadata configuration
    - Float safety validation
    - Export preview and summary
    """

    def __init__(self, image_colors: list, parent=None):
        """
        Initialize export dialog.

        Args:
            image_colors: List of colors in the design (QColor objects)
            parent: Parent widget
        """
        super().__init__(parent)
        self.image_colors = image_colors
        self.weave_map = {}

        self.setWindowTitle("Export for Loom")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        # Loom specifications
        specs_group = QGroupBox("Loom Specifications")
        specs_layout = QFormLayout(specs_group)

        self.spin_hooks = QSpinBox()
        self.spin_hooks.setRange(100, 4800)
        self.spin_hooks.setValue(480)
        self.spin_hooks.setSuffix(" hooks")
        specs_layout.addRow("Hooks:", self.spin_hooks)

        self.spin_reed = QSpinBox()
        self.spin_reed.setRange(50, 150)
        self.spin_reed.setValue(100)
        self.spin_reed.setSuffix(" reed")
        specs_layout.addRow("Reed:", self.spin_reed)

        self.combo_component = QComboBox()
        self.combo_component.addItems(
            ["Body", "Border", "Pallu", "Full Saree"])
        specs_layout.addRow("Component:", self.combo_component)

        layout.addWidget(specs_group)

        # Weave pattern mapping
        weave_group = QGroupBox("Weave Pattern Mapping")
        weave_layout = QVBoxLayout(weave_group)

        info_label = QLabel("Assign weave patterns to each color:")
        info_label.setStyleSheet("color: #888; font-style: italic;")
        weave_layout.addWidget(info_label)

        # Table for color-to-weave mapping
        self.table_weaves = QTableWidget()
        self.table_weaves.setColumnCount(3)
        self.table_weaves.setHorizontalHeaderLabels(
            ["Color", "Yarn Name", "Weave Pattern"])
        self.table_weaves.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table_weaves.setRowCount(len(self.image_colors))

        # Available weave patterns
        weave_patterns = [
            "Plain 1/1",
            "Twill 2/1 S",
            "Twill 2/1 Z",
            "Twill 2/2",
            "Satin 5",
            "Satin 8",
            "Basket 2/2",
            "Custom"
        ]

        for i, color in enumerate(self.image_colors):
            # Color preview
            color_label = QLabel()
            color_label.setFixedSize(40, 20)
            color_label.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #666;")
            self.table_weaves.setCellWidget(i, 0, color_label)

            # Yarn name input
            yarn_input = QLineEdit(f"Yarn {i+1}")
            self.table_weaves.setCellWidget(i, 1, yarn_input)

            # Weave pattern combo
            weave_combo = QComboBox()
            weave_combo.addItems(weave_patterns)
            if i == 0:
                # Background usually plain
                weave_combo.setCurrentText("Plain 1/1")
            else:
                # Default for colored areas
                weave_combo.setCurrentText("Satin 5")
            self.table_weaves.setCellWidget(i, 2, weave_combo)

        weave_layout.addWidget(self.table_weaves)

        layout.addWidget(weave_group)

        # Optional metadata
        meta_group = QGroupBox("Additional Information (Optional)")
        meta_layout = QFormLayout(meta_group)

        self.edit_designer = QLineEdit()
        self.edit_designer.setPlaceholderText("Designer name")
        meta_layout.addRow("Designer:", self.edit_designer)

        self.edit_notes = QLineEdit()
        self.edit_notes.setPlaceholderText("Design notes or description")
        meta_layout.addRow("Notes:", self.edit_notes)

        layout.addWidget(meta_group)

        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QFormLayout(options_group)

        self.combo_format = QComboBox()
        self.combo_format.addItems(
            ["8-bit BMP (Multi-color)", "1-bit BMP (Black/White)"])
        options_layout.addRow("Format:", self.combo_format)

        self.check_validate = QCheckBox("Run float safety check before export")
        self.check_validate.setChecked(True)
        options_layout.addRow("Validation:", self.check_validate)

        # New: Auto-Locking
        self.check_autofix = QCheckBox(
            "Auto-Fix Floats (Insert Binding Points)")
        # Default off to avoid unexpected edits
        self.check_autofix.setChecked(False)
        options_layout.addRow("Auto-Locking:", self.check_autofix)

        self.spin_max_float = QSpinBox()
        self.spin_max_float.setRange(5, 100)
        self.spin_max_float.setValue(20)  # Standard 20px
        self.spin_max_float.setSuffix(" px")
        options_layout.addRow("Max Float Length:", self.spin_max_float)

        layout.addWidget(options_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_export = QPushButton("Export BMP")
        btn_export.setProperty("class", "primary")
        btn_export.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(btn_export)

        layout.addLayout(btn_layout)

    def _validate_and_accept(self):
        """Validate settings and accept dialog."""
        # Build weave map
        self.weave_map = {}
        for i in range(self.table_weaves.rowCount()):
            yarn_widget = self.table_weaves.cellWidget(i, 1)
            weave_widget = self.table_weaves.cellWidget(i, 2)

            if yarn_widget and weave_widget:
                yarn_name = yarn_widget.text()
                weave_pattern = weave_widget.currentText()
                self.weave_map[i] = {
                    "yarn": yarn_name,
                    "weave": weave_pattern,
                    "color": self.image_colors[i].name()
                }

        # Validate
        if not self.weave_map:
            QMessageBox.warning(
                self, "Invalid", "Please assign weave patterns")
            return

        self.accept()

    def get_export_config(self) -> dict:
        """
        Get complete export configuration.

        Returns:
            Dictionary with all export settings
        """
        return {
            "hooks": self.spin_hooks.value(),
            "reed": self.spin_reed.value(),
            "component": self.combo_component.currentText(),
            "weave_map": self.weave_map,
            "format": "8bit" if "8-bit" in self.combo_format.currentText() else "1bit",
            "validate_float": self.check_validate.isChecked(),
            "auto_fix_floats": self.check_autofix.isChecked(),
            "max_float": self.spin_max_float.value(),
            "designer": self.edit_designer.text() or "Unknown",
            "notes": self.edit_notes.text() or ""
        }
