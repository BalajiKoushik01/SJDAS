from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (QColorDialog, QHBoxLayout, QListWidget,
                             QListWidgetItem, QPushButton, QVBoxLayout,
                             QWidget)


class YarnPaletteWidget(QWidget):
    """
    Widget to manage yarn colors (palette).
    """
    color_selected = pyqtSignal(int, QColor)  # index, color
    palette_changed = pyqtSignal(list)  # list of colors

    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = []  # List of QColor
        self.textile_service = None
        self.init_ui()

    def set_service(self, service):
        """Inject TextileService"""
        self.textile_service = service
        # Future: Load yarns from service
        # self.colors = service.get_project_yarns()
        # self._update_list()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # List of colors
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(32, 32))
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self._edit_color)
        layout.addWidget(self.list_widget)

        # Buttons
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Add")
        self.btn_add.clicked.connect(self._add_color)
        btn_layout.addWidget(self.btn_add)

        self.btn_remove = QPushButton("Remove")
        self.btn_remove.clicked.connect(self._remove_color)
        btn_layout.addWidget(self.btn_remove)

        layout.addLayout(btn_layout)

        # Initial Palette (Default)
        self.set_palette([
            QColor(255, 0, 0),   # Red
            QColor(0, 255, 0),   # Green
            QColor(0, 0, 255),   # Blue
            QColor(255, 255, 0),  # Yellow
            QColor(0, 255, 255),  # Cyan
            QColor(255, 0, 255)  # Magenta
        ])

    def set_palette(self, colors):
        self.colors = colors
        self._update_list()
        self.palette_changed.emit(self.colors)

    def _update_list(self):
        self.list_widget.clear()
        for i, color in enumerate(self.colors):
            item = QListWidgetItem(f"Yarn {i+1}")

            # Create icon
            pixmap = QPixmap(32, 32)
            pixmap.fill(color)
            item.setIcon(QIcon(pixmap))

            self.list_widget.addItem(item)

    def _add_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.colors.append(color)
            self._update_list()
            self.palette_changed.emit(self.colors)

    def _remove_color(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.colors.pop(row)
            self._update_list()
            self.palette_changed.emit(self.colors)

    def _edit_color(self, item):
        row = self.list_widget.row(item)
        if row >= 0:
            color = QColorDialog.getColor(self.colors[row])
            if color.isValid():
                self.colors[row] = color
                self._update_list()
                self.palette_changed.emit(self.colors)

    def _on_selection_changed(self, row):
        if row >= 0 and row < len(self.colors):
            # 1-based index for mask usually
            self.color_selected.emit(row + 1, self.colors[row])
