"""Card Sequence Editor Dialog.

Configure jacquard card lifting sequence for loom control.
"""

import logging

from PyQt6.QtWidgets import (QComboBox, QDialog, QFormLayout, QGroupBox,
                             QHBoxLayout, QLabel, QPushButton, QSpinBox,
                             QTextEdit, QVBoxLayout)

logger = logging.getLogger(__name__)


class CardSequenceDialog(QDialog):
    """
    Card sequence/details editor for jacquard loom control.

    Features:
    - Define card lifting sequence
    - Visualize repeat pattern
    - Export card data for loom
    """

    def __init__(self, hooks: int = 480, parent=None):
        super().__init__(parent)
        self.hooks = hooks
        self.setWindowTitle("Card Sequence / Details")
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

        self.lbl_hooks = QLabel(f"{self.hooks} hooks")
        specs_layout.addRow("Total Hooks:", self.lbl_hooks)

        # Card pattern type
        self.combo_pattern = QComboBox()
        self.combo_pattern.addItems([
            "Plain Weave (1/1)",
            "Twill 2/1",
            "Satin 5",
            "Custom Card Sequence"
        ])
        self.combo_pattern.currentTextChanged.connect(self._on_pattern_changed)
        specs_layout.addRow("Card Pattern:", self.combo_pattern)

        layout.addWidget(specs_group)

        # Card sequence details
        self.sequence_group = QGroupBox("Card Lifting Sequence")
        sequence_layout = QVBoxLayout(self.sequence_group)

        # Number of cards
        card_layout = QHBoxLayout()
        card_layout.addWidget(QLabel("Number of Cards:"))
        self.spin_cards = QSpinBox()
        self.spin_cards.setRange(1, 32)
        self.spin_cards.setValue(8)
        self.spin_cards.valueChanged.connect(self._update_preview)
        card_layout.addWidget(self.spin_cards)
        card_layout.addStretch()
        sequence_layout.addLayout(card_layout)

        # Sequence list
        sequence_layout.addWidget(
            QLabel("Lifting Sequence (comma-separated card numbers):"))
        self.txt_sequence = QTextEdit()
        self.txt_sequence.setPlaceholderText(
            "Example: 1,2,3,4,5,6,7,8 (repeat)")
        self.txt_sequence.setMaximumHeight(80)
        self.txt_sequence.textChanged.connect(self._update_preview)
        sequence_layout.addWidget(self.txt_sequence)

        # Auto-generate options
        auto_layout = QHBoxLayout()
        self.btn_auto_plain = QPushButton("Auto: Plain (1,2)")
        self.btn_auto_plain.clicked.connect(
            lambda: self._auto_generate_plain())
        auto_layout.addWidget(self.btn_auto_plain)

        self.btn_auto_twill = QPushButton("Auto: Twill (1,2,3,4)")
        self.btn_auto_twill.clicked.connect(
            lambda: self._auto_generate_twill())
        auto_layout.addWidget(self.btn_auto_twill)

        auto_layout.addStretch()
        sequence_layout.addLayout(auto_layout)

        layout.addWidget(self.sequence_group)

        # Preview
        preview_group = QGroupBox("Pattern Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.lbl_preview = QLabel("Preview will show repeat pattern...")
        self.lbl_preview.setWordWrap(True)
        preview_layout.addWidget(self.lbl_preview)

        layout.addWidget(preview_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_ok = QPushButton("Apply Card Sequence")
        btn_ok.setProperty("class", "primary")
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_ok)

        layout.addLayout(btn_layout)

    def _on_pattern_changed(self, pattern: str):
        """Handle pattern selection change."""
        if "Plain" in pattern:
            self._auto_generate_plain()
        elif "Twill" in pattern:
            self._auto_generate_twill()
        elif "Satin" in pattern:
            self._auto_generate_satin()

    def _auto_generate_plain(self):
        """Generate plain weave sequence (1/1)."""
        self.spin_cards.setValue(2)
        self.txt_sequence.setPlainText("1,2")
        logger.info("Auto-generated plain weave sequence")

    def _auto_generate_twill(self):
        """Generate twill weave sequence (2/1)."""
        self.spin_cards.setValue(3)
        self.txt_sequence.setPlainText("1,2,3")
        logger.info("Auto-generated twill weave sequence")

    def _auto_generate_satin(self):
        """Generate satin weave sequence."""
        self.spin_cards.setValue(5)
        self.txt_sequence.setPlainText("1,3,5,2,4")
        logger.info("Auto-generated satin weave sequence")

    def _update_preview(self):
        """Update pattern preview."""
        sequence_text = self.txt_sequence.toPlainText()
        if not sequence_text:
            return

        try:
            # Parse sequence
            sequence = [int(x.strip())
                        for x in sequence_text.split(',') if x.strip()]

            # Generate preview
            repeat_count = min(4, self.hooks // len(sequence))
            preview = "Pattern repeat: " + \
                " → ".join([str(x) for x in sequence])
            preview += f"\n\nRepeats {repeat_count}× across {self.hooks} hooks"
            preview += f"\n\nCards used: {self.spin_cards.value()}"

            self.lbl_preview.setText(preview)

        except ValueError:
            self.lbl_preview.setText(
                "Invalid sequence format. Use comma-separated numbers.")

    def get_card_sequence(self) -> dict:
        """
        Get configured card sequence.

        Returns:
            Dictionary with card pattern details
        """
        sequence_text = self.txt_sequence.toPlainText()

        try:
            sequence = [int(x.strip())
                        for x in sequence_text.split(',') if x.strip()]
        except BaseException:
            sequence = [1, 2]  # Default plain weave

        return {
            "pattern_type": self.combo_pattern.currentText(),
            "num_cards": self.spin_cards.value(),
            "lifting_sequence": sequence,
            "hooks": self.hooks
        }
