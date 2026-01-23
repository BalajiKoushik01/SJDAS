"""
Color Palette Panel for SJ-DAS.
Visual color management interface for textile designers.
"""
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import (QFileDialog, QFrame, QGridLayout, QHBoxLayout,
                             QInputDialog, QLabel, QMessageBox, QPushButton,
                             QScrollArea, QVBoxLayout, QWidget)

if TYPE_CHECKING:
    from sj_das.ui.editor_widget import PixelEditorWidget

from sj_das.core.color_manager import ColorManager, ColorPalette


class ColorSwatch(QWidget):
    """Individual color swatch widget."""

    clicked = pyqtSignal(QColor)

    def __init__(self, color: QColor, name: str = "", parent=None):
        super().__init__(parent)
        self.color = color
        self.name = name
        self.setFixedSize(40, 40)
        self.setToolTip(
            f"{name}\nRGB: ({color.red()}, {color.green()}, {color.blue()})")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw color
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawRect(2, 2, 36, 36)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.color)


class ColorPalettePanel(QWidget):
    """Color Palette Management Panel."""

    color_selected = pyqtSignal(QColor)

    def __init__(self, editor: 'PixelEditorWidget', parent=None):
        super().__init__(parent)
        self.editor = editor
        self.color_manager = ColorManager()
        self.current_palette = ColorPalette("Default Palette")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header
        header = QLabel("Color Palette")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)

        # Action Buttons
        btn_layout = QHBoxLayout()

        extract_btn = QPushButton("Extract Colors")
        extract_btn.setToolTip("Extract colors from current image")
        extract_btn.clicked.connect(self.extract_colors)
        btn_layout.addWidget(extract_btn)

        save_btn = QPushButton("Save")
        save_btn.setToolTip("Save palette to file")
        save_btn.clicked.connect(self.save_palette)
        btn_layout.addWidget(save_btn)

        load_btn = QPushButton("Load")
        load_btn.setToolTip("Load palette from file")
        load_btn.clicked.connect(self.load_palette)
        btn_layout.addWidget(load_btn)

        layout.addLayout(btn_layout)

        # Color Count Label
        self.count_label = QLabel("Colors: 0")
        self.count_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.count_label)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #555;")
        layout.addWidget(line)

        # Scroll Area for Swatches
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Swatch Container
        self.swatch_container = QWidget()
        self.swatch_layout = QGridLayout(self.swatch_container)
        self.swatch_layout.setSpacing(5)
        self.swatch_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self.swatch_container)
        layout.addWidget(scroll)

        # Reduce to Palette Button
        reduce_btn = QPushButton("Reduce Image to Palette")
        reduce_btn.setToolTip("Quantize image to use only palette colors")
        reduce_btn.clicked.connect(self.reduce_to_palette)
        layout.addWidget(reduce_btn)

    def extract_colors(self):
        """Extract colors from current image."""
        if not self.editor.original_image:
            QMessageBox.warning(
                self, "No Image", "Please load an image first.")
            return

        # Get max colors from user
        max_colors, ok = QInputDialog.getInt(
            self, "Extract Colors",
            "Maximum number of colors:",
            16, 2, 256
        )

        if not ok:
            return

        # Convert QImage to numpy array
        img_array = self.editor._get_cv2_image(self.editor.original_image)

        # Extract colors
        colors_rgb = self.color_manager.extract_colors(img_array, max_colors)

        # Create new palette
        self.current_palette = ColorPalette(
            f"Extracted ({len(colors_rgb)} colors)")

        for i, (r, g, b) in enumerate(colors_rgb):
            color = QColor(r, g, b)
            self.current_palette.add_color(color, f"Color {i+1}")

        self.update_swatches()

    def update_swatches(self):
        """Update the swatch display."""
        # Clear existing swatches
        while self.swatch_layout.count():
            item = self.swatch_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new swatches (4 per row)
        for i, color in enumerate(self.current_palette.colors):
            row = i // 4
            col = i % 4

            swatch = ColorSwatch(color, self.current_palette.color_names[i])
            swatch.clicked.connect(self.on_color_clicked)
            self.swatch_layout.addWidget(swatch, row, col)

        # Update count
        self.count_label.setText(f"Colors: {len(self.current_palette.colors)}")

    def on_color_clicked(self, color: QColor):
        """Handle swatch click."""
        self.editor.set_brush_color(color)
        self.color_selected.emit(color)

    def save_palette(self):
        """Save current palette to file."""
        if not self.current_palette.colors:
            QMessageBox.warning(self, "Empty Palette", "No colors to save.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Palette", "", "Palette Files (*.pal);;JSON Files (*.json)"
        )

        if filepath:
            success = self.color_manager.save_palette(
                self.current_palette, filepath)
            if success:
                QMessageBox.information(
                    self, "Success", "Palette saved successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to save palette.")

    def load_palette(self):
        """Load palette from file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Palette", "", "Palette Files (*.pal *.json)"
        )

        if filepath:
            palette = self.color_manager.load_palette(filepath)
            if palette:
                self.current_palette = palette
                self.update_swatches()
                QMessageBox.information(
                    self, "Success", "Palette loaded successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to load palette.")

    def reduce_to_palette(self):
        """Reduce image colors to palette."""
        if not self.current_palette.colors:
            QMessageBox.warning(
                self,
                "Empty Palette",
                "Please extract or load a palette first.")
            return

        if not self.editor.original_image:
            QMessageBox.warning(
                self, "No Image", "Please load an image first.")
            return

        # Confirm action
        reply = QMessageBox.question(
            self, "Reduce to Palette",
            f"This will reduce the image to {len(self.current_palette.colors)} colors. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Get image as numpy array
        img_array = self.editor._get_cv2_image(self.editor.original_image)

        # Reduce to palette
        reduced = self.color_manager.reduce_to_palette(
            img_array, self.current_palette.colors)

        # Update editor
        self.editor.set_image(reduced)

        QMessageBox.information(
            self, "Success", "Image reduced to palette colors.")
