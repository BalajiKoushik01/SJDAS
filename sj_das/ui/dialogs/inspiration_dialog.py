
import requests
from PyQt6.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (QDialog, QGridLayout, QHBoxLayout, QLabel,
                             QScrollArea, QVBoxLayout, QWidget)
from qfluentwidgets import (CardWidget, LineEdit, PrimaryPushButton,
                            StrongBodyLabel)

from sj_das.core.services.cloud_service import CloudService


class ImageLoader(QThread):
    loaded = pyqtSignal(int, QPixmap, str)  # index, pixmap, url

    def __init__(self, index, url):
        super().__init__()
        self.index = index
        self.url = url

    def run(self):
        try:
            if not self.url:
                return
            resp = requests.get(self.url, timeout=10)
            img = QImage()
            img.loadFromData(resp.content)
            pix = QPixmap.fromImage(img)
            self.loaded.emit(self.index, pix, self.url)
        except BaseException:
            pass


class InspirationCard(CardWidget):
    clicked = pyqtSignal(str)  # Emits image URL

    def __init__(self, title, date, parent=None):
        super().__init__(parent)
        self.url = None
        self.setFixedSize(200, 240)

        self.layout = QVBoxLayout(self)

        self.img_label = QLabel("Loading...")
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setFixedSize(180, 180)
        self.img_label.setStyleSheet(
            "background-color: #f0f0f0; border-radius: 4px;")
        self.img_label.setScaledContents(True)

        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-weight: bold;")

        self.layout.addWidget(self.img_label)
        self.layout.addWidget(self.title_label)

    def set_image(self, pixmap, url):
        self.img_label.setPixmap(pixmap)
        self.img_label.setText("")
        self.url = url

    def mousePressEvent(self, e):
        if self.url:
            self.clicked.emit(self.url)
        super().mousePressEvent(e)


class InspirationDialog(QDialog):
    image_selected = pyqtSignal(str)  # URL

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Infinite Inspiration (The Metadata)")
        self.resize(900, 700)

        self.cloud = CloudService.instance()
        self.loaders = []

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()
        self.search_box = LineEdit()
        self.search_box.setPlaceholderText(
            "Search The Met (e.g. 'Brocade', 'Silk', 'Floral')")
        self.search_box.returnPressed.connect(self.do_search)

        self.search_btn = PrimaryPushButton("Search History")
        self.search_btn.clicked.connect(self.do_search)

        header.addWidget(self.search_box)
        header.addWidget(self.search_btn)
        self.main_layout.addLayout(header)

        # Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid = QGridLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)

        self.main_layout.addWidget(self.scroll)

        self.status = StrongBodyLabel(
            "Ready to explore thousands of years of textile art.")
        self.main_layout.addWidget(self.status)

    def connect_signals(self):
        self.cloud.met_search_results.connect(self.on_search_results)
        self.cloud.met_object_details.connect(self.on_object_details)

    def do_search(self):
        query = self.search_box.text().strip()
        if not query:
            return

        # Clear grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.status.setText(f"Searching The Met for '{query}'...")
        self.cloud.search_met_museum(query)

    def on_search_results(self, ids):
        if not ids:
            self.status.setText("No results found. Try 'Silk' or 'Tapestry'.")
            return

        self.status.setText(f"Found {len(ids)} artifacts. Fetching details...")
        for oid in ids:
            self.cloud.get_met_object(oid)

    def on_object_details(self, data):
        if not data.get('image_url'):
            return

        # Add card to grid
        count = self.grid.count()
        row = count // 4
        col = count % 4

        card = InspirationCard(
            data.get(
                'title', 'Untitled'), data.get(
                'date', ''))
        card.clicked.connect(self.handle_selection)
        self.grid.addWidget(card, row, col)

        # Fetch thumbnail
        loader = ImageLoader(count, data['image_url'])
        loader.loaded.connect(lambda i, p, u, c=card: c.set_image(p, u))
        loader.start()
        self.loaders.append(loader)  # Keep ref

    def handle_selection(self, url):
        self.image_selected.emit(url)
        self.status.setText("Downloading high-res asset...")
        # In a real app, we'd emit and close OR let user browse more
        # For now, close
        self.accept()
