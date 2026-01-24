from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
    QLabel, QPushButton, QHBoxLayout, QFileDialog
)
from PyQt6.QtGui import QIcon, QPixmap, QDrag, QPainter, QColor
from PyQt6.QtCore import Qt, QMimeData, QSize, QUrl
import os

class DraggableListWidget(QListWidget):
    """Custom ListWidget to handle dragging of patterns."""
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
            
        drag = QDrag(self)
        mime = QMimeData()
        
        # Get data
        data = item.data(Qt.ItemDataRole.UserRole)
        
        if isinstance(data, QColor):
            # Send as Color and Text
            mime.setColorData(data)
            mime.setText(data.name())
        elif isinstance(data, str) and os.path.exists(data):
            # Send as File URL
            mime.setUrls([QUrl.fromLocalFile(data)])
        
        drag.setMimeData(mime)
        
        # Set drag pixmap
        pix = item.icon().pixmap(64, 64)
        drag.setPixmap(pix)
        drag.setHotSpot(pix.rect().center())
        
        drag.exec(Qt.DropAction.CopyAction)

class PatternLibraryWidget(QWidget):
    """
    Library of reusable Saree Motifs.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_patterns()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QHBoxLayout()
        self.lbl_title = QLabel("Motif Library")
        self.lbl_title.setStyleSheet("font-weight: bold; color: #ccc;")
        header.addWidget(self.lbl_title)
        
        self.btn_import = QPushButton("+")
        self.btn_import.setFixedWidth(30)
        self.btn_import.setToolTip("Import Pattern Image")
        self.btn_import.clicked.connect(self.import_pattern)
        header.addWidget(self.btn_import)
        
        layout.addLayout(header)

        # List View (Custom)
        self.list_widget = DraggableListWidget()
        self.list_widget.setIconSize(QSize(80, 80))
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setDragEnabled(True)
        self.list_widget.setSpacing(10)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: none;
            }
            QListWidget::item {
                color: #ddd;
            }
            QListWidget::item:selected {
                background-color: #444;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.list_widget)

    def load_sample_patterns(self):
        patterns = [
            ("Paisley", QColor(200, 100, 100)),
            ("Border 1", QColor(100, 200, 100)),
            ("Butta Sm", QColor(100, 100, 200)),
            ("Geometric", QColor(200, 200, 100)),
            ("Floral", QColor(200, 100, 200)),
        ]
        
        for name, color in patterns:
            pixmap = QPixmap(80, 80)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            if "Paisley" in name:
                painter.drawEllipse(20, 20, 40, 50)
            elif "Border" in name:
                painter.drawRect(0, 20, 80, 40)
            else:
                painter.drawEllipse(10, 10, 60, 60)
            
            painter.end()
            
            item = QListWidgetItem(QIcon(pixmap), name)
            item.setData(Qt.ItemDataRole.UserRole, color) 
            self.list_widget.addItem(item)

    def import_pattern(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Motif", "", "Images (*.png *.jpg *.bmp)")
        if path:
            name = os.path.basename(path)
            icon = QIcon(path)
            item = QListWidgetItem(icon, name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.list_widget.addItem(item)
