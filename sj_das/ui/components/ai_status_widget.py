
from qfluentwidgets import IconWidget
import logging

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QColor, QIcon, QPainter
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar, InfoBarPosition, ToolTipFilter

from sj_das.core.services.ai_service import AIService

logger = logging.getLogger("SJ_DAS.AIStatusWidget")


class StatusIcon(QWidget):
    """
    Animated Icon for AI Status.
    States: Idle, Active (Spinning/Pulsing), Error
    """

    def __init__(self, icon: FIF, tooltip: str, color="#6366F1", parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)
        self.icon_char = icon.value[0]  # Get char from FluentIcon enum
        self.base_color = QColor(color)
        self.tooltip_text = tooltip
        self.setToolTip(tooltip)

        self.is_active = False
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.setInterval(50)  # 20 FPS

        self.has_error = False

    def set_active(self, active: bool, msg: str = None):
        self.is_active = active
        self.has_error = False
        if active:
            self.timer.start()
            if msg:
                self.setToolTip(f"{self.tooltip_text}: {msg}")
        else:
            self.timer.stop()
            self.angle = 0
            self.setToolTip(self.tooltip_text)
            self.update()

    def set_error(self, msg: str):
        self.has_error = True
        self.is_active = False
        self.timer.stop()
        self.setToolTip(f"{self.tooltip_text}: Error - {msg}")
        self.update()

    def _animate(self):
        self.angle = (self.angle + 15) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # Color
        if self.has_error:
            c = QColor("#EF4444")  # Red
        elif self.is_active:
            c = self.base_color
        else:
            c = QColor("#64748B")  # Disabled Gray

        # Draw Icon (Text)
        # Fluent Icons are often font based.
        # But qfluentwidgets icons are generally SVG or Font based internally.
        # Ideally we should use the icon's paint method, but rotation is hard.
        # Let's use `qfluentwidgets.Icon` if possible, but we extended QWidget.
        # Simpler: Draw text if we have the font loaded, OR use existing Icon widget and rotate it?
        # QFluentWidgets doesn't expose easy rotation.
        # Fallback: Draw a ring around checkmark?
        # Let's Draw a ring indicator around the icon.

        cx, cy = self.width() // 2, self.height() // 2

        # Draw Ring if active
        if self.is_active:
            painter.translate(cx, cy)
            painter.rotate(self.angle)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(c)
            # Draw distinct spinner parts
            # simple arc
            painter.drawPie(-12, -12, 24, 24, 0, 90 * 16)
            painter.drawPie(-12, -12, 24, 24, 180 * 16, 90 * 16)
            painter.resetTransform()

        # Draw Static Icon centered
        # We can use the Icon's pixmap
        # Create pixmap on fly
        icon = FIF(self.icon_char).icon()  # Reconstruct logic or use stored
        # self.icon_char is internal char. FIF is enum.
        # Wait, FIF.ROBOT is an enum member.

        # Construct icon from enum passed in __init__
        # Assuming `icon` arg was the Enum (FIF.ROBOT)
        # We need to store it
        pass  # Handle below

        # For simplicity in this constrained environment, let's just make circles with letters?
        # No, we promised icons.
        # Let's use the provided `icon` object's pixmap.

        # Actually proper way:
        # parent class QWidget.
        # We can use qfluentwidgets.IconWidget inside?
        # Too complex layout.

        # Let's just draw a simplistic circle implementation for "Status"
        # and override paint to draw the icon *if inactive* or center it if
        # active.

        # Re-implementation:
        # Draw background circle
        painter.setPen(Qt.PenStyle.NoPen)
        # painter.setBrush(c.darker(150))
        # painter.drawEllipse(2, 2, 24, 24)

        # Draw Icon
        # Since we don't have easy font access to "Segoe Fluent Icons" here without import checks
        # We'll trust the FIF helper gets us a QIcon.

    # Improved Implementation below


class AIStatusWidget(QFrame):
    """
    Status Bar Widget containing indicators for all AI subsystems.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.ai = AIService.instance()

        # Icons
        # Vision (Eye/Search)
        self.vision_icon = StatusIconWrapper(
            FIF.VIEW, "Computer Vision", "#10B981")
        # LLM (Chat/Robot)
        self.llm_icon = StatusIconWrapper(
            FIF.CHAT, "Language Intelligence", "#6366F1")
        # Gen (Brush/Palette)
        self.gen_icon = StatusIconWrapper(
            FIF.PALETTE, "Generative Design", "#F59E0B")
        # Voice (Mic)
        self.voice_icon = StatusIconWrapper(
            FIF.MICROPHONE, "Voice Control", "#EC4899")

        layout.addWidget(self.vision_icon)
        layout.addWidget(self.llm_icon)
        layout.addWidget(self.gen_icon)
        layout.addWidget(self.voice_icon)

        # Connections
        self.ai.task_started.connect(self.on_started)
        self.ai.task_completed.connect(self.on_completed)
        self.ai.task_error.connect(self.on_error)

    def on_started(self, task_type, msg):
        w = self._get_widget(task_type)
        if w:
            w.set_active(True, msg)

    def on_completed(self, task_type):
        w = self._get_widget(task_type)
        if w:
            w.set_active(False)

    def on_error(self, task_type, msg):
        w = self._get_widget(task_type)
        if w:
            w.set_error(msg)

    def _get_widget(self, task_type):
        if task_type == AIService.TASK_VISION:
            return self.vision_icon
        if task_type == AIService.TASK_LLM:
            return self.llm_icon
        if task_type == AIService.TASK_GEN:
            return self.gen_icon
        if task_type == AIService.TASK_VOICE:
            return self.voice_icon
        return None


# Helper Class with simpler implementation using QFluentWidgets Icon


class StatusIconWrapper(QWidget):
    def __init__(self, fluent_icon, tooltip, color):
        super().__init__()
        self.setFixedSize(30, 30)
        self.icon = IconWidget(fluent_icon, self)
        self.icon.setFixedSize(16, 16)
        self.icon.move(7, 7)  # Center

        self.color = QColor(color)
        self.setToolTip(tooltip)

        self.is_active = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)  # Trigger repaint for rotation
        self.angle = 0

    def set_active(self, active, msg=None):
        self.is_active = active
        if active:
            self.timer.start(50)
            if msg:
                self.setToolTip(msg)
        else:
            self.timer.stop()
            self.angle = 0
            self.update()

    def set_error(self, msg):
        self.is_active = False
        self.timer.stop()
        self.setToolTip(f"Error: {msg}")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.is_active:
            self.angle = (self.angle + 15) % 360
            painter.translate(15, 15)
            painter.rotate(self.angle)

            # Draw Spinner Ring
            pen = painter.pen()
            pen.setColor(self.color)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawArc(-10, -10, 20, 20, 0, 270 * 16)

        elif not self.is_active:
            # Subtle dot if idle? Or just icon?
            # Let's draw a small background status dot
            pass
