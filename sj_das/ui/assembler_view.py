import os

import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QImage, QPixmap
from PyQt6.QtWidgets import (QComboBox, QFileDialog, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QScrollArea, QSpinBox, QVBoxLayout, QWidget)

from sj_das.core.assembler import AssemblerEngine
from sj_das.core.bmp_metadata import BMPMetadata
from sj_das.core.color_engine import ColorEngine
from sj_das.core.loom_engine import LoomEngine
from sj_das.core.smart_merge_engine import SmartMergeEngine
from sj_das.core.weave_engine import WeaveEngine


class DropZone(QLabel):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #7f8c8d;
                border-radius: 10px;
                background-color: #2c3e50;
                color: #bdc3c7;
                font-weight: bold;
                min-height: 100px;
                min-width: 100px;
            }
            QLabel:hover {
                background-color: #34495e;
                border-color: #3498db;
            }
        """)
        self.setAcceptDrops(True)
        self.image_path = None
        self.default_text = title

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.set_image(files[0])

    def set_image(self, path):
        self.image_path = path
        self.setText(os.path.basename(path))
        self.setStyleSheet(
            "border: 2px solid #27ae60; background-color: #2c3e50; color: white;")
        # Trigger parent callback if exists
        if hasattr(self, 'on_dropped') and self.on_dropped:
            self.on_dropped()


class AssemblerView(QWidget):
    def __init__(self):
        super().__init__()
        self.assembler = AssemblerEngine()
        self.weave_engine = WeaveEngine()
        self.color_engine = ColorEngine()
        self.loom_engine = LoomEngine()
        self.smart_assembler = SmartMergeEngine()
        self.loom_engine = LoomEngine()
        self.smart_assembler = SmartMergeEngine()
        self.assembled_image = None
        self.loom_ready_image = None  # Store loom-ready processed image
        self.nudge_x = 0
        self.nudge_y = 0
        self.init_ui()

    def on_component_dropped(self):
        """Trigger AI configuration when components change."""
        self.auto_configure()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # Left Panel: Configuration & Scroll Area
        config_scroll = QScrollArea()
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)

        # 1. Loom & Export Settings
        grp_loom = QGroupBox("1. Loom & Export Settings")
        loom_grid = QGridLayout()

        # Profile Selector
        from sj_das.core.loom_config import LoomConfigEngine
        self.loom_config_engine = LoomConfigEngine()

        self.combo_profile = QComboBox()
        self.combo_profile.addItems(
            self.loom_config_engine.get_formatted_names())
        self.combo_profile.currentIndexChanged.connect(self.on_profile_changed)

        # Sequence Number
        self.spin_seq = QSpinBox()
        self.spin_seq.setRange(1, 99)
        self.spin_seq.setValue(5)
        self.spin_seq.setPrefix("Seq: ")

        # Design Type
        self.combo_type = QComboBox()
        self.combo_type.addItems(
            ["Body", "Border", "Pallu", "Full Saree", "Blouse"])

        # Layout Input Grid
        loom_grid.addWidget(QLabel("Machine Profile:"), 0, 0)
        loom_grid.addWidget(self.combo_profile, 0, 1, 1, 3)

        loom_grid.addWidget(QLabel("Sequence:"), 1, 0)
        loom_grid.addWidget(self.spin_seq, 1, 1)
        loom_grid.addWidget(QLabel("Type:"), 1, 2)
        loom_grid.addWidget(self.combo_type, 1, 3)

        # Create Spinboxes (restoring these too as they might be
        # missing/undefined in local scope if I deleted the block)
        self.spin_reed = QSpinBox()
        self.spin_reed.setRange(1, 500)
        self.spin_reed.setValue(100)
        self.spin_reed.setSuffix(" Reed")

        self.spin_acchu = QSpinBox()
        self.spin_acchu.setRange(100, 10000)
        self.spin_acchu.setValue(2400)
        self.spin_acchu.setSuffix(" hooks")

        self.spin_kali = QSpinBox()
        self.spin_kali.setRange(1, 20)
        self.spin_kali.setValue(1)
        self.spin_kali.setPrefix("Repeats: ")

        self.spin_locking = QSpinBox()
        self.spin_locking.setRange(0, 100)
        self.spin_locking.setValue(4)
        self.spin_locking.setSuffix(" px")

        loom_grid.addWidget(QLabel("Reed:"), 2, 0)
        loom_grid.addWidget(self.spin_reed, 2, 1)
        loom_grid.addWidget(QLabel("Total Hooks:"), 2, 2)
        loom_grid.addWidget(self.spin_acchu, 2, 3)
        loom_grid.addWidget(QLabel("Repeats:"), 3, 0)
        loom_grid.addWidget(self.spin_kali, 3, 1)
        loom_grid.addWidget(QLabel("Locking:"), 3, 2)
        loom_grid.addWidget(self.spin_locking, 3, 3)

        grp_loom.setLayout(loom_grid)
        config_layout.addWidget(grp_loom)

        # Merged Loom & Export Settings above

        # 2. Drop Zones
        grp_files = QGroupBox("2. Design Components (Drag & Drop)")
        files_layout = QGridLayout()

        # Initialize DropZones with callback
        self.drop_body = DropZone("Body")
        self.drop_body.on_dropped = self.on_component_dropped

        self.drop_border_l = DropZone("Left Border")
        self.drop_border_l.on_dropped = self.on_component_dropped

        self.drop_border_r = DropZone("Right Border")
        self.drop_border_r.on_dropped = self.on_component_dropped

        self.drop_pallu = DropZone("Pallu")
        # Pallu doesn't affect Body repeats, but could affect flow.

        self.drop_skirt = DropZone("Skirt (Optional)")

        files_layout.addWidget(self.drop_border_l, 0, 0, 2, 1)
        files_layout.addWidget(self.drop_body, 0, 1)
        files_layout.addWidget(self.drop_skirt, 1, 1)
        files_layout.addWidget(self.drop_border_r, 0, 2, 2, 1)
        files_layout.addWidget(self.drop_pallu, 2, 0, 1, 3)

        grp_files.setLayout(files_layout)
        config_layout.addWidget(grp_files)

        # Title
        title = QLabel("Saree Assembly Mode")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #fff; padding: 10px;")
        config_layout.addWidget(title)

        # Details
        info = QLabel(
            "Auto-Assembly is Active. Drop designs to automatically calculate Repeats (Khali) and Locking."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #aaa; padding: 10px;")
        config_layout.addWidget(info)

        # Removed Redundant "AI Assemble" Button
        # We rely on "Assemble Saree" + Drop Event Logic

        # Configure Button Layout (Just Stretch now)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        config_layout.addLayout(btn_layout)

        # 3. Manufacturing Settings (Unified)
        grp_mfg = QGroupBox("3. Manufacturing (Optimize & Weave)")
        mfg_layout = QGridLayout()

        # Weave Selection
        mfg_layout.addWidget(QLabel("Weave Structure:"), 0, 0)
        self.combo_weave = QComboBox()
        self.combo_weave.addItems(self.weave_engine.get_weave_names())
        mfg_layout.addWidget(self.combo_weave, 0, 1)

        # Yarn Configuration (Quantization)
        mfg_layout.addWidget(QLabel("Number of Yarns:"), 1, 0)
        self.spin_colors = QSpinBox()
        self.spin_colors.setRange(2, 8)  # Usually 2-8 yarns/wefts
        self.spin_colors.setValue(3)
        self.spin_colors.setPrefix("Yarns: ")
        self.spin_colors.setToolTip(
            "Defines how many distinct yarn 'colors' or indices to reduce the image to.")
        mfg_layout.addWidget(self.spin_colors, 1, 1)

        grp_mfg.setLayout(mfg_layout)
        grp_mfg.setLayout(mfg_layout)
        config_layout.addWidget(grp_mfg)

        # Smart Merge Toggle
        from PyQt6.QtWidgets import QCheckBox
        self.chk_smart_merge = QCheckBox("Enable DreamTex Smart Merge")
        self.chk_smart_merge.setChecked(True)
        self.chk_smart_merge.setStyleSheet(
            "font-weight: bold; color: #f1c40f;")
        config_layout.addWidget(self.chk_smart_merge)

        # Status
        self.lbl_status = QLabel("Ready. Drop files to auto-configure.")
        self.lbl_status.setStyleSheet("color: #888; padding: 10px;")
        config_layout.addWidget(self.lbl_status)

        # 3. Actions
        btn_assemble = QPushButton("ASSEMBLE COMPLETE SAREE")
        btn_assemble.setStyleSheet(
            "background-color: #3498db; font-size: 16px; font-weight:bold; padding: 15px;")
        btn_assemble.clicked.connect(self.assemble)
        config_layout.addWidget(btn_assemble)

        btn_export = QPushButton("Export Merged Design")
        btn_export.setStyleSheet(
            "background-color: #27ae60; font-size: 16px; padding: 10px;")
        btn_export.clicked.connect(self.export)
        config_layout.addWidget(btn_export)

        config_layout.addStretch()
        config_widget.setLayout(config_layout)

        config_scroll.setWidget(config_widget)
        config_scroll.setWidgetResizable(True)
        config_scroll.setFixedWidth(450)

        layout.addWidget(config_scroll)

        # Right Panel: Preview
        self.preview_label = QLabel("Preview Area")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(
            "background-color: #121212; border: 1px solid #333;")

        preview_scroll = QScrollArea()
        preview_scroll.setWidget(self.preview_label)
        preview_scroll.setWidgetResizable(True)

        # Middle: Preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(preview_scroll)

        # Interactive Controls (Smart Assembly 2.0)
        controls_layout = QHBoxLayout()

        btn_drape = QPushButton("Simulate Drape 👗")
        btn_drape.clicked.connect(self.simulate_drape)
        controls_layout.addWidget(btn_drape)

        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Nudge Alignment:"))

        btn_left = QPushButton("←")
        btn_left.clicked.connect(lambda: self.nudge(-5, 0))
        btn_right = QPushButton("→")
        btn_right.clicked.connect(lambda: self.nudge(5, 0))
        btn_up = QPushButton("↑")
        btn_up.clicked.connect(lambda: self.nudge(0, -5))
        btn_down = QPushButton("↓")
        btn_down.clicked.connect(lambda: self.nudge(0, 5))

        for b in [btn_left, btn_right, btn_up, btn_down]:
            b.setFixedWidth(30)
            controls_layout.addWidget(b)

        preview_layout.addLayout(controls_layout)

        layout.addLayout(preview_layout, 1)  # Stretch factor 1

        # Right: AI Insights
        from sj_das.ui.panels.ai_insights_panel import AIInsightsPanel
        self.ai_panel = AIInsightsPanel()
        self.ai_panel.apply_suggestion.connect(self.handle_ai_suggestion)
        self.ai_panel.setFixedWidth(300)
        layout.addWidget(self.ai_panel)

    def assemble(self):
        """AI-Enhanced Assembly with automatic loom-ready processing."""
        components = {
            'body': self.drop_body.image_path,
            'border_l': self.drop_border_l.image_path,
            'border_r': self.drop_border_r.image_path,
            'pallu': self.drop_pallu.image_path,
            'skirt': self.drop_skirt.image_path
        }

        config = {
            'acchu': self.spin_acchu.value(),
            'kali': self.spin_kali.value(),
            'locking': self.spin_locking.value(),
            'reed': self.spin_reed.value(),
            'weave_name': self.combo_weave.currentText(),
            'yarn_count': self.spin_colors.value()
        }

        try:
            if self.chk_smart_merge.isChecked():
                self.lbl_status.setText("🤖 Running AI-Enhanced Assembly...")
                QApplication.processEvents()

                # Apply Nudge
                config['nudge_x'] = self.nudge_x
                config['nudge_y'] = self.nudge_y

                # Step 1: Smart Assembly with AI enhancements
                self.assembled_image = self.smart_assembler.smart_assemble(
                    components, config)
                self.lbl_status.setText(
                    "✅ Assembly complete! Preparing loom-ready export...")
                QApplication.processEvents()

                # Step 2: Automatic loom-ready processing
                self.loom_ready_image = self.smart_assembler.prepare_loom_ready_export(
                    self.assembled_image, config
                )
                self.lbl_status.setText(
                    "✅ Loom-ready image prepared! Ready to export.")

            else:
                self.lbl_status.setText("Running Standard Assembly...")
                self.assembled_image = self.assembler.assemble_saree(
                    components, config)
                self.loom_ready_image = None

            self.show_preview(self.assembled_image)

            # Run AI Checks
            self.run_analysis(self.assembled_image)

            # Show Production Analytics
            self.show_production_report(self.assembled_image)

            # Success message with next steps
            msg = "✅ Assembly Complete!\n\n"
            if self.loom_ready_image is not None:
                msg += "🎯 Loom-ready BMP is prepared with:\n"
                msg += f"  • Exact hook count: {config['acchu']}\n"
                msg += f"  • Weave pattern: {config['weave_name']}\n"
                msg += f"  • Yarn colors: {config['yarn_count']}\n\n"
                msg += "Click 'Export' to save the production-ready BMP file!"
            else:
                msg += "Click 'Export' to save the assembled design."

            QMessageBox.information(self, "Success", msg)

        except Exception as e:
            import traceback
            error_msg = f"Assembly Error: {str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Assembly Error", error_msg)
            self.lbl_status.setText(f"❌ Error: {str(e)}")

    def show_production_report(self, img):
        """Generates a professional production estimate (ThinkBig Feature)."""
        if img is None:
            return

        h, w = img.shape[:2]

        # 1. Loom Time Estimate
        rpm = 320  # Standard Jacquard Speed
        efficiency = 0.85  # 85% efficiency
        minutes = h / (rpm * efficiency)

        # 2. Yarn Estimate (Approximation)
        # Avg pick length = width * 1.1 (crimp)
        # Total meters = picks * width(m)
        width_m = 1.2  # Standard saree width
        total_weft_m = h * width_m

        msg = (
            f"<h3>🏭 Production Analytics</h3>"
            f"<b>Design Dimensions:</b> {w} Hooks x {h} Picks<br>"
            f"----------------------------------------<br>"
            f"<b>⏱️ Estimated Weave Time:</b> {minutes:.1f} minutes<br>"
            f"<i>(at {rpm} RPM, {int(efficiency*100)}% Eff)</i><br><br>"
            f"<b>🧵 Yarn Consumption:</b><br>"
            f"• Weft Needed: ~{total_weft_m:.0f} meters<br>"
            f"• Warp Length: {h/100:.2f} meters (approx)<br>"
            f"----------------------------------------<br>"
            f"<i>Ready for {self.combo_profile.currentText()}</i>"
        )

        QMessageBox.information(self, "Production Report", msg)

    def show_preview(self, img_array):
        height, width, channel = img_array.shape
        bytes_per_line = 3 * width
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        q_img = QImage(
            img_rgb.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(q_img)

        # Scale for preview if too large
        if width > 1000 or height > 1000:
            pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

        self.preview_label.setPixmap(pixmap)

    def export(self):
        """Export with automatic loom-ready processing."""
        if self.assembled_image is None:
            QMessageBox.warning(
                self, "No Image", "Please assemble the design first.")
            return

        # Smart Filename Generation
        seq = self.spin_seq.value()
        des_type = self.combo_type.currentText()
        reed = self.spin_reed.value()
        repeats = self.spin_kali.value()

        total_width = self.assembled_image.shape[1]

        # Breakdown string
        if repeats > 1:
            single_width = total_width // repeats
            if single_width * repeats == total_width:
                breakdown = "+".join([str(single_width)] * repeats)
            else:
                breakdown = str(total_width)
        else:
            breakdown = str(total_width)

        default_name = f"{seq:02d} {des_type} {breakdown} {reed} Reed.bmp"

        # File Dialog
        file_name, filter_used = QFileDialog.getSaveFileName(
            self,
            "Save Production Design",
            default_name,
            "Loom BMP (*.bmp);;PNG Image (*.png);;Preview Image (*.jpg)"
        )

        if not file_name:
            return

        # Use automated loom-ready export for BMPs
        if file_name.lower().endswith(".bmp"):
            try:
                # Use loom-ready image if available, otherwise process now
                if self.loom_ready_image is not None:
                    # Already processed by smart assembler
                    export_image = self.loom_ready_image
                    QMessageBox.information(
                        self, "Info", "Using pre-processed loom-ready image")
                else:
                    # Process now
                    config = {
                        'acchu': self.spin_acchu.value(),
                        'weave_name': self.combo_weave.currentText(),
                        'yarn_count': self.spin_colors.value(),
                        'reed': reed,
                        'kali': repeats,
                        'locking': self.spin_locking.value()
                    }
                    export_image = self.smart_assembler.prepare_loom_ready_export(
                        self.assembled_image, config
                    )

                # Export using SmartMergeEngine's built-in export
                config = {
                    'acchu': self.spin_acchu.value(),
                    'reed': reed,
                    'kali': repeats,
                    'locking': self.spin_locking.value(),
                    'yarn_count': self.spin_colors.value()
                }

                success = self.smart_assembler.export_loom_bmp(
                    export_image, file_name, config)

                if success:
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"✅ Loom-Ready BMP saved!\n\n"
                        f"File: {file_name}\n"
                        f"Hooks: {export_image.shape[1]}\n"
                        f"Picks: {export_image.shape[0]}\n\n"
                        f"Ready to feed into loom!"
                    )
                else:
                    QMessageBox.critical(
                        self, "Export Failed", "Could not save BMP file.")

            except Exception as e:
                import traceback
                error_msg = f"Export Error: {str(e)}\n\n{traceback.format_exc()}"
                QMessageBox.critical(self, "Export Error", error_msg)

        else:
            # Fallback for PNG/JPG (Visual Only)
            cv2.imwrite(file_name, self.assembled_image)
            QMessageBox.information(
                self,
                "Export Successful",
                f"Saved preview to {file_name}")

    def handle_ai_suggestion(self, action: str, data: dict):
        """Handle AI actions from the panel."""
        if action == 'refresh_analysis':
            if self.assembled_image is not None:
                self.run_analysis(self.assembled_image)
            else:
                QMessageBox.warning(
                    self, "No Assembly", "Please assemble the saree first.")
        else:
            QMessageBox.information(
                self, "AI Action", f"Action '{action}' triggered.")

    def run_analysis(self, image):
        """Run geometric and design checks on the assembled saree."""
        try:
            h, w = image.shape[:2]

            # 1. Prediction (Mock for now, or use real model if trained on full
            # sarees)
            prediction = {
                'pattern': {'type': 'Traditional Saree', 'confidence': 0.95},
                'weave': {'type': 'Unknown', 'confidence': 0.0},
                'segmentation': {'confidence': 1.0}
            }

            # 2. Logic-based Suggestions
            suggestions = []

            # Check Aspect Ratio (Standard Saree ~ 1.1m x 6.2m -> Ratio ~ 5.5)
            # In hooks/pixels: 2400 (4800) x ?
            w / h if h > 0 else 0
            # Saree usually Landscape in real life, but Portrait in Loom Files (Vertical warp)
            # Loom Machine: Width = Hooks (e.g. 2400), Height = Picks (e.g. 10000+)
            # So Image is Portrait (Tall).

            if h < w:
                suggestions.append({
                    'title': 'Orientation Warning',
                    'message': 'Saree design is wider than it is tall. Jacquard designs are usually vertical (Picks > Hooks). Verification recommended.',
                    'priority': 'medium',
                    'icon': '⚠️'
                })

            # Check Pixel Dimensions vs Hooks
            acchu = self.spin_acchu.value()
            if w != acchu:
                suggestions.append({
                    'title': 'Hook Count Mismatch',
                    'message': f'Assembled width ({w}px) does not match Acchu settings ({acchu} hooks). This mimics a resize.',
                    'priority': 'high',
                    'icon': '🚫'
                })

            # Check Component Alignment (Border Repeats)
            body_path = self.drop_body.image_path
            if body_path:
                body_img = cv2.imread(body_path)
                if body_img is not None:
                    _bw, bh = body_img.shape[1], body_img.shape[0]
                    # Check if body height tiles cleanly into total height
                    if h % bh != 0:
                        suggestions.append({
                            'title': 'Vertical Tile Warning',
                            'message': f'Total height ({h}) is not a multiple of body height ({bh}). Check Locking.',
                            'priority': 'low',
                            'icon': '📏'
                        })

            # --- MERGED MANUFACTURER LOGIC ---
            # 1. Float Check (Vectorized)
            float_suggestions = self.check_floats(image)
            suggestions.extend(float_suggestions)

            # 2. Cost Estimate (MOVED TO TWIN+ MODE)
            # cost_report = self.estimate_cost(image)
            # Add cost as an info suggestion
            # suggestions.append({
            #    'title': 'Yarn Estimate',
            #    'message': cost_report,
            #    'priority': 'info',
            #    'icon': '💰'
            # })

            self.ai_panel.update_insights(prediction, suggestions)

        except Exception as e:
            print(f"AI Analysis Error: {e}")

    def check_floats(self, img_color):
        """Analyzes floats (long runs of same color). Returns list of suggestions."""
        try:
            img = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

            # Vectorized Run Length Calculation
            # Iterate rows but use diff for speed
            max_float = 0

            # Sample every 10th row for speed in large files, or full scan?
            # Full scan is safer for manufacturing.
            for row in img:
                d = np.diff(row) != 0
                indices = np.where(d)[0] + 1
                if len(indices) == 0:
                    current_max = len(row)
                else:
                    all_indices = np.concatenate(([0], indices, [len(row)]))
                    lengths = np.diff(all_indices)
                    current_max = lengths.max()
                if current_max > max_float:
                    max_float = current_max

            suggestions = []
            priority = 'low'
            icon = '✅'
            msg = f"Max float length is {max_float}px. Safe for weaving."

            if max_float > 200:
                priority = 'high'
                icon = '❌'
                msg = f"CRITICAL: Found floats of {max_float}px. Loom will break thread."
            elif max_float > 150:
                priority = 'medium'
                icon = '⚠️'
                msg = f"WARNING: Floats up to {max_float}px. High tension risk."

            suggestions.append({
                'title': 'Float Analysis (Auto)',
                'message': msg,
                'priority': priority,
                'icon': icon
            })
            return suggestions
        except Exception:
            return []

    def on_profile_changed(self, index):
        """Update inputs based on selected loom profile."""
        try:
            profile_name = self.combo_profile.currentText()
            key = self.loom_config_engine.get_key_from_name(profile_name)
            profile = self.loom_config_engine.get_profile(key)

            # Auto-fill hooks (Acchu)
            self.spin_acchu.setValue(profile.default_hooks)
            self.spin_acchu.setToolTip(
                f"Set by profile: {profile.description}")
        except Exception:
            pass

    def nudge(self, dx, dy):
        """Interactive Nudge Implementation"""
        self.nudge_x += dx
        self.nudge_y += dy
        self.assemble()  # Re-run simple assembly

    def simulate_drape(self):
        """Simulate Drape on a Model (Placeholder/Mock)"""
        if self.assembled_image is None:
            return
        QMessageBox.information(
            self,
            "Drape Simulation",
            "Showing 3D Drape Preview (Mockup)...")
        # In real implementation: Warp image onto a pre-defined mask.

    def auto_configure(self):
        """
        AI-driven configuration: Automatically determines parameters.
        1. Analyzes components (Body Width vs Acchu).
        2. Calculates optimal Khali (Repeats) and Locking.
        3. Configures inputs automatically.
        """
        # Gather inputs
        body_path = self.drop_body.image_path
        if not body_path:
            return  # Silent return if no body (waiting for drop)

        try:
            # 1. Analyze Body Image
            body_img = cv2.imread(body_path)
            if body_img is None:
                return

            bw = body_img.shape[1]
            total_hooks = self.spin_acchu.value()

            # Check Borders
            border_w = 0
            if self.drop_border_l.image_path:
                b_img = cv2.imread(self.drop_border_l.image_path)
                if b_img is not None:
                    border_w += b_img.shape[1]

            if self.drop_border_r.image_path:
                b_img = cv2.imread(self.drop_border_r.image_path)
                if b_img is not None:
                    border_w += b_img.shape[1]

            # 2. Derive Configuration
            available_space = total_hooks - border_w
            if available_space <= 0:
                # Borders exceed total hooks, do nothing or warn?
                # Let's just return, user will see error on assemble
                return

            # Smart Khali Calculation
            # If body matches space closely, Khali=1
            # If body is much smaller, calculate repeats needed to fill space

            optimal_khali = 1
            if bw < available_space:
                optimal_khali = round(available_space / bw)
                if optimal_khali < 1:
                    optimal_khali = 1

            # Locking Logic:
            # If we are repeating, we usually need locking to seamless join
            optimal_locking = 4 if optimal_khali > 1 else 0

            # 3. Apply Configuration
            self.spin_kali.setValue(optimal_khali)
            self.spin_locking.setValue(optimal_locking)

            # Feedback
            self.lbl_status.setText(
                f"🤖 AI Configured: {optimal_khali} Repeats for {bw}px body in {available_space}px space."
            )

            # No longer auto-assembling; just configuring.

        except Exception as e:
            print(f"Auto-config error: {e}")
