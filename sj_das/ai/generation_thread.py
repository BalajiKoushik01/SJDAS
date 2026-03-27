from pathlib import Path
import logging

try:
    import cv2
    import numpy as np
    _LIBS_AVAILABLE = True
except Exception as e:
    logging.warning(f"GenerationThread: Libraries unavailable: {e}")
    cv2 = None
    np = None
    _LIBS_AVAILABLE = False

from PyQt6.QtCore import QThread, pyqtSignal
from sj_das.ai.model_manager import ModelManager


class GenerationThread(QThread):
    """
    Background thread for AI generation to keep UI responsive.
    """

    progress = pyqtSignal(int)
    finished = pyqtSignal(str)   # Returns path to generated image
    error = pyqtSignal(str)

    def __init__(self, model_manager: ModelManager,
                 seed=None, optimize_seamless=True):
        super().__init__()
        self.model_manager = model_manager
        self.seed = seed
        self.optimize_seamless = optimize_seamless

    def run(self):
        try:
            self.progress.emit(10)

            if not _LIBS_AVAILABLE:
                raise RuntimeError("Critical libraries (cv2/numpy) not available")

            # Ensure model is loaded (might take time on first run)
            if not self.model_manager.load_stylegan():
                raise RuntimeError("Failed to load StyleGAN model")

            self.progress.emit(30)

            # Generate
            image = self.model_manager.generate_textile(
                seed=self.seed,
                optimize_seamless=self.optimize_seamless
            )

            self.progress.emit(80)

            # Save to temp file (use user home for persistence and write permissions)
            temp_dir = Path.home() / ".sj_das" / "temp_results"
            temp_dir.mkdir(parents=True, exist_ok=True)
            output_path = temp_dir / "generated_pattern.png"

            # Convert RGB to BGR for OpenCV
            save_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_path), save_image)

            self.progress.emit(100)
            self.finished.emit(str(output_path.absolute()))

        except Exception as e:
            self.error.emit(str(e))
