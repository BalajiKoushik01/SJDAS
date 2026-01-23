"""
Advanced Generation UI Panel - Interface for all three generation methods
Provides intuitive design generation from text prompts
"""

import cv2
import numpy as np
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QImage, QPixmap
from PyQt6.QtWidgets import (QButtonGroup, QCheckBox, QFrame, QGroupBox,
                             QHBoxLayout, QLabel, QProgressBar, QPushButton,
                             QRadioButton, QScrollArea, QSpinBox, QTextEdit,
                             QVBoxLayout, QWidget)


class GenerationWorker(QThread):
    """Background worker for design generation."""

    finished = pyqtSignal(list)  # List of generated images
    progress = pyqtSignal(str)  # Progress message
    error = pyqtSignal(str)  # Error message

    def __init__(self, prompt: str, method: str, num_variations: int = 1):
        super().__init__()
        self.prompt = prompt
        self.method = method
        self.num_variations = num_variations

    def run(self):
        """Generate design in background."""
        try:
            from ..ai.procedural_generator import get_procedural_generator
            from ..ai.prompt_parser import get_prompt_parser
            from ..ai.stable_diffusion_generator import (get_hybrid_generator,
                                                         get_sd_generator)

            # Parse prompt
            self.progress.emit("Parsing prompt...")
            parser = get_prompt_parser()
            params = parser.parse(self.prompt)

            results = []

            if self.method == 'procedural':
                self.progress.emit("Generating with procedural method...")
                generator = get_procedural_generator()

                for i in range(self.num_variations):
                    self.progress.emit(
                        f"Creating variation {i+1}/{self.num_variations}...")
                    design = generator.generate_design(params)
                    results.append(design)

            elif self.method == 'stable_diffusion':
                self.progress.emit("Loading Stable Diffusion...")
                generator = get_sd_generator()

                if not generator.load_model():
                    raise Exception("Failed to load Stable Diffusion model")

                self.progress.emit("Generating with AI...")
                results = generator.generate(params, self.num_variations)

            elif self.method == 'hybrid':
                self.progress.emit("Generating hybrid design...")
                generator = get_hybrid_generator()

                for i in range(self.num_variations):
                    self.progress.emit(
                        f"Creating variation {i+1}/{self.num_variations}...")
                    design = generator.generate(params, use_ai_variation=True)
                    results.append(design)

            if results:
                self.progress.emit("Complete!")
                self.finished.emit(results)
            else:
                self.error.emit("No designs were generated")

        except Exception as e:
            self.error.emit(f"Generation error: {str(e)}")


