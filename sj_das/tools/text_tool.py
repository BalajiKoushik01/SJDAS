"""
TEXT TOOL - Most Critical Missing Feature!
Implements professional text editing for SJ-DAS
"""

import logging
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (QColorDialog, QDialog, QFontComboBox,
                             QGraphicsScene, QGraphicsTextItem, QHBoxLayout,
                             QLabel, QPushButton, QSpinBox, QVBoxLayout,
                             QCheckBox, QTextEdit, QDialogButtonBox)

from sj_das.tools.base import Tool

logger = logging.getLogger(__name__)


class TextToolDialog(QDialog):
    """Professional text input dialog with live preview."""

    text_created = pyqtSignal(str, QFont, QColor)  # text, font, color

    def __init__(self, parent=None, initial_text="",
                 initial_font=None, initial_color=None):
        super().__init__(parent)
        self.setWindowTitle("Text Tool")
        self.setMinimumSize(500, 400)

        self.current_color = initial_color or QColor(0, 0, 0)
        self.init_ui(initial_text, initial_font)

    def init_ui(self, initial_text, initial_font):
        layout = QVBoxLayout(self)

        # Text input area
        layout.addWidget(QLabel("Enter Text:"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(initial_text)
        self.text_edit.setMinimumHeight(150)
        self.text_edit.textChanged.connect(self.update_preview)
        layout.addWidget(self.text_edit)

        # Font controls
        font_layout = QHBoxLayout()

        # Font family
        font_layout.addWidget(QLabel("Font:"))
        self.font_combo = QFontComboBox()
        if initial_font:
            self.font_combo.setCurrentFont(initial_font)
        self.font_combo.currentFontChanged.connect(self.update_preview)
        font_layout.addWidget(self.font_combo, 2)

        # Font size
        font_layout.addWidget(QLabel("Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 200)
        self.size_spin.setValue(
            initial_font.pointSize() if initial_font else 24)
        self.size_spin.setSuffix(" pt")
        self.size_spin.valueChanged.connect(self.update_preview)
        font_layout.addWidget(self.size_spin)

        layout.addLayout(font_layout)

        # Font style
        style_layout = QHBoxLayout()

        self.chk_bold = QCheckBox("Bold")
        self.chk_bold.toggled.connect(self.update_preview)
        style_layout.addWidget(self.chk_bold)

        self.chk_italic = QCheckBox("Italic")
        self.chk_italic.toggled.connect(self.update_preview)
        style_layout.addWidget(self.chk_italic)

        self.chk_underline = QCheckBox("Underline")
        self.chk_underline.toggled.connect(self.update_preview)
        style_layout.addWidget(self.chk_underline)

        style_layout.addStretch()

        # Color button
        self.btn_color = QPushButton("Text Color")
        self.btn_color.clicked.connect(self.choose_color)
        self.update_color_button()
        style_layout.addWidget(self.btn_color)

        layout.addLayout(style_layout)

        # Preview area
        layout.addWidget(QLabel("Preview:"))
        self.preview_label = QLabel()
        self.preview_label.setMinimumHeight(80)
        self.preview_label.setStyleSheet(
            "border: 1px solid #ccc; background: white; padding: 10px;")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview_label)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Initial preview
        self.update_preview()

    def update_preview(self):
        """Update live preview of text."""
        text = self.text_edit.toPlainText()
        font = self.get_font()

        self.preview_label.setText(text or "[Empty Text]")
        self.preview_label.setFont(font)

        # Apply color
        palette = self.preview_label.palette()
        palette.setColor(
            self.preview_label.foregroundRole(),
            self.current_color)
        self.preview_label.setPalette(palette)

    def choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(
            self.current_color, self, "Choose Text Color")
        if color.isValid():
            self.current_color = color
            self.update_color_button()
            self.update_preview()

    def update_color_button(self):
        """Update color button visual."""
        r, g, b = self.current_color.red(), self.current_color.green(), self.current_color.blue()
        self.btn_color.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b}); "
            f"color: {'white' if r + g + b < 384 else 'black'};"
        )

    def get_font(self):
        """Get configured font."""
        font = QFont(self.font_combo.currentFont())
        font.setPointSize(self.size_spin.value())
        font.setBold(self.chk_bold.isChecked())
        font.setItalic(self.chk_italic.isChecked())
        font.setUnderline(self.chk_underline.isChecked())
        return font

    def get_text(self):
        """Get entered text."""
        return self.text_edit.toPlainText()

    def get_color(self):
        """Get selected color."""
        return self.current_color


class TextTool(Tool):
    """Professional text tool for canvas."""

    def __init__(self, editor):
        """Initialize with editor reference."""
        super().__init__(editor)
        self.active_text_item = None
        # scene is available via editor.scene() if needed, or we can use editor.viewport() mapping

    def mouse_press(self, pos: QPointF, buttons: Qt.MouseButton):
        """Handle mouse click - Create text at position."""
        if buttons & Qt.MouseButton.LeftButton:
            self.activate_at(pos)

    def activate_at(self, pos: QPointF):
        """Activate text tool dialog and create text at specific position."""
        dialog = TextToolDialog(self.editor)

        if dialog.exec():
            text = dialog.get_text()
            if text:
                font = dialog.get_font()
                color = dialog.get_color()
                self.create_text(text, font, color, pos)

    def create_text(self, text, font, color, pos: QPointF = None):
        """Create text item on canvas."""
        # Create text item
        text_item = QGraphicsTextItem(text)
        text_item.setFont(font)
        text_item.setDefaultTextColor(color)

        # Position at click point or center
        if pos:
            text_item.setPos(pos)
        elif hasattr(self.editor, 'viewport'):
            view_center = self.editor.viewport().rect().center()
            scene_center = self.editor.mapToScene(view_center)
            text_item.setPos(scene_center)
        else:
            text_item.setPos(100, 100)

        # Make it movable and selectable
        text_item.setFlag(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable, True)
        text_item.setFlag(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Add to scene
        # Access scene safely
        scene = self.editor.scene()
        if scene:
            scene.addItem(text_item)
            self.active_text_item = text_item
        else:
            logger.error("No scene found in editor to add text.")

        return text_item
