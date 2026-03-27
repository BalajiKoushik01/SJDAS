
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPixmap
from PyQt6.QtWidgets import (QApplication, QFrame, QGraphicsDropShadowEffect,
                             QLabel, QProgressBar, QVBoxLayout, QWidget, QSplashScreen)
from qfluentwidgets import IndeterminateProgressBar

class ModernSplashScreen(QSplashScreen):
    """
    Professional Glassmorphism Splash Screen.
    """
    def __init__(self):
        # Create a transparent pixmap for the splash surface
        pixmap = QPixmap(600, 350)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main Container (Glass)
        self.container = QWidget(self)
        self.container.setFixedSize(600, 350)
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 35, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
            }
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)
        
        # Layout
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)
        
        # 1. App Title
        self.lbl_title = QLabel("SJ-DAS Pro")
        self.lbl_title.setStyleSheet("""
            color: #FFFFFF;
            font-family: 'Segoe UI', sans-serif;
            font-size: 32px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl_title)
        
        # 2. Subtitle
        self.lbl_subtitle = QLabel("Professional AI Textile Suite | 2025.1")
        self.lbl_subtitle.setStyleSheet("""
            color: #A0A0A0;
            font-size: 14px;
            background: transparent;
            border: none;
        """)
        self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl_subtitle)
        
        self.layout.addStretch()
        
        # 3. Status
        self.lbl_status = QLabel("Initializing Cortex...")
        self.lbl_status.setStyleSheet("""
            color: #808080;
            font-size: 12px;
            background: transparent;
            border: none;
        """)
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl_status)
        
        # 4. Progress Bar
        self.progress = IndeterminateProgressBar(self.container)
        self.progress.setFixedWidth(400)
        self.layout.addWidget(self.progress, 0, Qt.AlignmentFlag.AlignHCenter)
        
    def show_message(self, message):
        """Update status message."""
        self.lbl_status.setText(message)
        QApplication.processEvents()
