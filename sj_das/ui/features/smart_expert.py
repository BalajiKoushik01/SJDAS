from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QComboBox, QDialog, QFormLayout, QHBoxLayout,
                             QLabel, QMessageBox, QPushButton, QTextEdit,
                             QVBoxLayout)

# Import Knowledge Base
from sj_das.ai.textile_knowledge import LOOM_SPECIFICATIONS, suggest_colors


class SmartExpert:
    """
    Expert System for Textile Design Consultation.

    Features:
    - **Knowledge Base Integration**: Suggests color palettes and loom specifications based on real textile data.
    - **Contextual Advice**: Tailored recommendations for 'Occasion' and 'Regional Style'.
    - **Fabric Dimensions**: Auto-configures canvas size for standard saree production.

    Usage:
    >>> expert = SmartExpert(editor_instance)
    >>> expert.show_dialog()
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = ExpertDialog(self.editor)
        if dialog.exec():
            # Apply recommended settings if user agreed
            w, h = dialog.get_recommended_dims()
            if w and h:
                # Resize canvas (ask user?)
                self._resize_canvas(w, h)
                pass  # Just showing info for now, maybe auto-resize is too aggressive

    def _resize_canvas(self, w, h):
        # Create new white canvas
        new_img = QImage(w, h, QImage.Format.Format_RGB888)
        new_img.fill(Qt.GlobalColor.white)
        self.editor.set_image(new_img)
        self.editor.mask_updated.emit()
        QMessageBox.information(
            None,
            "Expert Assistant",
            f"Canvas set to standard saree dimensions: {w}x{h} px (scaled).")


class ExpertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Textile Consultant")
        self.resize(500, 600)
        self.recommended_w = 0
        self.recommended_h = 0
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 1. Inputs
        form = QFormLayout()

        self.cmb_occasion = QComboBox()
        self.cmb_occasion.addItems(["-- Select Occasion --",
                                    "Bridal Wedding",
                                    "Festive Celebration",
                                    "Casual / Office",
                                    "Temple Visit"])
        self.cmb_occasion.currentIndexChanged.connect(self.update_advice)
        form.addRow("Occasion:", self.cmb_occasion)

        self.cmb_region = QComboBox()
        self.cmb_region.addItems(["-- Select Region --",
                                  "Kanchipuram (Tamil Nadu)",
                                  "Banarasi (North)",
                                  "Paithani (Maharashtra)",
                                  "Mysore Silk (Karnataka)"])
        self.cmb_region.currentIndexChanged.connect(self.update_advice)
        form.addRow("Regional Style:", self.cmb_region)

        layout.addLayout(form)

        # 2. Output: Palette
        layout.addWidget(QLabel("<b>Recommended Color Palette:</b>"))
        self.palette_layout = QHBoxLayout()
        # Placeholders
        self.palette_layout.addWidget(
            QLabel("<i>Select parameters to see suggestions</i>"))
        layout.addLayout(self.palette_layout)

        # 3. Output: Looms
        layout.addWidget(QLabel("<b>Loom Specifications:</b>"))
        self.lbl_loom = QLabel("-")
        self.lbl_loom.setWordWrap(True)
        layout.addWidget(self.lbl_loom)

        # 4. Output: Tips
        layout.addWidget(QLabel("<b>Design Guidelines:</b>"))
        self.txt_tips = QTextEdit()
        self.txt_tips.setReadOnly(True)
        layout.addWidget(self.txt_tips)

        # 5. Actions
        btn_apply = QPushButton("Apply Recommended Canvas Size")
        btn_apply.clicked.connect(self.accept)  # Closes and lets parent handle
        layout.addWidget(btn_apply)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)

    def update_advice(self):
        occ = self.cmb_occasion.currentText()
        reg = self.cmb_region.currentText()

        if "--" in occ and "--" in reg:
            return

        # 1. Get Colors
        colors = suggest_colors(occ if "--" not in occ else "Casual")

        # Clear layout
        while self.palette_layout.count():
            item = self.palette_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for c_name in colors:
            # simple mock mapping of name to hex
            hex_c = self._name_to_hex(c_name) if isinstance(
                c_name, str) else self._tuple_to_hex(c_name)

            lbl = QLabel()
            lbl.setFixedSize(50, 50)
            lbl.setStyleSheet(
                f"background-color: {hex_c}; border: 1px solid #777;")
            lbl.setToolTip(str(c_name))
            self.palette_layout.addWidget(lbl)

        self.palette_layout.addStretch()

        # 2. Loom Specs
        specs = LOOM_SPECIFICATIONS["Jacquard"]
        w_cm = specs["dimensions"]["width_cm"]
        # Convert cm to px (approx 10px per cm for view)
        self.recommended_w = int(w_cm[1] * 10)
        self.recommended_h = int(550 * 10)  # 5.5m -> 550cm

        hooks = specs["hook_ranges"]["standard"][0]
        if "Bridal" in occ:
            hooks = specs["hook_ranges"]["premium"][0]

        self.lbl_loom.setText(
            f"Recommended Hooks: {hooks}+\nStandard Width: {w_cm} cm\nProduction Time: {LOOM_SPECIFICATIONS['production_estimates'].get('medium_complexity', '?')}")

        # 3. Tips
        tips = []
        if "Kanchipuram" in reg:
            tips.append("• Use heavy silk and contrast borders.")
            tips.append("• Korvai technique recommended for distinct borders.")
            tips.append("• Traditional motifs: Temple, Peacock, Rudraksha.")
        elif "Banarasi" in reg:
            tips.append("• Mughal inspired florals (Kalga, Bel).")
            tips.append("• Continuous zari brocade work.")

        if "Bridal" in occ:
            tips.append("• Ensure high contrast between body and pallu.")
            tips.append("• Use Gold Zari liberally.")

        self.txt_tips.setText("\n".join(tips))

    def _name_to_hex(self, name):
        # Simplified map
        m = {
            "Red": "#FF0000", "Gold": "#FFD700", "Green": "#008000",
            "Maroon": "#800000", "Pink": "#FFC0CB", "Orange": "#FFA500",
            "Purple": "#800080", "Blue": "#0000FF", "White": "#FFFFFF",
            "Black": "#000000", "Silver": "#C0C0C0", "Peach": "#FFDAB9",
            "Cream": "#FFFDD0", "Royal Blue": "#4169E1", "Pastels": "#FDFD96"
        }
        return m.get(name, "#888888")

    def _tuple_to_hex(self, t):
        # Tuple might be (Name, Name) pair
        if isinstance(t, tuple):
            return self._name_to_hex(t[0])  # Just show first color of pair
        return "#888888"

    def get_recommended_dims(self):
        return self.recommended_w, self.recommended_h
