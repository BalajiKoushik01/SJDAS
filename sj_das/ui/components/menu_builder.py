
import logging

from qfluentwidgets import Action, DropDownPushButton
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import RoundMenu as Menu

logger = logging.getLogger("SJ_DAS.MenuBuilder")


class StandardMenuBuilder:
    """
    Standardized Menu Builder for modern_designer_view.
    Decouples UI layout from logic.
    """

    def __init__(self, parent_view, layout):
        self.view = parent_view
        self.layout = layout

    def build_all(self):
        """Constructs the entire Fluent Tool Options Bar."""
        # Add spacing between logical groups
        self.build_file_menu()
        self.build_edit_menu()
        self.build_view_menu()
        self.layout.addSpacing(12)  # Group separator

        # Design & Transform Group
        self.build_design_menu()
        self.build_image_menu()
        self.layout.addSpacing(12)  # Group separator

        # Domain-Specific Group
        self.build_textile_menu()
        self.layout.addSpacing(12)  # Group separator

        # AI & Automation Group
        self.build_ai_suite_menu()
        self.layout.addSpacing(12)  # Group separator

        # Utility Group
        self.build_tools_menu()
        self.build_help_menu()
        self.build_settings_menu()
        self.layout.addSpacing(16)  # Larger space before special button

        # Voice Control (Special Action Button)
        btn_voice = DropDownPushButton("🎙️ Voice", self.view)
        btn_voice.clicked.connect(self.view.activate_voice_control)
        btn_voice.setStyleSheet(
            "background-color: #EF4444; "
            "color: white; "
            "border-radius: 8px; "
            "font-weight: bold; "
            "padding: 6px 12px;"
        )
        self._add_btn(btn_voice)

        self.layout.addStretch()  # Push everything to the left

    def _add_btn(self, btn, add_spacing_after=False):
        """Add button with consistent sizing and optional spacing."""
        btn.setFixedHeight(34)  # Slightly taller for better touch targets
        btn.setMinimumWidth(80)  # Minimum width for consistency
        self.layout.addWidget(btn)
        if add_spacing_after:
            self.layout.addSpacing(8)  # Uniform spacing between groups

    # --- Core Menus ---

    def build_file_menu(self):
        btn = DropDownPushButton("File", self.view)
        menu = Menu(parent=self.view)
        menu.addAction(Action(FIF.FOLDER, "New", triggered=self.view.new_file))
        menu.addAction(
            Action(
                FIF.FOLDER_ADD,
                "Open",
                triggered=self.view.open_file))
        menu.addAction(Action(FIF.SAVE, "Save", triggered=self.view.save_file))
        menu.addAction(
            Action(
                FIF.SAVE_AS,
                "Save As",
                triggered=self.view.save_file_as))
        menu.addSeparator()
        menu.addAction(Action(FIF.CLOSE, "Exit", triggered=self.view.close))
        btn.setMenu(menu)
        self._add_btn(btn)

    def build_edit_menu(self):
        btn = DropDownPushButton("Edit", self.view)
        menu = Menu(parent=self.view)
        menu.addAction(Action(FIF.CANCEL, "Undo", triggered=self.view.undo))
        menu.addAction(Action(FIF.SYNC, "Redo", triggered=self.view.redo))
        menu.addSeparator()
        menu.addAction(Action(FIF.CUT, "Cut", triggered=self.view.cut))
        menu.addAction(Action(FIF.COPY, "Copy", triggered=self.view.copy))
        menu.addAction(Action(FIF.PASTE, "Paste", triggered=self.view.paste))
        btn.setMenu(menu)
        self._add_btn(btn)

    def build_view_menu(self):
        btn = DropDownPushButton("View", self.view)
        menu = Menu(parent=self.view)
        menu.addAction(
            Action(
                FIF.ZOOM_IN,
                "Zoom In",
                triggered=self.view.zoom_in))
        menu.addAction(
            Action(
                FIF.ZOOM_OUT,
                "Zoom Out",
                triggered=self.view.zoom_out))
        menu.addAction(
            Action(
                FIF.FIT_PAGE,
                "Fit to Window",
                triggered=self.view.fit_to_window))
        # Moved Grid here
        menu.addSeparator()
        menu.addAction(
            Action(
                FIF.TILES,
                "Toggle Grid",
                triggered=self.view.toggle_grid))
        menu.addAction(
            Action(
                FIF.TILES,
                "Toggle Symmetry Mode",
                triggered=self.view.toggle_symmetry))
        btn.setMenu(menu)
        self._add_btn(btn)

    def build_design_menu(self):
        """Design Tools: Selection, Layers, Filters, Colors"""
        btn = DropDownPushButton("🎨 Design", self.view)
        menu = Menu(parent=self.view)

        # Selection
        menu.addAction(
            Action(
                FIF.CHECKBOX,
                "Select All",
                triggered=lambda: None))
        menu.addAction(Action(FIF.CANCEL, "Deselect", triggered=lambda: None))
        menu.addSeparator()

        # Layers
        menu.addAction(Action(FIF.ADD, "New Layer", triggered=lambda: None))
        menu.addAction(
            Action(
                FIF.DELETE,
                "Delete Layer",
                triggered=lambda: None))
        menu.addSeparator()

        # Filters
        menu.addAction(Action(FIF.BRUSH, "Blur", triggered=lambda: None))
        menu.addAction(Action(FIF.BRUSH, "Sharpen", triggered=lambda: None))
        menu.addSeparator()

        # Colors
        menu.addAction(
            Action(
                FIF.PALETTE,
                "Reduce to 8 Colors",
                triggered=self.view.apply_smart_quantize_8))
        menu.addAction(
            Action(
                FIF.PALETTE,
                "Reduce to 16 Colors",
                triggered=self.view.apply_smart_quantize_16))
        
        menu.addSeparator()

        # Adjustments Submenu
        adj_menu = Menu(title="Adjustments", parent=menu)
        adj_menu.addAction(Action(FIF.EDIT, "Curves", triggered=self.view.show_curves))
        adj_menu.addAction(Action(FIF.EDIT, "Levels", triggered=self.view.show_levels))
        adj_menu.addAction(Action(FIF.EDIT, "Channel Mixer", triggered=self.view.show_channel_mixer))
        adj_menu.addAction(Action(FIF.EDIT, "HSL / Saturation", triggered=self.view.show_hsl))
        adj_menu.addAction(Action(FIF.EDIT, "Posterize", triggered=self.view.show_posterize))
        adj_menu.addAction(Action(FIF.EDIT, "Threshold", triggered=self.view.show_threshold))
        adj_menu.addAction(Action(FIF.EDIT, "Solarize", triggered=self.view.show_solarize))
        menu.addMenu(adj_menu)

        # Filters Submenu
        filt_menu = Menu(title="Filters", parent=menu)
        filt_menu.addAction(Action(FIF.BRUSH, "Vignette", triggered=self.view.show_vignette))
        filt_menu.addAction(Action(FIF.BRUSH, "Film Grain", triggered=self.view.show_film_grain))
        filt_menu.addAction(Action(FIF.BRUSH, "Noise Reduction", triggered=self.view.show_noise_reduction))
        filt_menu.addAction(Action(FIF.BRUSH, "Pixelate", triggered=self.view.show_pixelate))
        filt_menu.addAction(Action(FIF.BRUSH, "Emboss", triggered=self.view.show_emboss))
        filt_menu.addAction(Action(FIF.BRUSH, "Halftone", triggered=self.view.show_halftone))
        menu.addMenu(filt_menu)


        btn.setMenu(menu)
        self._add_btn(btn)

    def build_image_menu(self):
        """Image Transforms: Rotate, Flip"""
        btn = DropDownPushButton("🖼️ Transform", self.view)
        menu = Menu(parent=self.view)
        menu.addAction(
            Action(
                FIF.ROTATE,
                "Rotate 90°",
                triggered=self.view.rotate_90))
        menu.addAction(
            Action(
                FIF.ROTATE,
                "Rotate 180°",
                triggered=self.view.rotate_180))
        menu.addSeparator()
        menu.addAction(
            Action(
                FIF.ROTATE,
                "Flip Horizontal",
                triggered=self.view.flip_h))
        menu.addAction(
            Action(
                FIF.ROTATE,
                "Flip Vertical",
                triggered=self.view.flip_v))
        btn.setMenu(menu)
        self._add_btn(btn)

    def build_textile_menu(self):
        btn = DropDownPushButton("Textile", self.view)
        menu = Menu(parent=self.view)
        menu.addAction(
            Action(
                FIF.TILES,
                "Detect Pattern",
                triggered=self.view.detect_pattern_from_image))
        menu.addAction(
            Action(
                FIF.TILES,
                "Show Weave Simulator",
                triggered=self.view.show_fabric_simulation))
        menu.addAction(
            Action(
                FIF.TILES,
                "Motif Repeater",
                triggered=self.view.show_motif_repeater))
        menu.addSeparator()
        menu.addAction(
            Action(
                FIF.SAVE,
                "Export to Loom",
                triggered=self.view.export_to_loom))
        btn.setMenu(menu)
        self._add_btn(btn)

    def build_ai_suite_menu(self):
        """Unified AI Suite Menu"""
        btn = DropDownPushButton("AI Suite", self.view)
        menu = Menu(parent=self.view)

        # Core AI Tools
        menu.addAction(
            Action(
                FIF.ROBOT,
                "AI Assistant (Chat)",
                triggered=self.view.activate_ai_chat))
        menu.addSeparator()

        # Generators
        menu.addAction(
            Action(
                FIF.ROBOT,
                "Pattern Generator",
                triggered=self.view.show_ai_pattern_gen))
        menu.addAction(
            Action(
                FIF.PENCIL_INK,
                "Sketch to Design (ControlNet)",
                triggered=self.view.generate_from_sketch_controlnet))
        menu.addSeparator()

        # Utilities
        menu.addAction(
            Action(
                FIF.ROBOT,
                "Auto-Segment",
                triggered=self.view.auto_segment))
        menu.addAction(
            Action(
                FIF.CUT,
                "Remove Background",
                triggered=self.view.apply_remove_background))
        menu.addAction(
            Action(
                FIF.PEOPLE,
                "Virtual Drape Prep (Human Seg)",
                triggered=self.view.apply_human_parsing))
        menu.addAction(
            Action(
                FIF.TILES,
                "Show Fabric Relief (3D)",
                triggered=self.view.apply_depth_map))
        menu.addAction(
            Action(
                FIF.ZOOM,
                "Upscale 4x",
                triggered=self.view.apply_ai_upscale_4x))
        menu.addSeparator()

        # Artistic
        menu.addAction(
            Action(
                FIF.BRUSH,
                "Style Transfer",
                triggered=self.view.apply_style_transfer))
        menu.addAction(
            Action(
                FIF.PALETTE,
                "Colorize B&W",
                triggered=self.view.apply_colorization))

        btn.setMenu(menu)
        self._add_btn(btn)

    def build_tools_menu(self):
        """Drawing & Editing Tools"""
        btn = DropDownPushButton("🛠️ Tools", self.view)
        menu = Menu(parent=self.view)

        # Drawing Sub-group
        draw_menu = Menu(title="Drawing", parent=menu)
        draw_menu.addAction(
            Action(
                FIF.BRUSH,
                "Brush",
                triggered=lambda: self.view.activate_brush()))
        draw_menu.addAction(
            Action(
                FIF.EDIT,
                "Pencil (1px)",
                triggered=lambda: self.view.activate_pencil()))
        draw_menu.addAction(
            Action(
                FIF.EDIT,
                "Eraser",
                triggered=lambda: self.view.activate_eraser()))
        menu.addMenu(draw_menu)

        # Shapes Sub-group
        shape_menu = Menu(title="Shapes", parent=menu)
        shape_menu.addAction(
            Action(
                FIF.CHECKBOX,
                "Rectangle",
                triggered=lambda: self.view.activate_shape_tool('rect')))
        shape_menu.addAction(
            Action(
                FIF.SYNC,
                "Circle",
                triggered=lambda: self.view.activate_shape_tool('oval')))
        shape_menu.addAction(
            Action(
                FIF.MENU,
                "Line",
                triggered=lambda: self.view.activate_shape_tool('line')))
        menu.addMenu(shape_menu)

        # Paint & Fill
        fill_menu = Menu(title="Paint & Fill", parent=menu)
        fill_menu.addAction(
            Action(
                FIF.BACKGROUND_FILL,
                "Flood Fill",
                triggered=lambda: self.view.activate_fill_tool()))
        fill_menu.addAction(
            Action(
                FIF.BRUSH,
                "Gradient",
                triggered=lambda: None))
        menu.addMenu(fill_menu)

        menu.addSeparator()

        # Utilities
        menu.addAction(Action(FIF.ZOOM, "Zoom Tool", triggered=lambda: None))
        menu.addAction(Action(FIF.MOVE, "Hand Tool", triggered=lambda: None))
        menu.addAction(
            Action(
                FIF.PALETTE,
                "Eyedropper",
                triggered=lambda: self.view.activate_eyedropper()))

        btn.setMenu(menu)
        self._add_btn(btn)

    def build_settings_menu(self):
        btn = DropDownPushButton("Settings", self.view)
        menu = Menu(parent=self.view)
        menu.addAction(
            Action(
                FIF.SETTING,
                "Application Settings",
                triggered=lambda: None))
        btn.setMenu(menu)
        self._add_btn(btn)

    def build_help_menu(self):
        btn = DropDownPushButton("Help", self.view)
        menu = Menu(parent=self.view)
        menu.addAction(
            Action(
                FIF.HELP,
                "Help & Support",
                triggered=lambda: None))
        menu.addAction(Action(FIF.INFO, "About", triggered=self.view.show_about_dialog))
        btn.setMenu(menu)
        self._add_btn(btn)
