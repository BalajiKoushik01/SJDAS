"""
Theme management system for SJ-DAS.

Provides Dark/Light themes with custom accent colors,
similar to modern design applications.
"""

import json
import logging
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger("SJ_DAS.ThemeManager")


class ThemeManager(QObject):
    """
    Manages application themes and color schemes.

    Features:
        - Dark/Light mode switching
        - Custom accent colors
        - Theme persistence
        - Live theme updates
    """

    theme_changed = pyqtSignal(str)  # Emits theme name

    THEMES = {
        'dark': {
            'name': 'Dark',
            'colors': {
                'bg_primary': 'rgba(15, 23, 42, 0.60)',       # Glass Base
                'bg_secondary': 'rgba(30, 41, 59, 0.50)',     # Panels
                'bg_elevated': 'rgba(51, 65, 85, 0.60)',      # Hover/Popups
                'bg_hover': 'rgba(71, 85, 105, 0.40)',
                'border_subtle': 'rgba(255, 255, 255, 0.10)',
                'border_accent': '#6366F1',
                'text_primary': '#F1F5F9',
                'text_secondary': '#CBD5E1',
                'text_muted': '#94A3B8',
                'accent_primary': '#6366F1',
                'accent_secondary': '#8B5CF6',
                'success': '#10B981',
                'warning': '#F59E0B',
                'error': '#EF4444',
            }
        },
        'light': {
            'name': 'Light',
            'colors': {
                'bg_primary': '#FFFFFF',
                'bg_secondary': '#F8FAFC',
                'bg_elevated': '#F1F5F9',
                'bg_hover': '#E2E8F0',
                'border_subtle': '#E2E8F0',
                'border_accent': '#6366F1',
                'text_primary': '#0F172A',
                'text_secondary': '#475569',
                'text_muted': '#94A3B8',
                'accent_primary': '#6366F1',
                'accent_secondary': '#8B5CF6',
                'success': '#059669',
                'warning': '#D97706',
                'error': '#DC2626',
            }
        },
        'midnight': {
            'name': 'Midnight',
            'colors': {
                'bg_primary': '#000000',
                'bg_secondary': '#0A0A0A',
                'bg_elevated': '#1A1A1A',
                'bg_hover': '#2A2A2A',
                'border_subtle': '#1A1A1A',
                'border_accent': '#3B82F6',
                'text_primary': '#FFFFFF',
                'text_secondary': '#A0A0A0',
                'text_muted': '#606060',
                'accent_primary': '#3B82F6',
                'accent_secondary': '#60A5FA',
                'success': '#10B981',
                'warning': '#F59E0B',
                'error': '#EF4444',
            }
        }
    }

    ACCENT_COLORS = {
        'indigo': '#6366F1',
        'purple': '#8B5CF6',
        'blue': '#3B82F6',
        'cyan': '#06B6D4',
        'teal': '#14B8A6',
        'green': '#10B981',
        'orange': '#F97316',
        'red': '#EF4444',
        'pink': '#EC4899',
    }

    def __init__(self):
        super().__init__()
        self.current_theme = 'dark'
        self.current_accent = 'indigo'
        self.config_path = Path.home() / '.sj_das' / 'theme.json'
        self.load_preferences()

    def set_theme(self, theme_name: str) -> bool:
        """
        Switch to a different theme.

        Args:
            theme_name: Name of theme ('dark', 'light', 'midnight')

        Returns:
            True if theme was applied
        """
        if theme_name not in self.THEMES:
            logger.warning(f"Theme '{theme_name}' not found")
            return False

        self.current_theme = theme_name
        self._apply_theme()
        self.theme_changed.emit(theme_name)
        self._save_preferences()
        logger.info(f"Switched to theme: {theme_name}")
        return True

    def set_accent_color(self, accent_name: str) -> bool:
        """
        Set accent color.

        Args:
            accent_name: Name of accent color

        Returns:
            True if accent was applied
        """
        if accent_name not in self.ACCENT_COLORS:
            logger.warning(f"Accent '{accent_name}' not found")
            return False

        self.current_accent = accent_name
        self._apply_theme()
        self._save_preferences()
        logger.info(f"Set accent color: {accent_name}")
        return True

    def get_color(self, color_name: str) -> str:
        """Get color value from current theme."""
        theme = self.THEMES[self.current_theme]
        return theme['colors'].get(color_name, '#000000')

    def get_all_colors(self) -> dict[str, str]:
        """Get all colors from current theme."""
        theme = self.THEMES[self.current_theme]
        colors = theme['colors'].copy()
        # Override accent with current selection
        colors['accent_primary'] = self.ACCENT_COLORS[self.current_accent]
        return colors

    def get_stylesheet(self) -> str:
        """
        Generate global stylesheet for current theme.

        Returns:
            CSS stylesheet string
        """
        colors = self.get_all_colors()

        return f"""
        QWidget {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            font-family: 'Inter', 'Segoe UI', 'San Francisco', Roboto, sans-serif;
            font-size: 12px;
        }}

        QMainWindow {{
            background-color: {colors['bg_primary']};
        }}

        QPushButton {{
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['bg_elevated']}, stop:1 {colors['bg_primary']});
            color: {colors['text_primary']};
            border: 1px solid {colors['border_subtle']};
            border-radius: 6px;
            padding: 8px 16px; /* Increased padding */
            font-weight: 500;
            font-size: 12px;
        }}

        QPushButton:hover {{
            background-color: {colors['bg_hover']};
            border-color: {colors['border_accent']};
        }}

        QPushButton:pressed {{
            background-color: {colors['accent_primary']};
            color: white;
        }}

        QPushButton:disabled {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_muted']};
        }}

        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_subtle']};
            border-radius: 4px;
            padding: 8px 12px; /* Increased padding */
            font-size: 12px;
        }}

        QLineEdit:focus, QTextEdit:focus {{
            border-color: {colors['accent_primary']};
        }}

        QComboBox {{
            background-color: {colors['bg_elevated']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_subtle']};
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 12px;
        }}

        QComboBox:hover {{
            border-color: {colors['border_accent']};
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        QScrollBar:vertical {{
            background-color: {colors['bg_secondary']};
            width: 14px; /* Wider scrollbar */
            border-radius: 7px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {colors['bg_hover']};
            border-radius: 7px;
            min-height: 30px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {colors['accent_primary']};
        }}

        QToolTip {{
            background-color: {colors['bg_elevated']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_subtle']};
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 11px;
        }}

        QMenuBar {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border-bottom: 1px solid {colors['border_subtle']};
            font-size: 12px;
            padding: 4px;
        }}

        QMenuBar::item {{
            padding: 6px 12px;
        }}

        QMenuBar::item:selected {{
            background-color: {colors['bg_hover']};
            border-radius: 4px;
        }}

        QMenu {{
            background-color: {colors['bg_elevated']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_subtle']};
            border-radius: 6px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 6px 24px 6px 12px;
            border-radius: 4px;
        }}

        QMenu::item:selected {{
            background-color: {colors['accent_primary']};
            color: white;
        }}
        """

    def _apply_theme(self):
        """Apply current theme to application."""
        app = QApplication.instance()
        if app:
            app.setStyleSheet(self.get_stylesheet())
            logger.debug("Applied theme stylesheet")

    def load_preferences(self):
        """Load theme preferences from disk."""
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path) as f:
                prefs = json.load(f)
            self.current_theme = prefs.get('theme', 'dark')
            self.current_accent = prefs.get('accent', 'indigo')
            logger.info(
                f"Loaded theme preferences: {self.current_theme}/{self.current_accent}")
        except Exception as e:
            logger.error(f"Failed to load theme preferences: {e}")

    def _save_preferences(self):
        """Save theme preferences to disk."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump({
                    'theme': self.current_theme,
                    'accent': self.current_accent
                }, f, indent=2)
            logger.debug("Saved theme preferences")
        except Exception as e:
            logger.error(f"Failed to save theme preferences: {e}")
