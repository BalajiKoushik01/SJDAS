"""
Theme Manager
-------------
Handles loading and applying the application theme (QSS).
Standardizes the visual look across the application.
"""

import os

from PyQt6.QtCore import QFile, QTextStream
from PyQt6.QtWidgets import QApplication

from sj_das.core.config import cfg
from sj_das.core.logging_config import log


class ThemeManager:
    @staticmethod
    def apply_theme(app: QApplication,
                    theme_name: str = "modern_indigo_theme.qss"):
        """
        Loads and applies the QSS stylesheet to the global QApplication.
        """
        try:
            # Construct asset path based on config
            theme_path = cfg.paths.ASSETS / theme_name

            if not theme_path.exists():
                # Fallback check (if using raw script and assets not moved yet)
                fallback_path = os.path.join(
                    os.getcwd(), "sj_das", "assets", theme_name)
                if os.path.exists(fallback_path):
                    theme_path = fallback_path
                else:
                    # Try modern_light_theme.qss as fallback
                    theme_path = cfg.paths.ASSETS / "modern_light_theme.qss"
                    if not theme_path.exists():
                        log.warning(f"Theme file not found: {theme_name}")
                        return

            file = QFile(str(theme_path))
            if file.open(QFile.OpenModeFlag.ReadOnly |
                         QFile.OpenModeFlag.Text):
                stream = QTextStream(file)
                style_sheet = stream.readAll()
                app.setStyleSheet(style_sheet)
                log.info(f"Applied Theme: {theme_path.name}")
                file.close()
            else:
                log.error(f"Could not open theme file: {theme_path}")

        except Exception as e:
            log.error(f"Failed to apply theme: {e}", exc_info=True)

    @staticmethod
    def get_accent_color():
        return "#6366F1"  # Modern indigo
