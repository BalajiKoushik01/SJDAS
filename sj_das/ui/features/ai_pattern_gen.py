import cv2
import numpy as np
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                             QFormLayout, QLabel, QLineEdit, QPushButton,
                             QTabWidget, QVBoxLayout, QWidget)

# Import AI Backend
from sj_das.ai.stable_diffusion_generator import get_hybrid_generator


# Mock DesignParameters if not available easily (or check prompt_parser.py)
# Actually, let's create a simple dataclass adapter here to avoid complex
# imports if prompt_parser is tricky
class SimpleDesignParams:
    def __init__(self, design_type, occasion, style,
                 motifs, colors, weave, complexity):
        self.design_type = design_type
        self.occasion = occasion
        self.style = style
        self.motifs = motifs
        self.colors = colors
        self.weave = weave
        self.complexity = complexity
        self.width_mm = 512  # pixels in this context
        self.length_mm = 512


class AIPatternGen:
    """
    Intelligent Pattern Generator for Textile Design.

    Features:
    - **Hybrid Architecture**: Combines Procedural Algorithms with Stable Diffusion.
    - **Context Awareness**: Generates designs based on 'Occasion', 'Region', and 'Weave'.
    - **Seamless Integration**: Directly updates the Editor Canvas.

    Usage:
    >>> generator = AIPatternGen(editor_instance)
    >>> generator.show_dialog()
    """

    def __init__(self, editor):
        self.editor = editor
        self.generator = get_hybrid_generator()

    def show_dialog(self):
        dialog = AIPatternDialog(self.generator)
        if dialog.exec():
            img = dialog.get_result_image()
            if img is not None:
                self._update_editor(img)

    def _update_editor(self, cv_img):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bpl = ch * w
        qimg = QImage(rgb.data, w, h, bpl, QImage.Format.Format_RGB888).copy()
        self.editor.set_image(qimg)
        self.editor.mask_updated.emit()


class GenerationWorker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, generator, params, use_ai, use_flux):
        super().__init__()
        self.generator = generator
        self.params = params
        self.use_ai = use_ai
        self.use_flux = use_flux

    def run(self):
        # Generate
        try:
            if self.use_flux:
                # Use Flux.1 (SOTA)
                from sj_das.core.engines.generative.flux_engine import \
                    FluxEngine

                # Note: FluxEngine handles model loading internally
                flux = FluxEngine()
                prompt = f"{self.params.design_type} design with {', '.join(self.params.motifs)} in {', '.join(self.params.colors)}, high quality, textile pattern"
                res = flux.generate(prompt, width=512, height=512)
            else:
                res = self.generator.generate(
                    self.params, use_ai_variation=self.use_ai)
            self.finished.emit(res)
        except Exception as e:
            print(f"Gen Error: {e}")
            self.finished.emit(None)


