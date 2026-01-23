"""
Refactored LoomEngine with Enhanced Error Handling and Logging
"""
from typing import Dict, Optional

import cv2
import numpy as np

from sj_das.utils.decorators import handle_errors, validate_input
from sj_das.utils.enhanced_logger import get_logger, log_performance
from sj_das.utils.exceptions import (ExportError, InvalidWeaveError,
                                     LoomException)

logger = get_logger(__name__)


class LoomEngine:
    """
    Core Manufacturing Engine - Converts designs into loom-ready weave maps.

    Features:
    - Multiple weave patterns (Plain, Twill, Satin, Honeycomb)
    - Binary graph generation for Jacquard looms
    - BMP export for manufacturing
    - Robust error handling and logging
    """

    def __init__(self):
        """Initialize loom engine with weave library."""
        logger.info("Initializing LoomEngine")

        # Weave Library (1 = Warp up, 0 = Weft up)
        self.weaves = {
            'Plain': np.array([[1, 0], [0, 1]], dtype=np.uint8),

            'Twill 3/1': np.array([
                [1, 1, 1, 0],
                [1, 1, 0, 1],
                [1, 0, 1, 1],
                [0, 1, 1, 1]
            ], dtype=np.uint8),

            'Satin 5': np.array([
                [1, 0, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1],
                [0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0]
            ], dtype=np.uint8),

            'Satin 8': np.array([
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0]
            ], dtype=np.uint8),

            'Twill 2/2': np.array([
                [1, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 1, 1],
                [1, 0, 0, 1]
            ], dtype=np.uint8),

            'Honeycomb': np.array([
                [1, 1, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0],
                [0, 1, 0, 1, 0, 1],
                [0, 0, 1, 1, 1, 0],
                [0, 1, 0, 1, 0, 1],
                [1, 0, 1, 0, 1, 0]
            ], dtype=np.uint8)
        }

        logger.info(
            f"LoomEngine initialized with {len(self.weaves)} weave patterns")

    @log_performance(logger)
    @validate_input(
        indexed_image=lambda x: x is not None and isinstance(x, np.ndarray),
        color_map=lambda x: isinstance(x, dict)
    )
    def generate_graph(self, indexed_image: np.ndarray,
                       color_map: Dict[int, str]) -> np.ndarray:
        """
        Generates binary loom graph from indexed design.

        Args:
            indexed_image: 2D array of color indices (0-N)
            color_map: Dict mapping color_index -> weave_name

        Returns:
            Binary graph (0/255) ready for loom

        Raises:
            LoomException: If graph generation fails
            InvalidWeaveError: If weave pattern is invalid
        """
        try:
            h, w = indexed_image.shape
            logger.debug(f"Generating loom graph for {w}x{h} design")

            graph = np.zeros((h, w), dtype=np.uint8)
            unique_indices = np.unique(indexed_image)

            logger.debug(f"Processing {len(unique_indices)} unique colors")

            for idx in unique_indices:
                weave_name = color_map.get(idx, 'Plain')

                if weave_name not in self.weaves:
                    logger.warning(
                        f"Unknown weave '{weave_name}', using Plain")
                    weave_name = 'Plain'

                weave = self.weaves[weave_name]
                wh, ww = weave.shape

                # Create mask for this color
                mask = (indexed_image == idx)

                # Tile weave pattern
                Y, X = np.indices((h, w))
                tiled = weave[Y % wh, X % ww]

                # Apply to graph (255 for Warp Up, 0 for Weft Up)
                graph[mask] = tiled[mask] * 255

            logger.info(f"Loom graph generated successfully: {w}x{h}")
            return graph

        except Exception as e:
            logger.error(
                f"Loom graph generation failed",
                context={
                    "error": str(e)},
                exc_info=True)
            raise LoomException(
                f"Failed to generate loom graph: {e}", context={
                    "size": indexed_image.shape})

    @log_performance(logger)
    @validate_input(
        graph=lambda x: x is not None and isinstance(x, np.ndarray),
        filepath=lambda x: isinstance(x, str) and len(x) > 0
    )
    def save_loom_file(self, graph: np.ndarray, filepath: str) -> None:
        """
        Saves binary graph as BMP file for loom.

        Args:
            graph: Binary graph array
            filepath: Output file path

        Raises:
            ExportError: If file save fails
        """
        try:
            logger.debug(f"Saving loom file to {filepath}")

            # Ensure binary
            _, binary = cv2.threshold(graph, 127, 255, cv2.THRESH_BINARY)

            # Save as BMP
            success = cv2.imwrite(filepath, binary)

            if not success:
                raise ExportError(f"Failed to write file: {filepath}")

            logger.info(f"Loom file saved successfully: {filepath}")

        except Exception as e:
            logger.error(
                f"Loom file save failed",
                context={
                    "filepath": filepath,
                    "error": str(e)},
                exc_info=True)
            raise ExportError(
                f"Failed to save loom file: {e}", context={
                    "filepath": filepath})

    @handle_errors(default_return=None)
    def get_weave_structure(self, weave_type: str) -> Optional[np.ndarray]:
        """
        Get basic weave structure pattern.

        Args:
            weave_type: Type of weave (plain, twill, satin)

        Returns:
            Numpy array representing weave structure, or None if invalid
        """
        weave_map = {
            'plain': 'Plain',
            'twill': 'Twill 3/1',
            'satin': 'Satin 5'
        }

        weave_name = weave_map.get(weave_type.lower(), 'Plain')
        return self.weaves.get(weave_name, self.weaves['Plain'])

    @log_performance(logger)
    @validate_input(
        design=lambda x: x is not None and isinstance(x, np.ndarray),
        hooks=lambda x: isinstance(x, int) and x > 0
    )
    def design_to_weave(self, design: np.ndarray, hooks: int,
                        weave_type: str = "plain") -> np.ndarray:
        """
        Convert design to weave map for loom.

        Args:
            design: 2D array (grayscale or indexed)
            hooks: Number of hooks (warp threads)
            weave_type: Type of weave to use

        Returns:
            Binary weave map (1 = warp up, 0 = warp down)

        Raises:
            LoomException: If conversion fails
        """
        try:
            # Ensure 2D
            if len(design.shape) == 3:
                design = design[:, :, 0]

            # Resize to match hooks
            h, w = design.shape
            if w != hooks:
                design = cv2.resize(
                    design, (hooks, h), interpolation=cv2.INTER_NEAREST)

            # Create color map (all colors use same weave)
            unique_colors = np.unique(design)
            color_map = {int(c): weave_type.title() for c in unique_colors}

            # Generate weave map
            weave_map = self.generate_graph(design, color_map)

            # Convert to binary (0/1)
            return (weave_map > 127).astype(np.uint8)

        except Exception as e:
            logger.error(
                f"Design to weave conversion failed",
                context={
                    "error": str(e)},
                exc_info=True)
            # Fallback: simple binary conversion
            return (design > 127).astype(np.uint8)
