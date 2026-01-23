
import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from sj_das.core.fabric_sim import FabricSimulator
from sj_das.core.loom_engine import LoomEngine
from sj_das.core.loom_exporter import LoomExporter
from sj_das.core.weave_manager import WeaveManager

logger = logging.getLogger("SJ_DAS.TextileService")


class TextileWorker(QThread):
    # ... (existing code)
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
            logger.error(f"Textile Task Failed: {e}", exc_info=True)
            self.error.emit(str(e))


class TextileService(QObject):
    # ... (existing signals)
    simulation_started = pyqtSignal()
    simulation_completed = pyqtSignal(object)

    loom_generation_started = pyqtSignal()
    loom_generation_completed = pyqtSignal(object)

    export_started = pyqtSignal()
    export_completed = pyqtSignal(bool)

    error_occurred = pyqtSignal(str)

    _instance = None

    def __init__(self):
        super().__init__()
        self.loom_engine = LoomEngine()
        self.fabric_sim = FabricSimulator(scale=2, light_intensity=25.0)
        self.loom_exporter = LoomExporter()
        self.weave_manager = WeaveManager()

        self._worker = None

    @staticmethod
    def instance() -> 'TextileService':
        if not TextileService._instance:
            TextileService._instance = TextileService()
        return TextileService._instance

    # ... (existing API)

    def export_loom_file(self, image: np.ndarray,
                         output_path: str, hooks: int, picks: int, **kwargs):
        """
        Async: Exports design to BMP for Jacquard.
        """
        self.export_started.emit()

        # We wrap the export call.
        # Note: LoomExporter.export takes many args. We pass them via kwargs or explicit args.
        # For simplicity, we pass strictly required + kwargs.

        worker = TextileWorker(
            self.loom_exporter.export,
            image,
            output_path,
            hooks,
            picks,
            **kwargs
        )
        worker.finished.connect(self.export_completed.emit)
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        self._worker = worker

    @staticmethod
    def instance() -> 'TextileService':
        if not TextileService._instance:
            TextileService._instance = TextileService()
        return TextileService._instance

    # ==========================
    # Public Async API
    # ==========================

    def run_simulation(self, design_img: np.ndarray,
                       color_map: Dict[Tuple[int, int, int], str]):
        """
        Async: Generates photorealistic fabric preview.
        Args:
            design_img: BGR numpy array
            color_map: (R,G,B) -> Weave Name
        """
        self.simulation_started.emit()

        # Validate inputs briefly
        if design_img is None:
            self.error_occurred.emit("No design image provided")
            return

        worker = TextileWorker(
            self.fabric_sim.simulate,
            design_img,
            color_map,
            self.weave_manager
        )
        worker.finished.connect(self.simulation_completed.emit)
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        self._worker = worker

    def generate_loom_graph(
            self, indexed_image: np.ndarray, index_map: Dict[int, str]):
        """
        Async: Generates binary graph for Jacquard.
        Args:
            indexed_image: 2D index array
            index_map: Index -> Weave Name
        """
        self.loom_generation_started.emit()

        worker = TextileWorker(
            self.loom_engine.generate_graph,
            indexed_image,
            index_map
        )
        worker.finished.connect(self.loom_generation_completed.emit)
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        self._worker = worker

    # ==========================
    # Public Sync API (Getters)
    # ==========================

    def get_available_weaves(self) -> list:
        """Returns list of available weave names."""
        # Merge sources if needed. LoomEngine has a dict.
        return list(self.loom_engine.weaves.keys())

    def get_weave_pattern(self, name: str) -> np.ndarray:
        return self.loom_engine.weaves.get(name)
