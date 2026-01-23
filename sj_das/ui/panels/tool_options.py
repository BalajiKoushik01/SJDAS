from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel,
                             QPushButton, QSpinBox, QWidget)


class ToolOptionsBar(QWidget):
    """
    Dynamic Tool Options Bar (PSP Style).
    Updates controls based on the active tool.
    """

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(15)
        self.setFixedHeight(40)
        self.setObjectName("options_bar")
        self.setStyleSheet("background-color: #333; color: white;")

        # Initial State
        self.set_tool(1)  # Brush

    def clear(self):
        """Clear all widgets."""
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            if w:
                w.setParent(None)

    def set_tool(self, tool_id):
        """Rebuild UI for tool."""
        self.clear()

        # Common: Tool Name Label
        name = "Tool"
        if tool_id == 1:
            name = "Brush Tool"  # Brush
        elif tool_id == 2:
            name = "Eraser"
        elif tool_id == 9:
            name = "Magic Wand"
        elif tool_id == 12:
            name = "Airbrush"
        elif tool_id == 13:
            name = "Clone Stamp"
        elif tool_id == 14:
            name = "Smudge"
        elif tool_id == 8:
            name = "Rect Select"

        lbl = QLabel(f"<b>{name}</b>")
        lbl.setStyleSheet("color: #aaa;")
        self.layout.addWidget(lbl)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet("color: #555;")
        self.layout.addWidget(line)

        # Dynamic Controls
        if tool_id in [1, 2, 12, 13, 14]:  # Brush-like
            self._add_brush_controls(tool_id)
        elif tool_id == 9:  # Wand
            self._add_wand_controls()
        elif tool_id == 3:  # Fill
            self._add_fill_controls()

        self.layout.addStretch()

    def _add_brush_controls(self, tool_id):
        # Size
        self.layout.addWidget(QLabel("Size:"))
        s_spin = QSpinBox()
        s_spin.setRange(1, 200)
        s_spin.setValue(self.editor.brush_size)
        s_spin.valueChanged.connect(
            lambda v: setattr(
                self.editor, 'brush_size', v))
        self.layout.addWidget(s_spin)

        # Opacity (General for Brush/Airbrush/Clone)
        self.layout.addWidget(QLabel("Opacity:"))
        o_spin = QSpinBox()
        o_spin.setRange(1, 100)
        # Handle attribute check safely
        val = getattr(self.editor, 'brush_opacity', 100)
        o_spin.setValue(val)
        o_spin.setSuffix("%")
        o_spin.valueChanged.connect(
            lambda v: setattr(
                self.editor, 'brush_opacity', v))
        self.layout.addWidget(o_spin)

        # Hardness (Brush specific)
        if tool_id in [1, 2]:  # Brush/Eraser
            self.layout.addWidget(QLabel("Hardness:"))
            h_spin = QSpinBox()
            h_spin.setRange(0, 100)
            val = getattr(self.editor, 'brush_hardness', 100)
            h_spin.setValue(val)
            h_spin.setSuffix("%")
            h_spin.valueChanged.connect(
                lambda v: setattr(
                    self.editor, 'brush_hardness', v))
            self.layout.addWidget(h_spin)

        # Flow (Brush specific)
        if tool_id in [1, 12]:  # Brush/Airbrush
            self.layout.addWidget(QLabel("Flow:"))
            f_spin = QSpinBox()
            f_spin.setRange(1, 100)
            val = getattr(self.editor, 'brush_flow', 100)
            f_spin.setValue(val)
            f_spin.setSuffix("%")
            f_spin.valueChanged.connect(
                lambda v: setattr(
                    self.editor, 'brush_flow', v))
            self.layout.addWidget(f_spin)

        # Hack for Clone Stamp Aligned
        if tool_id == 13:
            chk = QCheckBox("Aligned")
            chk.setChecked(True)
            self.layout.addWidget(chk)

        # Phase 11: Symmetry Controls
        # Available for Brush, Eraser, Pencil (Airbrush?)
        if tool_id in [1, 2, 12]:
            vline = QFrame()
            vline.setFrameShape(QFrame.Shape.VLine)
            vline.setStyleSheet("color: #555;")
            self.layout.addWidget(vline)

            self.layout.addWidget(QLabel("Symmetry:"))
            sym_combo = QComboBox()
            sym_combo.addItems(
                ["None", "Horizontal", "Vertical", "Quad", "Radial"])

            # Sync with current state
            if hasattr(self.editor, 'symmetry'):
                current_mode = self.editor.symmetry.mode.name
                # Map enum name to index?
                # Enum: NONE, HORIZONTAL...
                # Title case for UI: None, Horizontal...
                index = sym_combo.findText(current_mode.capitalize())
                if index >= 0:
                    sym_combo.setCurrentIndex(index)

                sym_combo.currentTextChanged.connect(
                    lambda t: self.editor.symmetry.set_mode(t))

            self.layout.addWidget(sym_combo)

    def _add_wand_controls(self):
        self.layout.addWidget(QLabel("Tolerance:"))
        t_spin = QSpinBox()
        t_spin.setRange(0, 255)
        t_spin.setValue(self.editor.wand_tolerance)
        t_spin.valueChanged.connect(
            lambda v: setattr(
                self.editor, 'wand_tolerance', v))
        self.layout.addWidget(t_spin)

        chk_ai = QCheckBox("✨ AI Smart Select (Ctrl)")
        chk_ai.setChecked(True)
        chk_ai.setToolTip("Use GrabCut AI for object selection")
        self.layout.addWidget(chk_ai)

    def _add_fill_controls(self):
        """Add controls for Fill/Bucket tool."""
        # Fill Type Selector
        self.layout.addWidget(QLabel("Fill Type:"))
        fill_combo = QComboBox()
        fill_combo.addItems(["Solid Color", "Pattern"])
        fill_combo.currentIndexChanged.connect(self._on_fill_type_changed)
        self.layout.addWidget(fill_combo)

        # Define Pattern Button
        self.pattern_btn = QPushButton("Define Pattern")
        self.pattern_btn.setToolTip("Capture current selection as pattern")
        self.pattern_btn.clicked.connect(self._define_pattern)
        self.pattern_btn.setEnabled(False)  # Enable when selection exists
        self.layout.addWidget(self.pattern_btn)

        # Pattern Preview (Small Label)
        self.pattern_preview = QLabel("No Pattern")
        self.pattern_preview.setStyleSheet(
            "border: 1px solid #555; padding: 2px;")
        self.pattern_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pattern_preview.setFixedHeight(30)
        self.layout.addWidget(self.pattern_preview)

    def _on_fill_type_changed(self, index):
        """Handle fill type change."""
        # Get the active Fill tool instance
        # We need to set a property on it
        # The tool is created fresh each click in mousePressEvent
        # So we store state on the EDITOR instead
        use_pattern = (index == 1)  # 1 = Pattern
        self.editor.fill_use_pattern = use_pattern

    def _define_pattern(self):
        """Capture selection as pattern."""
        success = self.editor.define_pattern()
        if success:
            # Update Preview
            if self.editor.active_pattern is not None:
                h, w = self.editor.active_pattern.shape[:2]
                self.pattern_preview.setText(f"Pattern: {w}x{h}px")
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select an area first.")
