from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QComboBox, QDialog, QFrame, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QVBoxLayout, QWidget)


class WeaveMapperDialog(QDialog):
    """
    Dialog to assign Weave Structures to Design Colors.
    Competitor Feature: Mapping Table.
    """

    def __init__(self, unique_colors, weave_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Assign Weaves to Colors")
        self.resize(500, 600)

        self.colors = unique_colors  # List of (B, G, R) tuples
        self.wm = weave_manager
        self.mapping = {}  # {(B,G,R): "WeaveName"}

        layout = QVBoxLayout(self)

        # Header
        layout.addWidget(QLabel("Map each yarn color to a weave structure:"))

        # Scroll Area for Color List
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        form_layout = QVBoxLayout(container)

        self.combos = []
        weaves = self.wm.list_weaves()

        for i, color_bgr in enumerate(self.colors):
            row = QHBoxLayout()

            # Color Swatch
            swatch = QLabel()
            swatch.setFixedSize(40, 40)
            # BGR -> RGB for Qt
            c = QColor(int(color_bgr[2]), int(color_bgr[1]), int(color_bgr[0]))
            swatch.setStyleSheet(
                f"background-color: {c.name()}; border: 1px solid #555;")
            row.addWidget(swatch)

            # Info
            info = QLabel(f"Color {i+1}\n{c.name()}")
            row.addWidget(info)

            # ComboBox
            combo = QComboBox()
            combo.addItems(weaves)
            # Default: Cycle through weaves
            combo.setCurrentIndex(i % len(weaves))
            row.addWidget(combo)

            self.combos.append((color_bgr, combo))
            form_layout.addLayout(row)

            # Separator
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            form_layout.addWidget(line)

        container.setLayout(form_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Buttons
        btns = QHBoxLayout()
        ok_btn = QPushButton("Simulate Fabric")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btns.addWidget(cancel_btn)
        btns.addWidget(ok_btn)
        layout.addLayout(btns)

    def get_mapping(self):
        result = {}
        for color, combo in self.combos:
            result[tuple(color)] = combo.currentText()
        return result
