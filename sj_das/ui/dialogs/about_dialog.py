
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QFrame, QHBoxLayout, QGraphicsDropShadowEffect)
from qfluentwidgets import PrimaryPushButton, FluentIcon as FIF

class AboutDialog(QDialog):
    """
    Premium About Dialog with Glassmorphism.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About SJ-DAS")
        self.setFixedSize(500, 400)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            AboutDialog {
                background-color: #1E1E1E;
                border: 1px solid #333;
                border-radius: 12px;
            }
            QLabel {
                color: #E0E0E0;
            }
            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI Display', sans-serif;
                color: #FFFFFF;
            }
            QLabel#version {
                font-size: 14px;
                color: #A0A0A0;
            }
            QFrame#content {
                background-color: #2D2D2D;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header = QVBoxLayout()
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon = QLabel("💎")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("SJ-DAS Professional")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        version = QLabel("Version 2026.1 (Enterprise Edition)")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header.addWidget(icon)
        header.addWidget(title)
        header.addWidget(version)
        layout.addLayout(header)

        # Content Card
        card = QFrame()
        card.setObjectName("content")
        card_layout = QVBoxLayout(card)
        
        desc = QLabel(
            "The ultimate AI-powered ecosystem for textile design.\n"
            "Seamlessly integrating Neural Networks with traditional\n"
            "motif creation."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 13px; color: #CCCCCC; line-height: 1.4;")
        
        copyright = QLabel("© 2026 SJ-DAS Corp. All Rights Reserved.")
        copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright.setStyleSheet("font-size: 11px; color: #666666; margin-top: 10px;")
        
        card_layout.addWidget(desc)
        card_layout.addWidget(copyright)
        layout.addWidget(card)

        # Button
        btn_close = PrimaryPushButton("Close", self)
        btn_close.clicked.connect(self.accept)
        btn_close.setFixedWidth(120)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