class AIPatternDialog(QDialog):
    def __init__(self, generator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Design Generator (Smart)")
        self.resize(400, 500)
        self.generator = generator
        self.result_img = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["border", "pallu", "blouse", "full_saree"])
        form.addRow("Design Section:", self.cmb_type)

        self.cmb_style = QComboBox()
        self.cmb_style.addItems(
            ["kanchipuram", "banarasi", "paithani", "traditional"])
        form.addRow("Regional Style:", self.cmb_style)

        self.cmb_motif = QComboBox()
        self.cmb_motif.addItems(
            ["peacock", "mango", "lotus", "temple", "geometric", "elephant"])
        form.addRow("Primary Motif:", self.cmb_motif)

        self.cmb_occasion = QComboBox()
        self.cmb_occasion.addItems(["bridal", "festive", "casual", "formal"])
        form.addRow("Occasion:", self.cmb_occasion)

        self.txt_colors = QLineEdit("red, gold")
        self.txt_colors.setPlaceholderText("e.g. red, gold")
        form.addRow("Colors (comma sep):", self.txt_colors)

        self.cmb_weave = QComboBox()
        # From textile_knowledge keys
        self.cmb_weave.addItems(["jeri", "meena", "ani"])
        form.addRow("Weave Technique:", self.cmb_weave)

        self.chk_ai = QCheckBox("Use Generative AI (Stable Diffusion)")
        # Default off for speed/reliability first
        self.chk_ai.setChecked(False)
        self.chk_ai.setToolTip(
            "If checked, uses Neural Network generation (slower). If unchecked, uses Algorithmic generation (instant).")
        form.addRow(self.chk_ai)

        self.chk_flux = QCheckBox("Use Flux.1 [Ultra Quality]")
        self.chk_flux.setChecked(False)
        self.chk_flux.setToolTip(
            "State-of-the-art generation (requires GPU, ~10GB VRAM). Overrides SD if checked.")
        form.addRow(self.chk_flux)

        # Create missing widgets
        self.lbl_status = QLabel("Ready to generate")
        self.lbl_status.setStyleSheet("color: #10B981; font-weight: bold;")

        self.btn_gen = QPushButton("Generate Design")
        self.btn_gen.setStyleSheet(
            "background-color: #6366F1; color: white; padding: 10px; font-weight: bold;")
        self.btn_gen.clicked.connect(self.start_generation)

        self.lbl_preview = QLabel("Preview will appear here")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setStyleSheet(
            "border: 2px dashed #6366F1; min-height: 300px; background-color: #1E1E1E;")

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Text to Image
        tab1 = QWidget()
        lay1 = QVBoxLayout(tab1)
        lay1.addLayout(form)
        lay1.addWidget(self.lbl_status)
        lay1.addWidget(self.btn_gen)
        tab1.setLayout(lay1)
        self.tabs.addTab(tab1, "Text to Design")

        # Tab 2: Image Variations (New)
        tab2 = QWidget()
        lay2 = QVBoxLayout(tab2)

        lay2.addWidget(QLabel("Select a Motif from the Editor first."))

        self.btn_var = QPushButton("Generate 4 Variations of Selection")
        self.btn_var.setStyleSheet(
            "background-color: #E11D48; color: white; padding: 10px; font-weight: bold;")
        self.btn_var.clicked.connect(self.generate_variations)
        lay2.addWidget(self.btn_var)

        self.lbl_var_preview = QLabel("Variations will appear here")
        self.lbl_var_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_var_preview.setStyleSheet(
            "border: 1px dashed #777; min-height: 200px;")
        lay2.addWidget(self.lbl_var_preview)

        tab2.setLayout(lay2)
        self.tabs.addTab(tab2, "Motif Scrambler (Img2Img)")

        # Shared Preview
        layout.addWidget(self.lbl_preview)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def start_generation(self):
        self.lbl_status.setText("Generating... Please Wait...")
        self.btn_gen.setEnabled(False)

        # Build Params
        colors = [c.strip() for c in self.txt_colors.text().split(',')]
        params = SimpleDesignParams(
            design_type=self.cmb_type.currentText(),
            occasion=self.cmb_occasion.currentText(),
            style=self.cmb_style.currentText(),
            motifs=[self.cmb_motif.currentText()],
            colors=colors,
            weave=self.cmb_weave.currentText(),
            complexity="complex"
        )

        self.worker = GenerationWorker(
            self.generator,
            params,
            self.chk_ai.isChecked(),
            self.chk_flux.isChecked())
        self.worker.finished.connect(self.on_generation_done)
        self.worker.start()

    def generate_variations(self):
        """Generates variations of the input motif."""
        if not self.editor.has_selection():
            self.lbl_status.setText("Select an area first!")
            return

        self.lbl_status.setText("Dreaming up variations (AI)...")
        self.btn_var.setEnabled(False)

        # Get Selection
        sel_img = self.editor.get_selection_image()  # QImage

        # QImage to CV2
        ptr = sel_img.bits()
        ptr.setsize(sel_img.sizeInBytes())
        arr = np.array(ptr).reshape(sel_img.height(), sel_img.width(), 4)
        cv_sel = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

        # Run in worker to avoid freeze
        # (Reusing GenerationWorker but needs tweak or new one. For speed, simpler logic here)

        class VarWorker(QThread):
            done = pyqtSignal(object)

            def __init__(self, generator, img):
                super().__init__()
                self.gen = generator
                self.img = img

            def run(self):
                try:
                    # Generate 1 variation for now
                    if hasattr(self.gen, 'generate_variations'):
                        res = self.gen.generate_variations(
                            self.img, prompt="textile variation", strength=0.7)
                        self.done.emit(res)
                    else:
                        print("Generator missing variation support")
                        self.done.emit(None)
                except Exception as e:
                    print(f"Var Error: {e}")
                    self.done.emit(None)

        self.var_worker = VarWorker(self.generator, cv_sel)
        self.var_worker.done.connect(self.on_variations_done)
        self.var_worker.start()

    def on_variations_done(self, img):
        self.btn_var.setEnabled(True)
        if img is None:
            self.lbl_status.setText("Variation Failed.")
            return

        self.lbl_status.setText("Variation Complete!")
        self.result_img = img  # Store so user can accept it

        # Show
        h, w, c = img.shape
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, c * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.lbl_var_preview.setPixmap(pix.scaled(
            300, 300, Qt.AspectRatioMode.KeepAspectRatio))

    def on_generation_done(self, img):
        self.btn_gen.setEnabled(True)
        if img is None:
            self.lbl_status.setText("Generation Failed.")
            return

        self.result_img = img
        self.lbl_status.setText("Generation Complete!")

        # Show Preview
        h, w, c = img.shape
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, c * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.lbl_preview.setPixmap(
            pix.scaled(
                300,
                300,
                Qt.AspectRatioMode.KeepAspectRatio))

    def get_result_image(self):
        return self.result_img
