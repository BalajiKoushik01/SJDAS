"""
Toast Notification System.
Provides non-intrusive, auto-fading feedback messages (like Android Toasts).
"""

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QLabel


class ToastNotification(QLabel):
    """
    A modern, semi-transparent notification bubble that fades in/out.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        # Transparent background for the widget itself, we draw inside
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Style
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(30, 30, 30, 220);
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
                border: 1px solid #444;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.adjustSize()

        # Opacity Effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Animation
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)  # 300ms fade

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)

        self.hide()

    def show_message(self, message, duration=2000, color="#6C5CE7"):
        """
        Show a toast message.

        Args:
            message: Text to display
            duration: Time in ms to stay visible
            color: Border/Accent color (optional)
        """
        self.setText(message)
        # Dynamic styling for border color if needed
        self.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(30, 30, 30, 230);
                color: white;
                border-radius: 18px;
                padding: 10px 20px;
                border: 1px solid {color};
                font-family: "Segoe UI", sans-serif;
                font-size: 13px;
            }}
        """)
        self.adjustSize()

        # Center horizontally, position near bottom
        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            y = parent_rect.height() - self.height() - 60  # 60px from bottom
            self.move(x, y)

        self.show()
        self.raise_()

        # Fade In
        self.anim.setDirection(QPropertyAnimation.Direction.Forward)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

        # Schedule Fade Out
        self.timer.start(duration)

    def fade_out(self):
        self.anim.setDirection(QPropertyAnimation.Direction.Backward)
        self.anim.setEndValue(0.0)
        self.anim.start()
        # Hide after animation
        QTimer.singleShot(350, self.hide)
