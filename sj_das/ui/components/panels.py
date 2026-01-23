from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QPushButton, QVBoxLayout,
                             QWidget)


class HistoryPanel(QWidget):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.init_ui()

        # Connect to Undo Stack
        if self.editor.undo_stack:
            self.editor.undo_stack.indexChanged.connect(self.refresh_list)
            self.refresh_list()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        layout.addWidget(QLabel("History Actions"))

        # List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            "background: transparent; border: 1px solid #3E3E42;")
        layout.addWidget(self.list_widget)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_undo = QPushButton("Undo")
        btn_undo.clicked.connect(self.editor.undo_stack.undo)
        btn_redo = QPushButton("Redo")
        btn_redo.clicked.connect(self.editor.undo_stack.redo)
        btn_layout.addWidget(btn_undo)
        btn_layout.addWidget(btn_redo)
        layout.addLayout(btn_layout)

    def refresh_list(self):
        self.list_widget.clear()
        stack = self.editor.undo_stack
        count = stack.count()
        idx = stack.index()

        for i in range(count):
            cmd = stack.command(i)
            name = cmd.text()
            item = QListWidgetItem(f"{i+1}. {name}")
            if i == idx - 1:
                item.setBackground(QColor("#3E3E42"))  # Active
            self.list_widget.addItem(item)


class PalettePanel(QWidget):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Presets
        self.combo = QComboBox()
        self.combo.addItems(["Default Saree", "Pastel", "Neon", "Grayscale"])
        layout.addWidget(QLabel("Preset:"))
        layout.addWidget(self.combo)

        # Swatches (Grid)
        # Simplified as buttons for now
        self.grid = QVBoxLayout()
        self.refresh_swatches()
        layout.addLayout(self.grid)

        layout.addStretch()

    def refresh_swatches(self):
        # Clear
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        palette = [
            "#800000", "#FFD700", "#008000", "#FF007F",
            "#FFFFFF", "#000000", "#0000FF", "#FFA500"
        ]

        row = QHBoxLayout()
        for i, color in enumerate(palette):
            btn = QPushButton()
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(
                f"background-color: {color}; border: 1px solid gray;")
            btn.clicked.connect(lambda _, c=color: self.set_color(c))
            row.addWidget(btn)

            if (i + 1) % 4 == 0:
                self.grid.addLayout(row)
                row = QHBoxLayout()
        if row.count() > 0:
            self.grid.addLayout(row)

    def set_color(self, color_hex):
        self.editor.set_brush_color(QColor(color_hex))
