"""
Grid Settings Dialog for SJ-DAS.
Configure grid spacing and snap options.
"""
from PyQt6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QGroupBox,
                             QHBoxLayout, QLabel, QSpinBox, QVBoxLayout)


class GridSettingsDialog(QDialog):
    """Dialog for configuring grid and snap settings."""

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Grid & Snap Settings")
        self.setModal(True)
        self.setMinimumWidth(300)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Grid Settings Group
        grid_group = QGroupBox("Grid Settings")
        grid_layout = QVBoxLayout()

        # Grid Spacing
        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(QLabel("Grid Spacing:"))
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setRange(1, 100)
        self.spacing_spin.setValue(getattr(self.editor, 'grid_spacing', 8))
        self.spacing_spin.setSuffix(" px")
        spacing_layout.addWidget(self.spacing_spin)
        spacing_layout.addStretch()
        grid_layout.addLayout(spacing_layout)

        # Show Grid Checkbox
        self.show_grid_check = QCheckBox("Show Grid")
        self.show_grid_check.setChecked(
            getattr(self.editor, 'show_grid', True))
        grid_layout.addWidget(self.show_grid_check)

        grid_group.setLayout(grid_layout)
        layout.addWidget(grid_group)

        # Snap Settings Group
        snap_group = QGroupBox("Snap Settings")
        snap_layout = QVBoxLayout()

        # Snap to Grid
        self.snap_grid_check = QCheckBox("Snap to Grid")
        self.snap_grid_check.setChecked(
            getattr(self.editor, 'snap_to_grid', False))
        self.snap_grid_check.setToolTip(
            "Snap shapes and selections to grid points")
        snap_layout.addWidget(self.snap_grid_check)

        # Snap to Guides
        self.snap_guides_check = QCheckBox("Snap to Guides")
        self.snap_guides_check.setChecked(
            getattr(self.editor, 'snap_to_guides', False))
        self.snap_guides_check.setToolTip(
            "Snap to ruler guides (when implemented)")
        self.snap_guides_check.setEnabled(False)  # Future feature
        snap_layout.addWidget(self.snap_guides_check)

        snap_group.setLayout(snap_layout)
        layout.addWidget(snap_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_settings(self):
        """Return the configured settings."""
        return {
            'grid_spacing': self.spacing_spin.value(),
            'show_grid': self.show_grid_check.isChecked(),
            'snap_to_grid': self.snap_grid_check.isChecked(),
            'snap_to_guides': self.snap_guides_check.isChecked()
        }
