
import logging
from typing import Any, Optional

import numpy as np
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from sj_das.ai.stable_diffusion_generator import get_sd_generator
from sj_das.core.engines.llm.llama_engine import get_llama_engine
from sj_das.core.engines.vision.sam_engine import SAMEngine

logger = logging.getLogger("SJ_DAS.AIService")


class AIWorker(QThread):
    """
    Background worker for blocking AI tasks.
    Ensures UI never freezes (Google-quality responsiveness).
    """
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.task_func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"AI Task Failed: {e}", exc_info=True)
            self.error.emit(str(e))


class AIService(QObject):
    """
    Centralized Facade for all AI capabilities.
    Implements Singleton pattern for resource management.
    """

    # Signals for UI updates
    model_loading_started = pyqtSignal(str)
    model_ready = pyqtSignal(str)
    analysis_completed = pyqtSignal(str)
    generation_completed = pyqtSignal(object)  # Returns image/data
    error_occurred = pyqtSignal(str)

    # Granular Status Signals
    task_started = pyqtSignal(str, str)   # (task_type, message)
    task_completed = pyqtSignal(str)      # (task_type)
    task_error = pyqtSignal(str, str)     # (task_type, message)

    # Task Constants
    TASK_VISION = "vision"
    TASK_LLM = "llm"
    TASK_GEN = "gen_ai"
    TASK_VOICE = "voice"
    TASK_SEARCH = "search"

    _instance = None

    def __init__(self):
        super().__init__()
        self._llama = None
        self._sd = None
        self._sam = None
        self._whisper = None
        self._active_workers = []  # Keep references

    def initialize_core_models(self):
        """Pre-load essential models in background."""
        self.model_loading_started.emit("Initializing Core AI Models...")
        # We can implement a warm-up sequence here if requested.
        # For now, we rely on lazy loading to keep startup fast.
        logger.info("AIService initialized. Models will load on demand.")

    # --- LLM Capabilities ---
    def analyze_design(self, description: str,
                       image_context: Optional[str] = None):
        """Analyze design asynchronously."""
        if not self._llama:
            self._llama = get_llama_engine()

        # Check configuration
        if not self._llama.is_configured():
            # Try auto-configure
            if not self._llama.configure(model_path=""):
                self.error_occurred.emit(
                    "Llama model not found. Please install Llama 3.2.")
                self.task_error.emit(self.TASK_LLM, "Model missing")
                return

        self.task_started.emit(self.TASK_LLM, "Analyzing Design...")
        worker = AIWorker(self._llama.analyze_design,
                          f"{description}\nContext: {image_context or ''}")
        worker.finished.connect(self.analysis_completed.emit)
        worker.finished.connect(
            lambda: self.task_completed.emit(
                self.TASK_LLM))
        worker.error.connect(self.error_occurred.emit)
        worker.error.connect(
            lambda e: self.task_error.emit(
                self.TASK_LLM, str(e)))
        worker.start()
        # Keep reference to avoid GC
        self._current_worker = worker

    # --- Vision Capabilities ---
    def generate_pattern(self, prompt: str, **kwargs):
        """Generate pattern asynchronously."""
        if not self._sd:
            self._sd = get_sd_generator()

        self.task_started.emit(self.TASK_GEN, f"Generating: {prompt[:20]}...")
        worker = AIWorker(self._sd.generate, kwargs.get('params'))
        worker.finished.connect(self.generation_completed.emit)
        worker.finished.connect(
            lambda: self.task_completed.emit(
                self.TASK_GEN))
        worker.error.connect(self.error_occurred.emit)
        worker.error.connect(
            lambda e: self.task_error.emit(
                self.TASK_GEN, str(e)))
        worker.start()
        self._current_worker = worker

    def segment_image(self, image, point_coords=None, point_labels=None):
        """Run SAM segmentation asynchronously."""
        if not self._sam:
            self._sam = SAMEngine()

        # We wrap the call. If point_coords provided, we use precise
        # segmentation, else automatic.
        if point_coords:
            def task(): return self._sam.predict_mask(image, point_coords, point_labels)
        else:
            def task(): return self._sam.generate_masks(image)

        self.task_started.emit(self.TASK_VISION, "Segmenting Image...")
        worker = AIWorker(task)
        worker.finished.connect(self.generation_completed.emit)
        worker.finished.connect(
            lambda: self.task_completed.emit(
                self.TASK_VISION))
        worker.error.connect(self.error_occurred.emit)
        worker.error.connect(
            lambda e: self.task_error.emit(
                self.TASK_VISION, str(e)))
        worker.start()
        self._current_worker = worker

    # --- Interactive Vision Tools (Magic Wand) ---
    def prepare_magic_wand(self, image: np.ndarray):
        """
        Pre-calculate image embeddings for instant segmentation.
        This is a heavy operation (~2-5s on CPU).
        """
        if not self._sam:
            self._sam = SAMEngine()

        self.task_started.emit(
            self.TASK_VISION,
            "Analyzing Image Structure...")

        # Run embedding in background
        worker = AIWorker(self._sam.set_image, image)
        worker.finished.connect(
            lambda: self.task_completed.emit(
                self.TASK_VISION))
        worker.finished.connect(
            lambda: self.model_ready.emit("Magic Wand Ready"))
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        self._active_workers.append(worker)

    def get_magic_wand_mask(self, x: int, y: int) -> Optional[np.ndarray]:
        """
        Instant segmentation from point.
        Must call prepare_magic_wand first.
        """
        if not self._sam or not self._sam.is_ready:
            return None
        return self._sam.predict_click(x, y)

    # --- Enhancement Tools ---
    def upscale_image(self, image: np.ndarray, scale: int = 4):
        """
        Upscale image using Real-ESRGAN.
        """
        # Lazy import to avoid heavy dependency if unused
        from sj_das.core.engines.enhancement.real_esrgan_upscaler import \
            RealESRGANUpscaler

        # Note: We instantiate transiently or cache. For now transient is safer
        # for VRAM.
        upscaler = RealESRGANUpscaler(scale=scale)

        self.task_started.emit(self.TASK_GEN, f"Upscaling {scale}x...")
        worker = AIWorker(upscaler.upscale, image)
        worker.finished.connect(self.generation_completed.emit)
        worker.finished.connect(
            lambda: self.task_completed.emit(
                self.TASK_GEN))
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        self._active_workers.append(worker)

    def inpaint_image(self, image, mask, prompt):
        """Run Inpainting asynchronously."""
        if not self._sd:
            self._sd = get_sd_generator()

        self.task_started.emit(self.TASK_GEN, f"Inpainting: {prompt[:20]}...")
        worker = AIWorker(self._sd.inpaint, image, mask, prompt)
        worker.finished.connect(self.generation_completed.emit)
        worker.finished.connect(
            lambda: self.task_completed.emit(
                self.TASK_GEN))
        worker.error.connect(self.error_occurred.emit)
        worker.error.connect(
            lambda e: self.task_error.emit(
                self.TASK_GEN, str(e)))
        worker.start()
        self._current_worker = worker

    def search_object(self, image: np.ndarray, query: str):
        """
        Async: Find objects in image described by text query.
        Signals: task_started('search'), task_completed('search')
        """
        from sj_das.core.engines.vision.owl_engine import OwlEngine

        self.task_started.emit(self.TASK_SEARCH, f"Searching for '{query}'...")

        # Lazy init locally or in worker?
        # Ideally engines are managed by service.
        # For prototype simplicity:
        if not hasattr(self, 'owl_engine'):
            self.owl_engine = OwlEngine()

        worker = AIWorker(
            self.owl_engine.detect,
            image,
            [query]
        )
        worker.finished.connect(
            lambda res: self.task_completed.emit(
                self.TASK_SEARCH))
        worker.finished.connect(self.search_completed.emit)
        worker.error.connect(self.error_occurred.emit)
        worker.error.connect(
            lambda e: self.task_error.emit(
                self.TASK_SEARCH, str(e)))
        worker.start()
        self._active_workers.append(worker)

    search_completed = pyqtSignal(list)  # Returns detections list

    # --- Singleton Access ---
    @staticmethod
    def instance() -> 'AIService':
        if AIService._instance is None:
            AIService._instance = AIService()
        return AIService._instance