class GenerationPanel(QWidget):
    """Advanced UI panel for design generation."""

    design_generated = pyqtSignal(np.ndarray)  # Emitted when design is ready

    def __init__(self):
        super().__init__()
        self.current_results = []
        self.generation_worker = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("✨ AI Design Generator")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Prompt input
        prompt_label = QLabel("📝 Describe your design:")
        prompt_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(prompt_label)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Example: Create a red and gold Kanchipuram bridal border "
            "with peacock motifs, 6 inches wide, elaborate zari work"
        )
        self.prompt_input.setMaximumHeight(100)
        self.prompt_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 8px;
                background: #2d2d2d;
                color: white;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.prompt_input)

        # Quick templates
        templates_label = QLabel("🎨 Quick Templates:")
        layout.addWidget(templates_label)

        templates_layout = QHBoxLayout()
        templates = [
            ("Bridal Border",
             "Traditional bridal border, red and gold, elaborate jeri work, 6 inches"),
            ("Festival Pallu",
             "Festive pallu design, vibrant colors, temple motifs, silk weave"),
            ("Casual Border", "Simple border for daily wear, geometric patterns, 3 inches"),
            ("Temple Design",
             "Temple architecture motifs, traditional style, detailed work")
        ]

        for name, prompt in templates:
            btn = QPushButton(name)
            btn.clicked.connect(
                lambda checked,
                p=prompt: self.prompt_input.setText(p))
            btn.setStyleSheet("""
                QPushButton {
                    background: #3d3d3d;
                    border: 1px solid #555;
                    padding: 6px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background: #4d4d4d;
                }
            """)
            templates_layout.addWidget(btn)

        layout.addLayout(templates_layout)

        # Generation method selection
        method_group = QGroupBox("Generation Method")
        method_layout = QVBoxLayout()

        self.method_group = QButtonGroup()

        # Procedural
        self.radio_procedural = QRadioButton("⚡ Procedural (Fast - 1 second)")
        self.radio_procedural.setToolTip(
            "Fast algorithmic generation, 100% loom-compatible")
        self.radio_procedural.setChecked(True)
        self.method_group.addButton(self.radio_procedural)
        method_layout.addWidget(self.radio_procedural)

        procedural_desc = QLabel(
            "   • Instant generation\n   • Perfect loom compatibility\n   • Pre-defined motif library")
        procedural_desc.setStyleSheet(
            "color: #aaa; font-size: 9pt; padding-left: 20px;")
        method_layout.addWidget(procedural_desc)

        # Hybrid
        self.radio_hybrid = QRadioButton("🎯 Hybrid (Balanced - 3-5 seconds)")
        self.radio_hybrid.setToolTip("Combines templates with AI variation")
        self.method_group.addButton(self.radio_hybrid)
        method_layout.addWidget(self.radio_hybrid)

        hybrid_desc = QLabel(
            "   • Fast with creativity\n   • 95% loom-compatible\n   • AI-enhanced patterns")
        hybrid_desc.setStyleSheet(
            "color: #aaa; font-size: 9pt; padding-left: 20px;")
        method_layout.addWidget(hybrid_desc)

        # Stable Diffusion
        self.radio_sd = QRadioButton(
            "🤖 Stable Diffusion (Creative - 10-30 seconds)")
        self.radio_sd.setToolTip(
            "AI image generation - most creative but may need refinement")
        self.method_group.addButton(self.radio_sd)
        method_layout.addWidget(self.radio_sd)

        sd_desc = QLabel(
            "   • Photorealistic results\n   • Unlimited creativity\n   • Requires GPU recommended")
        sd_desc.setStyleSheet(
            "color: #aaa; font-size: 9pt; padding-left: 20px;")
        method_layout.addWidget(sd_desc)

        method_group.setLayout(method_layout)
        layout.addWidget(method_group)

        # Options
        options_layout = QHBoxLayout()

        options_layout.addWidget(QLabel("Variations:"))
        self.spin_variations = QSpinBox()
        self.spin_variations.setRange(1, 4)
        self.spin_variations.setValue(1)
        self.spin_variations.setToolTip(
            "Number of design variations to generate")
        options_layout.addWidget(self.spin_variations)

        options_layout.addStretch()

        self.check_auto_refine = QCheckBox("Auto-refine for loom")
        self.check_auto_refine.setChecked(True)
        self.check_auto_refine.setToolTip(
            "Automatically optimize design for loom compatibility")
        options_layout.addWidget(self.check_auto_refine)

        layout.addLayout(options_layout)

        # Generate button
        self.gen_button = QPushButton("🎨 Generate Design")
        self.gen_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.gen_button.setMinimumHeight(50)
        self.gen_button.clicked.connect(self.start_generation)
        self.gen_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #FFD700, stop:1 #FFA500);
                color: black;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #FFA500, stop:1 #FFD700);
            }
            QPushButton:disabled {
                background: #555;
                color: #888;
            }
        """)
        layout.addWidget(self.gen_button)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("color: #FFD700;")
        layout.addWidget(self.progress_label)

        # Results preview (scrollable)
        results_label = QLabel("Generated Designs:")
        results_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(results_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)

        self.results_widget = QWidget()
        self.results_layout = QHBoxLayout(self.results_widget)
        self.results_layout.setSpacing(10)

        scroll.setWidget(self.results_widget)
        layout.addWidget(scroll)

        layout.addStretch()

    def start_generation(self):
        """Start design generation in background."""
        prompt = self.prompt_input.toPlainText().strip()

        if not prompt:
            self.progress_label.setText("⚠️ Please enter a design description")
            self.progress_label.setStyleSheet("color: #FF6B6B;")
            return

        # Determine method
        if self.radio_procedural.isChecked():
            method = 'procedural'
        elif self.radio_hybrid.isChecked():
            method = 'hybrid'
        else:
            method = 'stable_diffusion'

        num_variations = self.spin_variations.value()

        # Update UI
        self.gen_button.setEnabled(False)
        self.progress_bar.show()
        self.progress_label.setText("Starting generation...")
        self.progress_label.setStyleSheet("color: #FFD700;")

        # Clear previous results
        self._clear_results()

        # Start worker
        self.generation_worker = GenerationWorker(
            prompt, method, num_variations)
        self.generation_worker.progress.connect(self.on_progress)
        self.generation_worker.finished.connect(self.on_finished)
        self.generation_worker.error.connect(self.on_error)
        self.generation_worker.start()

    def on_progress(self, message: str):
        """Update progress display."""
        self.progress_label.setText(message)

    def on_finished(self, results: list):
        """Handle generation completion."""
        self.progress_bar.hide()
        self.gen_button.setEnabled(True)

        if not results:
            self.progress_label.setText("❌ No designs generated")
            self.progress_label.setStyleSheet("color: #FF6B6B;")
            return

        self.progress_label.setText(f"✅ Generated {len(results)} design(s)!")
        self.progress_label.setStyleSheet("color: #4CAF50;")

        self.current_results = results
        self._display_results(results)

    def on_error(self, error_msg: str):
        """Handle generation error."""
        self.progress_bar.hide()
        self.gen_button.setEnabled(True)
        self.progress_label.setText(f"❌ {error_msg}")
        self.progress_label.setStyleSheet("color: #FF6B6B;")

    def _display_results(self, results: list):
        """Display generated designs."""
        for img in results:
            # Create preview card
            card = self._create_result_card(img)
            self.results_layout.addWidget(card)

    def _create_result_card(self, image: np.ndarray) -> QFrame:
        """Create a result preview card."""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background: #2d2d2d;
                border: 2px solid #444;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(card)

        # Preview image
        h, w = image.shape[:2]
        scale = min(200 / h, 150 / w)
        preview_h = int(h * scale)
        preview_w = int(w * scale)

        preview = cv2.resize(image, (preview_w, preview_h))

        # Convert to QPixmap
        if len(preview.shape) == 3:
            height, width, channel = preview.shape
            bytes_per_line = 3 * width
            q_img = QImage(
                preview.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888)
        else:
            height, width = preview.shape
            bytes_per_line = width
            q_img = QImage(
                preview.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_Grayscale8)

        pixmap = QPixmap.fromImage(q_img)

        img_label = QLabel()
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(img_label)

        # Use button
        use_btn = QPushButton("✅ Use This Design")
        use_btn.clicked.connect(lambda: self.design_generated.emit(image))
        use_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        layout.addWidget(use_btn)

        return card

    def _clear_results(self):
        """Clear previous results."""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
