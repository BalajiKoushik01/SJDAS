"""
Quick Actions command palette for fast feature access.

Provides a Cmd+K style searchable command palette similar to
VS Code, Figma, and modern design tools.
"""

import logging
from collections.abc import Callable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QVBoxLayout,
                             QWidget)

logger = logging.getLogger("SJ_DAS.QuickActions")


class QuickActionsDialog(QDialog):
    """
    Searchable command palette for quick access to all features.

    Features:
        - Fuzzy search
        - Keyboard navigation
        - Recent actions
        - Favorites system
    """

    action_triggered = pyqtSignal(str)  # Emits action ID

    def __init__(self, parent=None):
        super().__init__(parent)
        # (id, name, shortcut, callback)
        self.actions: list[tuple[str, str, str, Callable]] = []
        self.recent_actions: list[str] = []
        self.favorites: list[str] = []
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle("Quick Actions")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        # Remove window frame for modern look
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Type to search actions... (Esc to close)")
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #E2E8F0;
                border: none;
                border-bottom: 2px solid #6366F1;
                padding: 16px;
                font-size: 16px;
            }
        """)
        self.search_box.textChanged.connect(self.filter_actions)
        layout.addWidget(self.search_box)

        # Actions list
        self.actions_list = QListWidget()
        self.actions_list.setStyleSheet("""
            QListWidget {
                background-color: #0F172A;
                color: #E2E8F0;
                border: none;
                padding: 8px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 6px;
                margin: 2px 4px;
            }
            QListWidget::item:selected {
                background-color: #6366F1;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #334155;
            }
        """)
        self.actions_list.itemActivated.connect(self.execute_action)
        layout.addWidget(self.actions_list)

        # Footer with hints
        footer = QLabel("↑↓ Navigate  •  Enter Execute  •  Esc Close")
        footer.setStyleSheet("""
            QLabel {
                background-color: #1E293B;
                color: #94A3B8;
                padding: 8px 16px;
                font-size: 11px;
            }
        """)
        layout.addWidget(footer)

    def add_action(self, action_id: str, name: str,
                   shortcut: str = "", callback: Callable | None = None):
        """
        Add an action to the palette.

        Args:
            action_id: Unique identifier
            name: Display name
            shortcut: Keyboard shortcut (for display)
            callback: Function to call when executed
        """
        self.actions.append((action_id, name, shortcut, callback))

    def populate_actions(self, view):
        """
        Populate with all available actions from the view.

        Args:
            view: Main designer view with feature methods
        """
        # File operations
        self.add_action("new", "New Design", "Ctrl+N", view.new_design)
        self.add_action(
            "open",
            "Open/Import Image",
            "Ctrl+O",
            view.import_image)
        self.add_action("save", "Save Project", "Ctrl+S", view.save_project)
        self.add_action("export", "Export BMP", "Ctrl+E", view.export_design)
        self.add_action(
            "export_preview",
            "Export PNG Preview",
            "",
            view.export_preview)

        # Edit operations
        self.add_action("undo", "Undo", "Ctrl+Z", view.undo)
        self.add_action("redo", "Redo", "Ctrl+Y", view.redo)

        # Tools
        self.add_action("tool_select", "Selection Tool", "V",
                        lambda: view.on_tool_selected("select"))
        self.add_action("tool_brush", "Brush Tool", "B",
                        lambda: view.on_tool_selected("brush"))
        self.add_action("tool_eraser", "Eraser Tool", "E",
                        lambda: view.on_tool_selected("eraser"))
        self.add_action(
            "tool_fill",
            "Fill Tool",
            "G",
            lambda: view.on_tool_selected("fill"))
        self.add_action(
            "tool_wand",
            "Magic Wand",
            "W",
            lambda: view.on_tool_selected("magic_wand"))

        # AI Features
        self.add_action(
            "ai_analyze",
            "AI Analyze Design",
            "Ctrl+Shift+A",
            view.run_ai_analysis)
        self.add_action("ai_segment", "Auto-Segment", "", view.auto_segment)
        self.add_action(
            "ai_variations",
            "Generate Variations",
            "",
            view.generate_variations)

        # Color operations
        self.add_action("pick_color", "Pick Color", "", view.pick_color)
        self.add_action(
            "reduce_colors",
            "Reduce to Palette",
            "Ctrl+Shift+R",
            view.reduce_to_palette)

        # Advanced features (if available)
        if hasattr(view, 'activate_magic_eraser'):
            self.add_action("magic_eraser", "Magic Eraser",
                            "", view.activate_magic_eraser)

        logger.info(f"Populated {len(self.actions)} actions")

    def filter_actions(self, search_text: str):
        """Filter actions based on search text."""
        self.actions_list.clear()

        search_lower = search_text.lower()

        # Show recent actions first if no search
        if not search_text and self.recent_actions:
            recent_label = QListWidgetItem("Recent Actions")
            recent_label.setFlags(Qt.ItemFlag.NoItemFlags)
            recent_label.setForeground(Qt.GlobalColor.gray)
            self.actions_list.addItem(recent_label)

            for action_id in self.recent_actions[:5]:
                action = next(
                    (a for a in self.actions if a[0] == action_id), None)
                if action:
                    self._add_action_item(action)

            if len(self.actions) > len(self.recent_actions):
                all_label = QListWidgetItem("All Actions")
                all_label.setFlags(Qt.ItemFlag.NoItemFlags)
                all_label.setForeground(Qt.GlobalColor.gray)
                self.actions_list.addItem(all_label)

        # Filter and display matching actions
        for action in self.actions:
            action_id, name, shortcut, callback = action

            # Skip recent actions if already shown
            if not search_text and action_id in self.recent_actions[:5]:
                continue

            # Fuzzy match
            if not search_text or search_lower in name.lower():
                self._add_action_item(action)

        # Select first item
        if self.actions_list.count() > 0:
            # Skip category labels
            for i in range(self.actions_list.count()):
                item = self.actions_list.item(i)
                if item.flags() & Qt.ItemFlag.ItemIsSelectable:
                    self.actions_list.setCurrentRow(i)
                    break

    def _add_action_item(self, action: tuple):
        """Add an action item to the list."""
        action_id, name, shortcut, callback = action

        # Create custom widget for better layout
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(4, 0, 4, 0)

        name_label = QLabel(name)
        name_label.setStyleSheet("color: #E2E8F0; font-weight: 500;")
        item_layout.addWidget(name_label)

        item_layout.addStretch()

        if shortcut:
            shortcut_label = QLabel(shortcut)
            shortcut_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
            item_layout.addWidget(shortcut_label)

        item = QListWidgetItem(self.actions_list)
        item.setSizeHint(item_widget.sizeHint())
        item.setData(Qt.ItemDataRole.UserRole, action_id)

        self.actions_list.addItem(item)
        self.actions_list.setItemWidget(item, item_widget)

    def execute_action(self, item: QListWidgetItem):
        """Execute the selected action."""
        action_id = item.data(Qt.ItemDataRole.UserRole)
        if not action_id:
            return

        # Find and execute action
        action = next((a for a in self.actions if a[0] == action_id), None)
        if action and action[3]:  # Has callback
            logger.info(f"Executing action: {action_id}")

            # Add to recent actions
            if action_id in self.recent_actions:
                self.recent_actions.remove(action_id)
            self.recent_actions.insert(0, action_id)
            self.recent_actions = self.recent_actions[:10]  # Keep last 10

            # Execute
            try:
                action[3]()  # Call callback
                self.accept()  # Close dialog
            except Exception as e:
                logger.error(f"Error executing action {action_id}: {e}")

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard navigation."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current_item = self.actions_list.currentItem()
            if current_item:
                self.execute_action(current_item)
        elif event.key() == Qt.Key.Key_Down:
            current_row = self.actions_list.currentRow()
            if current_row < self.actions_list.count() - 1:
                self.actions_list.setCurrentRow(current_row + 1)
        elif event.key() == Qt.Key.Key_Up:
            current_row = self.actions_list.currentRow()
            if current_row > 0:
                self.actions_list.setCurrentRow(current_row - 1)
        else:
            # Pass to search box
            self.search_box.setFocus()
            super().keyPressEvent(event)

    def showEvent(self, event):
        """Focus search box when shown."""
        super().showEvent(event)
        self.search_box.setFocus()
        self.search_box.clear()
        self.filter_actions("")  # Show all/recent
