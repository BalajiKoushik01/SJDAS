from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont, QScreen
from PyQt6.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel, QMainWindow,
                             QMessageBox, QPushButton, QStackedWidget,
                             QTextEdit, QVBoxLayout, QWidget)

from sj_das.utils.logger import logger

from .assembler_view import AssemblerView
from .designer_view import DesignerView
from .digital_twin_view import DigitalTwinView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SJ-DAS | Smart Jacquard Design Automation System")

        # Optimize for screen real estate - use larger default size
        screen = QScreen.availableGeometry(self.screen())
        # Use 90% of screen size by default
        width = int(screen.width() * 0.9)
        height = int(screen.height() * 0.9)
        # Center on screen
        x = int((screen.width() - width) / 2)
        y = int((screen.height() - height) / 2)
        self.setGeometry(x, y, width, height)

        # Set minimum size for usability
        self.setMinimumSize(1280, 720)

        # Stylesheet is loaded globally by ThemeManager
        # self.load_stylesheet()

        # Professional Status Bar
        self.status_bar = self.statusBar()
        self.status_bar.setObjectName("statusBar")
        self.status_bar = self.statusBar()
        self.status_bar.setObjectName("statusBar")
        # Hardcoded styles removed in favor of global theme

        # Create status widgets
        from PyQt6.QtWidgets import QLabel
        self.status_coordinates = QLabel("X: 0, Y: 0")
        self.status_coordinates.setObjectName("statusCoordinates")
        self.status_zoom = QLabel("Zoom: 100%")
        self.status_zoom.setObjectName("statusZoom")
        self.status_tool = QLabel("Tool:  None")
        self.status_tool.setObjectName("statusTool")

        self.status_bar.addPermanentWidget(self.status_coordinates)
        self.status_bar.addPermanentWidget(QLabel("|"))
        self.status_bar.addPermanentWidget(self.status_zoom)
        self.status_bar.addPermanentWidget(QLabel("|"))
        self.status_bar.addPermanentWidget(self.status_tool)

        self.status_bar.showMessage(
            "Welcome to SJ-DAS | Professional Textile Design Software")

        # Menu Bar
        self.create_menu_bar()

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header
        self.create_header()

        # Content Area (Stacked Widget for modes)
        self.stack = QStackedWidget()

        # OPTIMIZATION: Lazy load views
        self._views_loaded = {
            0: False, 1: False, 2: False, 3: False
        }

        # Create placeholders
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QLabel

        for _i in range(3):
            placeholder = QLabel("Loading...")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("font-size: 18px; color: #888;")
            self.stack.addWidget(placeholder)

        self.main_layout.addWidget(self.stack)

        # Defer loading of first view
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.delayed_init)

        # Show Welcome Overlay for New Users
        QTimer.singleShot(500, self.show_welcome_overlay)

    def load_stylesheet(self):
        import os
        try:
            # Path relative to this file: ../resources/
            base_dir = os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)))

            # Try professional theme first
            qss_path = os.path.join(
                base_dir, "resources", "professional_theme.qss")

            if os.path.exists(qss_path):
                with open(qss_path, encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
                logger.info("Loaded professional_theme.qss")
                return

            # Fallback to styles.qss
            qss_path = os.path.join(base_dir, "resources", "styles.qss")
            if os.path.exists(qss_path):
                with open(qss_path) as f:
                    self.setStyleSheet(f.read())
                logger.info("Loaded styles.qss")
            else:
                logger.warning(f"Stylesheet not found at {qss_path}")
        except Exception as e:
            logger.error(f"Failed to load stylesheet: {e}")

    def delayed_init(self):
        """Called after window is shown to load initial view and start background tasks."""
        try:
            logger.debug("Starting delayed_init...")
            self._load_view(0)

            # Schedule background loading later to avoid competing with initial
            # render
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1000, self.start_background_loader)

            logger.info("Initial view loaded. Background tasks scheduled.")
        except Exception as e:
            logger.error(f"Error in delayed_init: {e}", exc_info=True)

    def start_background_loader(self):
        """Start background thread to warm up PyTorch models."""
        from PyQt6.QtCore import QThread, pyqtSignal

        class BackgroundLoader(QThread):
            finished = pyqtSignal()

            def run(self):
                try:
                    logger.debug("BackgroundLoader started.")
                    from sj_das.core.segmentation import SegmentationEngine
                    SegmentationEngine()
                    # engine._ensure_torch() # Warm up
                    logger.debug("BackgroundLoader finished imports.")
                except Exception as e:
                    logger.warning(f"Background load warning: {e}")
                self.finished.emit()

        self.bg_loader = BackgroundLoader()
        self.bg_loader.start()

    def create_menu_bar(self):
        print("=" * 60)
        print("MAINWINDOW: Creating menu bar NOW!")
        print("=" * 60)

        menubar = self.menuBar()
        menubar.setVisible(True)  # Explicitly make visible
        menubar.setNativeMenuBar(False)  # Don't use native menu bar
        # Hardcoded styles removed in favor of global theme

        # File Menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu (NEW - For Advanced Panels)
        view_menu = menubar.addMenu("View")

        toggle_fullscreen_action = QAction("Toggle Fullscreen", self)
        toggle_fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(toggle_fullscreen_action)

        view_menu.addSeparator()

        self.panels_action = QAction("Show Advanced Panels", self)
        self.panels_action.setShortcut("F9")
        self.panels_action.setCheckable(True)
        self.panels_action.triggered.connect(self.toggle_advanced_panels)
        view_menu.addAction(self.panels_action)

        view_menu.addSeparator()

        self.layers_action = QAction("Layers Panel", self)
        self.layers_action.setCheckable(True)
        view_menu.addAction(self.layers_action)

        self.history_action = QAction("History Panel", self)
        self.history_action.setCheckable(True)
        view_menu.addAction(self.history_action)

        self.palette_action = QAction("Color Palette Panel", self)
        self.palette_action.setCheckable(True)
        view_menu.addAction(self.palette_action)

        # Image Menu (Phase 8) - Delegates to View
        image_menu = menubar.addMenu("Image")

        # Adjustments
        adj_menu = image_menu.addMenu("Adjustments")
        adj_menu.addAction(
            "Brightness/Contrast...",
            lambda: self.trigger_view_action("apply_brightness_contrast"))
        adj_menu.addAction(
            "Hue/Saturation...",
            lambda: self.trigger_view_action("apply_hue_saturation"))

        image_menu.addSeparator()

        # Transforms
        image_menu.addAction(
            "Flip Horizontal",
            lambda: self.trigger_view_action_param(
                "apply_transform",
                "flip_h"))
        image_menu.addAction(
            "Flip Vertical",
            lambda: self.trigger_view_action_param(
                "apply_transform_v",
                "flip_v"))  # Wrapper needed
        image_menu.addAction(
            "Rotate 90° CW",
            lambda: self.trigger_view_action_param(
                "apply_transform",
                "rotate_cw"))
        image_menu.addAction(
            "Rotate 90° CCW",
            lambda: self.trigger_view_action_param(
                "apply_transform",
                "rotate_ccw"))

        # Filter Menu (Phase 8)
        filter_menu = menubar.addMenu("Filter")
        filter_menu.addAction(
            "Gaussian Blur",
            lambda: self.trigger_view_action("apply_filter_gaussian_blur"))
        filter_menu.addAction(
            "Sharpen",
            lambda: self.trigger_view_action("apply_filter_sharpen"))

        # Select Menu (Phase 9)
        select_menu = menubar.addMenu("Select")

        sel_all = QAction("All", self)
        sel_all.setShortcut("Ctrl+A")
        sel_all.triggered.connect(
            lambda: self.trigger_view_action("select_all"))
        select_menu.addAction(sel_all)

        sel_inv = QAction("Inverse", self)
        sel_inv.setShortcut("Ctrl+Shift+I")
        sel_inv.triggered.connect(
            lambda: self.trigger_view_action("invert_selection"))
        select_menu.addAction(sel_inv)

        sel_none = QAction("Deselect", self)
        sel_none.setShortcut("Ctrl+D")
        sel_none.triggered.connect(
            lambda: self.trigger_view_action("clear_selection"))
        select_menu.addAction(sel_none)

        # Help Menu
        help_menu = menubar.addMenu("Help")

        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.triggered.connect(self.show_shortcuts_dialog)
        help_menu.addAction(shortcuts_action)

        about_action = QAction("About SJ-DAS", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def toggle_advanced_panels(self):
        """Toggle all advanced panels on/off."""
        # Get current designer view
        current_widget = self.stack.currentWidget()
        if hasattr(current_widget, 'show_advanced_panels'):
            current_widget.show_advanced_panels()
            self.panels_action.setChecked(True)

    def show_shortcuts_dialog(self):
        """Show keyboard shortcuts help dialog."""

        dialog = QDialog(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml("""
        <h2>SJ-DAS Keyboard Shortcuts</h2>
        <h3>Tools</h3>
        <table>
        <tr><td><b>B</b></td><td>Brush Tool</td></tr>
        <tr><td><b>E</b></td><td>Eraser Tool</td></tr>
        <tr><td><b>G</b></td><td>Fill Tool</td></tr>
        <tr><td><b>I</b></td><td>Eyedropper</td></tr>
        <tr><td><b>H</b></td><td>Pan Tool</td></tr>
        <tr><td><b>M</b></td><td>Rectangle Select</td></tr>
        <tr><td><b>W</b></td><td>Magic Wand</td></tr>
        </table>
        <h3>File Operations</h3>
        <table>
        <tr><td><b>Ctrl+N</b></td><td>New Project</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save</td></tr>
        <tr><td><b>Ctrl+E</b></td><td>Export</td></tr>
        </table>
        <h3>Edit</h3>
        <table>
        <tr><td><b>Ctrl+Z</b></td><td>Undo</td></tr>
        <tr><td><b>Ctrl+Y</b></td><td>Redo</td></tr>
        </table>
        <h3>View</h3>
        <table>
        <tr><td><b>+</b></td><td>Zoom In</td></tr>
        <tr><td><b>-</b></td><td>Zoom Out</td></tr>
        <tr><td><b>0</b></td><td>Zoom 100%</td></tr>
        <tr><td><b>F9</b></td><td>Toggle Advanced Panels</td></tr>
        <tr><td><b>F1</b></td><td>This Help</td></tr>
        </table>
        """)
        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def show_about_dialog(self):
        """Show about dialog."""

        QMessageBox.about(self, "About SJ-DAS",
                          "<h2>SJ-DAS</h2>"
                          "<p><b>Smart Jacquard Design Automation System</b></p>"
                          "<p>Version 1.0 Production</p>"
                          "<p>Professional textile design software with AI-powered pattern detection</p>"
                          "<p>© 2025 SJ-DAS. All rights reserved.</p>"
                          "<p><a href='https://sjdas.com'>www.sjdas.com</a></p>"
                          )

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def create_header(self):
        header = QFrame()
        # Header Styling is now in QSS under QFrame#header usually, but we can
        # set object name
        header.setObjectName("header")
        header.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border-bottom: 2px solid #333;
            }
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Title
        title = QLabel("SJ-DAS")
        title.setObjectName("lbl_title")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))

        subtitle = QLabel("| Design Automation")
        subtitle.setObjectName("lbl_subtitle")
        subtitle.setFont(QFont("Segoe UI", 12))

        header_layout.addWidget(title)
        header_layout.addSpacing(10)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()

        # Mode Switcher Buttons
        self.btn_designer = self.create_nav_button("Designer Mode", True)
        self.btn_production = self.create_nav_button(
            "Production Mode (F2)", False)
        self.btn_twin = self.create_nav_button("Twin+ Mode (F3)", False)

        self.btn_designer.clicked.connect(lambda: self.switch_mode(0))
        # Renamed Assembler to 1 (Production)
        self.btn_production.clicked.connect(lambda: self.switch_mode(1))
        self.btn_twin.clicked.connect(
            lambda: self.switch_mode(2))       # Renamed Twin to 2

        # Add shortcuts
        self.btn_designer.setShortcut("F1")
        self.btn_production.setShortcut("F2")
        self.btn_twin.setShortcut("F3")

        header_layout.addWidget(self.btn_designer)
        header_layout.addWidget(self.btn_production)
        header_layout.addWidget(self.btn_twin)

        # Help Button
        btn_help = QPushButton("?")
        btn_help.setFixedSize(30, 30)
        btn_help.setToolTip("User Guide")
        # Reuses welcome overlay as help
        btn_help.clicked.connect(self.show_welcome_overlay)
        header_layout.addWidget(btn_help)

        self.main_layout.addWidget(header)

    def show_welcome_overlay(self):
        from PyQt6.QtWidgets import QMessageBox
        help_text = """
        <div style='text-align: center; color: #e0e0e0;'>
            <h2>Welcome to SJ-DAS</h2>
            <p>Smart Jacquard Design Automation System</p>
        </div>
        <hr style='border: 1px solid #444;'>
        <table cellspacing='10' style='color: #ccc;'>
            <tr>
                <td style='font-size: 16px; font-weight: bold; color: #0078d4;'>1. Designer Mode</td>
                <td>Load sketches, Auto-Segment, and Pattern Design.</td>
            </tr>
            <tr>
                <td style='font-size: 16px; font-weight: bold; color: #2ecc71;'>2. Manufacturer Mode</td>
                <td>Weave mapping, Color Reduction, and Loom Config.</td>
            </tr>
             <tr>
                <td style='font-size: 16px; font-weight: bold; color: #e67e22;'>3. Assembler Mode</td>
                <td>Assemble Saree parts (Body+Border+Pallu).</td>
            </tr>
        </table>
        <p style='color: #888; text-align: center;'><i>Press '?' at top right to see this guide again.</i></p>
        """
        QMessageBox.information(self, "Quick Start Guide", help_text)

    def create_nav_button(self, text, active=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.update_btn_style(btn, active)
        return btn

    def update_btn_style(self, btn, active):
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #bdc3c7;
                    border: 1px solid #7f8c8d;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    color: white;
                }
            """)

    def _load_view(self, index):
        """Lazy load a view only when needed"""
        if self._views_loaded.get(index, False):
            return

        try:
            logger.debug(f"Loading view {index}...")
            if self.status_bar:
                self.status_bar.showMessage(f"Loading view {index}...")

            views_classes = [
                ("DesignerView", DesignerView),
                # Reusing Assembler as Production
                ("ProductionView", AssemblerView),
                ("TwinPlusView", DigitalTwinView)
            ]

            # Safety check
            if index >= len(views_classes):
                return

            name, ViewClass = views_classes[index]

            # Instantiate View
            view = ViewClass()

            # Replace placeholder safely
            current_widget = self.stack.widget(index)
            if current_widget:
                self.stack.removeWidget(current_widget)
                current_widget.deleteLater()

            self.stack.insertWidget(index, view)

            # Ensure it shows
            if self.stack.currentIndex() == index:
                self.stack.setCurrentWidget(view)

            self._views_loaded[index] = True
            if self.status_bar:
                self.status_bar.showMessage(f"Ready: {name}")
            logger.debug(f"View {index} ({name}) loaded successfully.")

        except Exception as e:
            logger.error(f"Failed to load view {index}: {e}", exc_info=True)
            if self.status_bar:
                self.status_bar.showMessage(f"Error loading view {index}")

    def switch_mode(self, index):
        # Load view if not already loaded
        self._load_view(index)

        self.stack.setCurrentIndex(index)
        self.update_btn_style(self.btn_designer, index == 0)
        self.update_btn_style(self.btn_production, index == 1)
        self.update_btn_style(self.btn_twin, index == 2)

    def trigger_view_action(self, method_name):
        """Call method on current view or its editor."""
        widget = self.stack.currentWidget()
        if not widget:
            return

        # 1. Try View Method
        if hasattr(widget, method_name):
            getattr(widget, method_name)()
            return

        # 2. Try Editor Method
        if hasattr(widget, 'editor') and hasattr(widget.editor, method_name):
            getattr(widget.editor, method_name)()

    def trigger_view_action_param(self, method_name, param):
        """Call method with param on current view or its editor."""
        widget = self.stack.currentWidget()
        if not widget:
            return

        # 1. Try View Method
        if hasattr(widget, method_name):
            getattr(widget, method_name)(param)
            return

        # 2. Try Editor Method
        if hasattr(widget, 'editor') and hasattr(widget.editor, method_name):
            getattr(widget.editor, method_name)(param)
