import sys
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QDesktopServices

class CloudExportDialog(QDialog):
    """
    A sleek, 'Midnight Industrial' Frameless Dialog that mirrors the Next.js Web UI.
    Receives pyqtSignals from the asynchronous CloudSyncWorker and vividly displays
    the Celery backend's progress in real-time.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. The Frameless Architecture
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(450, 220)
        
        # Build the main container to hold styling
        self.container = QWidget(self)
        self.container.setObjectName("MainContainer")
        self.container.setGeometry(0, 0, 450, 220)
        
        # Add a subtle neon drop shadow to the borderless window 
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor("#38bdf8")) # Neon Cyan
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)

        self._setup_ui()
        self._apply_styles()

        self.file_url = None

    def _setup_ui(self):
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Header section
        self.header_label = QLabel("Compiling Master Loom File...")
        self.header_label.setObjectName("HeaderLabel")
        header_font = QFont("Inter", 14, QFont.Weight.Bold)
        self.header_label.setFont(header_font)
        
        # Dynamic Celery WebSocket Text
        self.status_label = QLabel("Initializing AI Background Workers...")
        self.status_label.setObjectName("StatusLabel")
        status_font = QFont("Consolas", 10)
        self.status_label.setFont(status_font)
        self.status_label.setWordWrap(True)

        # The High-Tech Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)  # Hide the default % text for a cleaner look
        self.progress_bar.setFixedHeight(8)

        # The Action Buttons (Hidden initially)
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("BtnCancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_download = QPushButton("Download & Open JC5")
        self.btn_download.setObjectName("BtnDownload")
        self.btn_download.clicked.connect(self._handle_download)
        self.btn_download.hide() # Hidden until compilation succeeds

        self.button_layout.addWidget(self.btn_cancel)
        self.button_layout.addWidget(self.btn_download)

        # Assembly
        layout.addWidget(self.header_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(self.button_layout)

    def _apply_styles(self):
        """
        QSS Styles replicating the Tailwind CSS slate-900 / neon cyan theme.
        """
        self.setStyleSheet("""
            QWidget#MainContainer {
                background-color: #0f172a; /* Tailwind slate-900 */
                border: 1px solid #334155; /* Tailwind slate-700 */
                border-radius: 12px;
            }
            QLabel#HeaderLabel {
                color: #f8fafc; /* Tailwind slate-50 */
            }
            QLabel#StatusLabel {
                color: #94a3b8; /* Tailwind slate-400 */
                min-height: 20px;
            }
            QProgressBar {
                background-color: #1e293b; /* Tailwind slate-800 */
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #38bdf8; /* Tailwind cyan-400 */
                border-radius: 4px;
            }
            QPushButton {
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton#BtnCancel {
                background-color: transparent;
                color: #94a3b8;
                border: 1px solid #334155;
            }
            QPushButton#BtnCancel:hover {
                background-color: #1e293b;
                color: #f8fafc;
            }
            QPushButton#BtnDownload {
                background-color: rgba(16, 185, 129, 0.2); /* Emerald glow */
                color: #34d399; /* Emerald 400 */
                border: 1px solid rgba(16, 185, 129, 0.5);
            }
            QPushButton#BtnDownload:hover {
                background-color: rgba(16, 185, 129, 0.3);
            }
        """)

    # ---------------------------------------------------------
    # Public Slots for the CloudSyncWorker Signals
    # ---------------------------------------------------------
    def update_progress_ui(self, percentage: int, message: str):
        """Receives live websocket updates from the QThread."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)

    def show_success_state(self, file_url: str):
        """Triggered when Celery successfully compiles the BMP."""
        self.file_url = file_url
        self.header_label.setText("Master File Ready")
        self.header_label.setStyleSheet("color: #34d399;") # Turn header emerald
        self.btn_cancel.setText("Close")
        self.btn_download.show()

    def show_error_state(self, error_msg: str):
        """Triggered if the cloud stack crashes."""
        self.header_label.setText("Compilation Failed")
        self.header_label.setStyleSheet("color: #f43f5e;") # Turn header rose-500
        self.status_label.setText(error_msg)
        self.status_label.setStyleSheet("color: #f43f5e;")
        self.progress_bar.setStyleSheet("""
            QProgressBar::chunk { background-color: #f43f5e; }
        """)

    def _handle_download(self):
        """Opens the hardware BMP directly in the user's default OS browser."""
        if self.file_url:
            QDesktopServices.openUrl(QUrl(self.file_url))
        self.accept()
