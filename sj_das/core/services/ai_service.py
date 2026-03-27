
import logging
from typing import Any, Optional

try:
    import numpy as np
except Exception:
    import numpy as np # Forced if missing in some envs but needed for types

from PyQt6.QtCore import QObject, QThread, pyqtSignal

try:
    from sj_das.ai.flux_generator import FluxGenerator
except Exception as e:
    logging.warning(f"FluxGenerator unavailable: {e}")
    FluxGenerator = None

try:
    from sj_das.core.engines.llm.local_llm_engine import get_local_llm_engine
except Exception as e:
    logging.warning(f"LocalLLMEngine unavailable: {e}")
    get_local_llm_engine = None

try:
    from sj_das.core.engines.vision.sam_engine import SAMEngine
except Exception as e:
    logging.warning(f"SAMEngine unavailable: {e}")
    SAMEngine = None

try:
    from sj_das.core.remote_ai import RemoteAIEngine
except Exception as e:
    logging.warning(f"RemoteAIEngine unavailable: {e}")
    RemoteAIEngine = None

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
    Implements Singleton pattern for free resource management.
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
        self.llm_engine = None
        self._flux = None
        self._remote = None
        self._sam = None
        self._active_workers = []
        # Fallback to cloud if local loading fails?
        self.generation_mode = "hybrid" # local | cloud | remote

    def initialize_core_models(self):
        """Pre-load essential models in background."""
        self.model_loading_started.emit("Initializing Core AI Models...")
        # Lazy loading preferred for performance
        logger.info("AIService initialized. Models will load on demand.")

    # --- LLM Capabilities ---
    def analyze_design(self, description: str,
                       image_context: Optional[str] = None):
        """Analyze design asynchronously."""
        if not self.llm_engine:
            self.llm_engine = get_local_llm_engine()

        # Check configuration
        if not self.llm_engine.is_configured():
            if not self.llm_engine.configure(model_path=""):
                # Fallback to Pure Python Engine
                logger.warning("Native GGUF Engine failed. Trying Pure-Python Fallback...")
                try:
                    from sj_das.core.engines.llm.transformers_engine import get_transformers_engine
                    self.llm_engine = get_transformers_engine()
                    if not self.llm_engine.configure():
                        raise ImportError("Transformers Fallback failed")
                    logger.info("Switched to Transformers Engine (Pure Python).")
                except Exception as e:
                    self.error_occurred.emit(
                        "AI Model Error: C++ Build Tools missing & Fallback failed.")
                    self.task_error.emit(self.TASK_LLM, f"Model missing: {e}")
                    return

        self.task_started.emit(self.TASK_LLM, "Analyzing Design...")
        worker = AIWorker(self.llm_engine.analyze_design,
                          f"{description}\nContext: {image_context or ''}")
        worker.finished.connect(self.analysis_completed.emit)
        worker.finished.connect(
            lambda: self.task_completed.emit(
                self.TASK_LLM))
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        self._current_worker = worker

    # --- Vision Capabilities (Hybrid: Local/Cloud/Remote) ---
    def generate_pattern(self, prompt: str, mode: str = "hybrid", **kwargs):
        """
        Generate pattern using SOTA models.
        Modes: 
        - 'local': Uses Flux.1 [schnell] on local GPU.
        - 'cloud': Uses SJDAS Backend API (allows offloading).
        - 'remote': Uses direct Gemini/SDXL/Pollinations.
        """
        task_msg = f"Generating: {prompt[:20]}..."
        self.task_started.emit(self.TASK_GEN, task_msg)
        
        # Decide physical engine
        if mode == "cloud":
            # Call Backend (Offloading)
            from sj_das.core.services.cloud_service import CloudService
            def cloud_task():
                return CloudService.instance().generate_ai_design(prompt)
            worker = AIWorker(cloud_task)
        elif mode == "remote" or (mode == "hybrid" and not FluxGenerator):
            # Call Direct APIs (Gemini/Pollinations)
            if not self._remote:
                self._remote = RemoteAIEngine()
            worker = AIWorker(self._remote.generate_with_pollinations, prompt)
        else:
            # Local Flux (Performance King)
            if not self._flux:
                self._flux = FluxGenerator()
            params = kwargs.get('params', prompt)
            worker = AIWorker(self._flux.generate, params)

        worker.finished.connect(self.generation_completed.emit)
        worker.finished.connect(lambda: self.task_completed.emit(self.TASK_GEN))
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        self._current_worker = worker

    def segment_image(self, image, point_coords=None, point_labels=None):
        """Run SAM segmentation asynchronously."""
        if not self._sam:
            self._sam = SAMEngine()

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
        worker.start()
        self._current_worker = worker

    # --- Interactive Vision Tools (Magic Wand) ---
    def prepare_magic_wand(self, image: np.ndarray):
        """Pre-calculate image embeddings for instant segmentation."""
        if not self._sam:
            self._sam = SAMEngine()

        self.task_started.emit(
            self.TASK_VISION,
            "Analyzing Image Structure...")

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
        """Instant segmentation from point."""
        if not self._sam or not self._sam.is_ready:
            return None
        return self._sam.predict_click(x, y)

    # --- Enhancement Tools ---
    def upscale_image(self, image: np.ndarray, scale: int = 4):
        """Upscale image using Real-ESRGAN."""
        from sj_das.core.engines.enhancement.real_esrgan_upscaler import \
            RealESRGANUpscaler

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
        """Run Inpainting (Requires Flux Refactor or fallback to SD-Inpaint)."""
        pass

    # --- World Class Features (Phase 10) ---
    def virtual_try_on(self, design_image: np.ndarray, pose="standing"):
        """
        Generate a photorealistic mockup of a model wearing the design.
        """
        from sj_das.ai.virtual_try_on import get_tryon_engine
        
        self.task_started.emit(self.TASK_GEN, f"Generating Virtual Try-On ({pose})...")
        
        def task():
            engine = get_tryon_engine()
            return engine.generate_mockup(design_image, pose)
            
        worker = AIWorker(task)
        worker.finished.connect(self.generation_completed.emit)
        worker.finished.connect(lambda: self.task_completed.emit(self.TASK_GEN))
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        self._active_workers.append(worker)

    def remove_background(self, image: np.ndarray):
        """
        Intelligent Background Removal (rembg).
        """
        from sj_das.ai.smart_eraser import get_smart_eraser
        
        self.task_started.emit(self.TASK_VISION, "Removing Background...")
        
        def task():
            eraser = get_smart_eraser()
            return eraser.remove_background(image)
            
        worker = AIWorker(task)
        worker.finished.connect(self.generation_completed.emit)
        worker.finished.connect(lambda: self.task_completed.emit(self.TASK_VISION))
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        self._active_workers.append(worker)

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
