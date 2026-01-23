"""
Centralized keyboard shortcut management for SJ-DAS.

This module provides a unified system for registering and managing
keyboard shortcuts across the application, following industry standards
from Adobe Creative Suite and Figma.
"""

import logging
from collections.abc import Callable

from PyQt6.QtCore import QObject, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget

logger = logging.getLogger("SJ_DAS.ShortcutManager")


class ShortcutManager(QObject):
    """
    Manages all keyboard shortcuts for the application.

    Features:
        - Centralized shortcut registration
        - Conflict detection
        - Dynamic enable/disable
        - Shortcut customization support
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.parent = parent
        self.shortcuts: dict[str, QShortcut] = {}
        self.descriptions: dict[str, str] = {}

    def register(
        self,
        key_sequence: str,
        callback: Callable,
        description: str = "",
        context: Qt.ShortcutContext = Qt.ShortcutContext.WindowShortcut
    ) -> QShortcut:
        """
        Register a keyboard shortcut.

        Args:
            key_sequence: Key combination (e.g., "Ctrl+S", "V")
            callback: Function to call when shortcut is activated
            description: Human-readable description
            context: Shortcut context (Window, Application, Widget)

        Returns:
            The created QShortcut object

        Raises:
            ValueError: If shortcut already registered
        """
        if key_sequence in self.shortcuts:
            logger.warning(
                f"Shortcut {key_sequence} already registered, overwriting")

        shortcut = QShortcut(QKeySequence(key_sequence), self.parent)
        shortcut.setContext(context)
        shortcut.activated.connect(callback)

        self.shortcuts[key_sequence] = shortcut
        self.descriptions[key_sequence] = description

        logger.debug(f"Registered shortcut: {key_sequence} - {description}")
        return shortcut

    def unregister(self, key_sequence: str) -> bool:
        """
        Unregister a keyboard shortcut.

        Args:
            key_sequence: Key combination to unregister

        Returns:
            True if shortcut was found and removed
        """
        if key_sequence in self.shortcuts:
            self.shortcuts[key_sequence].setEnabled(False)
            del self.shortcuts[key_sequence]
            del self.descriptions[key_sequence]
            logger.debug(f"Unregistered shortcut: {key_sequence}")
            return True
        return False

    def enable(self, key_sequence: str, enabled: bool = True):
        """Enable or disable a specific shortcut."""
        if key_sequence in self.shortcuts:
            self.shortcuts[key_sequence].setEnabled(enabled)

    def get_all_shortcuts(self) -> dict[str, str]:
        """Get all registered shortcuts with their descriptions."""
        return self.descriptions.copy()

    def setup_default_shortcuts(self, view):
        """
        Setup all default keyboard shortcuts.

        Args:
            view: The main designer view with tool methods
        """
        # ===== TOOL SHORTCUTS (Single Key) =====
        self.register(
            "V",
            lambda: view.on_tool_selected("select"),
            "Selection Tool")
        self.register(
            "L",
            lambda: view.on_tool_selected("lasso"),
            "Lasso Tool")
        self.register(
            "W",
            lambda: view.on_tool_selected("magic_wand"),
            "Magic Wand")
        self.register(
            "B",
            lambda: view.on_tool_selected("brush"),
            "Brush Tool")
        self.register(
            "E",
            lambda: view.on_tool_selected("eraser"),
            "Eraser Tool")
        self.register("G", lambda: view.on_tool_selected("fill"), "Fill Tool")
        self.register("T", lambda: view.on_tool_selected("text"), "Text Tool")
        self.register(
            "I",
            lambda: view.on_tool_selected("eyedropper"),
            "Eyedropper")
        self.register(
            "S",
            lambda: view.on_tool_selected("clone"),
            "Clone Stamp")
        self.register(
            "R",
            lambda: view.on_tool_selected("rectangle"),
            "Rectangle Tool")
        self.register(
            "O",
            lambda: view.on_tool_selected("ellipse"),
            "Ellipse Tool")
        self.register("U", lambda: view.on_tool_selected("line"), "Line Tool")
        self.register("H", lambda: view.on_tool_selected("pan"), "Pan Tool")
        self.register("Z", lambda: view.on_tool_selected("zoom"), "Zoom Tool")

        # ===== EDIT OPERATIONS =====
        self.register("Ctrl+Z", view.undo, "Undo")
        self.register("Ctrl+Y", view.redo, "Redo")
        self.register("Ctrl+Shift+Z", view.redo, "Redo (Alt)")

        # ===== FILE OPERATIONS =====
        self.register("Ctrl+N", view.new_design, "New Design")
        self.register("Ctrl+O", view.import_image, "Open/Import")
        self.register("Ctrl+S", view.save_project, "Save")
        self.register(
            "Ctrl+Shift+S",
            view.save_project,
            "Save As")  # TODO: Add save_as
        self.register("Ctrl+E", view.export_design, "Export BMP")

        # ===== VIEW CONTROLS =====
        self.register("Ctrl++", lambda: view.editor.zoom_in(), "Zoom In")
        self.register("Ctrl+-", lambda: view.editor.zoom_out(), "Zoom Out")
        self.register(
            "Ctrl+0",
            lambda: view.editor.fit_to_window(),
            "Fit to Window")
        self.register("Ctrl+1", lambda: view.editor.zoom_to(1.0), "100% Zoom")
        self.register("F11", self.toggle_fullscreen, "Toggle Fullscreen")
        self.register("Tab", self.toggle_panels, "Toggle Panels")

        # ===== BRUSH SIZE CONTROLS =====
        self.register(
            "[", lambda: self.adjust_brush_size(
                view, -5), "Decrease Brush Size")
        self.register(
            "]", lambda: self.adjust_brush_size(
                view, +5), "Increase Brush Size")
        self.register(
            "Shift+[", lambda: self.adjust_opacity(view, -10), "Decrease Opacity")
        self.register(
            "Shift+]", lambda: self.adjust_opacity(view, +10), "Increase Opacity")

        # ===== QUICK ACTIONS =====
        self.register("Ctrl+K", self.show_quick_actions, "Quick Actions")
        self.register("Ctrl+Shift+A", view.auto_segment, "Auto-Segment")
        self.register("Ctrl+Shift+R", view.reduce_to_palette, "Reduce Colors")

        logger.info(f"Registered {len(self.shortcuts)} keyboard shortcuts")

    def adjust_brush_size(self, view, delta: int):
        """Adjust brush size by delta."""
        if hasattr(view, 'editor') and hasattr(view.editor, 'brush_size'):
            new_size = max(1, min(200, view.editor.brush_size + delta))
            view.editor.brush_size = new_size
            if hasattr(view, 'size_slider'):
                view.size_slider.setValue(new_size)

    def adjust_opacity(self, view, delta: int):
        """Adjust brush opacity by delta."""
        if hasattr(view, 'editor') and hasattr(view.editor, 'brush_opacity'):
            current = int(view.editor.brush_opacity * 100)
            new_opacity = max(0, min(100, current + delta))
            view.editor.brush_opacity = new_opacity / 100.0
            if hasattr(view, 'opacity_slider'):
                view.opacity_slider.setValue(new_opacity)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        window = self.parent.window()
        if window.isFullScreen():
            window.showNormal()
        else:
            window.showFullScreen()

    def toggle_panels(self):
        """Toggle visibility of side panels."""
        # Will be implemented when docking system is added
        logger.info("Toggle panels (not yet implemented)")

    def show_quick_actions(self):
        """Show quick actions command palette."""
        # Will be implemented in quick_actions.py
        logger.info("Quick actions (not yet implemented)")
