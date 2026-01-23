from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QSplashScreen


class SplashScreen(QSplashScreen):
    def __init__(self):
        # Create a pixmap for the splash screen
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor("#2c3e50"))

        # Draw Logo/Text
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Title
        painter.setPen(QColor("#ecf0f1"))
        font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            pixmap.rect(),
            Qt.AlignmentFlag.AlignCenter,
            "SJ-DAS\nSmart Jacquard Design Automation")

        # Subtitle
        font.setPointSize(12)
        font.setWeight(QFont.Weight.Normal)
        painter.setFont(font)
        painter.drawText(
            0,
            250,
            600,
            50,
            Qt.AlignmentFlag.AlignCenter,
            "Initializing System Components...")

        painter.end()

        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        # Add Progress Bar (Overlay)
        # QSplashScreen doesn't support layouts directly easily, so we usually just draw or use message
        # We'll use showMessage for updates

    def update_progress(self, message):
        self.showMessage(f"\n\n\n\n\n\n\n{message}",
                         Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                         QColor("#bdc3c7"))
