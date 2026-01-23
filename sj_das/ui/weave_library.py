import numpy as np
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QIcon, QImage, QPainter, QPixmap
from PyQt6.QtWidgets import (QLabel, QListWidget, QListWidgetItem, QPushButton,
                             QVBoxLayout, QWidget)


class WeaveLibraryWidget(QWidget):
    """
    A widget to display and select standard textile weave structures.
    """
    weave_selected = pyqtSignal(object, str)  # Emits (pattern_array, name)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.textile_service = None
        self.init_ui()

    def set_service(self, service):
        self.textile_service = service
        self.populate_weaves()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        lbl = QLabel("Standard Weaves")
        lbl.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(lbl)

        # Actions
        btn_layout = QVBoxLayout()
        btn_load = QPushButton("Load Custom...")
        btn_load.setToolTip("Load custom weave from BMP/PNG")
        btn_load.clicked.connect(self.load_custom_weave)
        btn_layout.addWidget(btn_load)

        btn_apply = QPushButton("🖌 Apply to Selection")
        btn_apply.setToolTip(
            "Apply selected weave to current selection on canvas")
        btn_apply.clicked.connect(self.apply_to_selection)
        btn_layout.addWidget(btn_apply)

        btn_split = QPushButton("🏭 Split Channels (Jari/Meena)")
        btn_split.setToolTip("Separate design into manufacturing channels")
        btn_split.clicked.connect(self.open_channel_split_dialog)
        btn_split.setStyleSheet(
            "background-color: #4F46E5; color: white; font-weight: bold;")
        btn_layout.addWidget(btn_split)

        layout.addLayout(btn_layout)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(32, 32))
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

        # Generate and populate standard weaves
        self.populate_weaves()

    def open_channel_split_dialog(self):
        # Lazy import to avoid circular deps
        from sj_das.ui.dialogs.channel_split_dialog import ChannelSplitDialog

        # We need the current image to split.
        # This widget is created by PanelFactory, which has access to 'view'.
        # But WeaveLibraryWidget doesn't know about 'view' or 'editor' directly yet?
        # PanelFactory sets it: self.view.weaves_panel. But doesn't pass
        # editor.

        # We need to find the editor.
        # Attempt to find parent view.
        parent = self.parent()
        editor = None
        while parent:
            if hasattr(parent, 'editor'):
                editor = parent.editor
                break
            parent = parent.parent()

        if not editor or not editor.original_image:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "No Image", "Please load an image first.")
            return

        dialog = ChannelSplitDialog(editor.get_current_image(), self)
        dialog.exec()

    def apply_to_selection(self):
        # 1. Get Selected Item
        item = self.list_widget.currentItem()
        if not item:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "No Weave", "Please select a weave pattern first.")
            return

        pattern = item.data(Qt.ItemDataRole.UserRole)

        # 2. Find Editor
        parent = self.parent()
        editor = None
        while parent:
            if hasattr(parent, 'editor'):
                editor = parent.editor
                break
            parent = parent.parent()

        if not editor:
            print("Editor not found for weave apply")
            return

        # 3. Apply
        editor.fill_with_pattern(pattern)

    def populate_weaves(self):
        self.list_widget.clear()

        weaves = {}
        if self.textile_service:
            # Load from Service
            # Service returns names, we fetch patterns one by one or we expose
            # a dict
            names = self.textile_service.get_available_weaves()
            for name in names:
                weaves[name] = self.textile_service.get_weave_pattern(name)
        else:
            # Fallback (Legacy)
            weaves = {
                "Plain": self._generate_plain(),
                "Twill 3/1": self._generate_twill(3, 1),
                "Satin 5": self._generate_satin(5, 2),
                "Satin 8": self._generate_satin(8, 3),
                "Honeycomb": self._generate_basket(2)  # Fallback mapping
            }

        for name, pattern in weaves.items():
            item = QListWidgetItem(name)
            # Create icon
            icon = self._create_icon(pattern)
            item.setIcon(icon)
            item.setData(Qt.ItemDataRole.UserRole, pattern)
            self.list_widget.addItem(item)

    def _create_icon(self, pattern):
        h, w = pattern.shape
        # Scale up for visibility (e.g. 10x)
        scale = 8
        img = QImage(w * scale, h * scale, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)  # Transparent background

        painter = QPainter(img)
        # Check active theme? Assuming Dark Theme
        # Draw White pixels for structure (warp up)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(Qt.PenStyle.NoPen)

        for y in range(h):
            for x in range(w):
                if pattern[y, x] == 1:
                    painter.drawRect(x * scale, y * scale, scale, scale)

        painter.end()
        return QIcon(QPixmap.fromImage(img))

    def on_item_clicked(self, item):
        pattern = item.data(Qt.ItemDataRole.UserRole)
        name = item.text()
        self.weave_selected.emit(pattern, name)

    def load_custom_weave(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Weave Pattern", "", "Images (*.bmp *.png *.jpg)")
        if not file_name:
            return

        try:
            import cv2
            img = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise ValueError("Failed to load image")

            # Threshold to binary (0/1)
            # Assume white (255) is warp up (1), black is down (0)
            _, binary = cv2.threshold(img, 127, 1, cv2.THRESH_BINARY)

            # Add to list
            name = "Custom: " + file_name.split("/")[-1]
            item = QListWidgetItem(name)
            item.setIcon(self._create_icon(binary))
            item.setData(Qt.ItemDataRole.UserRole, binary)
            self.list_widget.addItem(item)

            QMessageBox.information(
                self, "Success", f"Loaded custom weave: {name}")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load custom weave:\n{e}")

    # --- Weave Generators ---

    def _generate_plain(self):
        return np.array([[1, 0], [0, 1]], dtype=np.uint8)

    def _generate_basket(self, n):
        # 2x2 basket is 4x4 array
        arr = np.zeros((n * 2, n * 2), dtype=np.uint8)
        arr[0:n, 0:n] = 1
        arr[n:2 * n, n:2 * n] = 1
        return arr

    def _generate_twill(self, up, down):
        size = up + down
        arr = np.zeros((size, size), dtype=np.uint8)
        for y in range(size):
            for x in range(size):
                # Standard twill diagonal
                if (x - y) % size < up:
                    arr[y, x] = 1
        return arr

    def _generate_satin(self, size, step):
        # Sateen/Satin
        arr = np.zeros((size, size), dtype=np.uint8)
        for y in range(size):
            x = (y * step) % size
            arr[y, x] = 1
        return arr
