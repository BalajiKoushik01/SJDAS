"""
Loom Exporter Module.
Converts design data into signals for Electronic Jacquard Controllers.
Supports:
- BMP (Standard Window Bitmap, 1-bit or 8-bit)
- EP (Stub for Staubli/Bonas formats)
"""

import logging
import struct
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger("SJ_DAS.LoomExporter")


class LoomExporter:
    """
    Export designs to Loom formats.
    """

    def __init__(self):
        pass

    def export_bmp(self, data: np.ndarray, path: str, hooks: int):
        """
        Export as Loom-Ready BMP (1-bit or 8-bit).
        Digital Jacquards often read BMPs where 1 pixel = 1 hook selection.
        """
        try:
            # Resize width to match hook count exactly?
            # Or assume data is already correct?
            h, w = data.shape[:2]

            if w != hooks:
                logger.warning(
                    f"Resizing design width {w} to match loom hooks {hooks}")
                # Nearest neighbor to preserve crisp lines
                data = cv2.resize(
                    data, (hooks, h), interpolation=cv2.INTER_NEAREST)

            # Convert to 1-bit if strictly binary
            if len(data.shape) == 2 or data.shape[2] == 1:
                # Ensure binary
                _, binary = cv2.threshold(data, 127, 255, cv2.THRESH_BINARY)
                cv2.imwrite(path, binary)
            else:
                # 8-bit color
                cv2.imwrite(path, data)

            logger.info(f"Exported BMP to {path}")
            return True
        except Exception as e:
            logger.error(f"BMP Export failed: {e}")
            return False

    def export_ep(self, jari_mask: np.ndarray,
                  meena_mask: np.ndarray, path: str):
        """
        Export as Simulated EP (Electronic Pattern) file.
        Real EP files are proprietary binary formats (Bonas/Staubli).
        We will simulate a mapped structure here.

        Structure:
        - Header (Design Info)
        - Body (RLE encoded or raw hook data)
        """
        try:
            # For now, we save a composite BMP where:
            # Color 1 = Jari
            # Color 2 = Meena
            # Color 0 = Ground

            h, w = jari_mask.shape
            composite = np.zeros((h, w), dtype=np.uint8)

            # Map values (Arbitrary paletted values for logic)
            # 1 = Jari
            # 2 = Meena
            composite[jari_mask > 128] = 1
            composite[meena_mask > 128] = 2

            # If we had a real EP encoder, we'd use it here.
            # Fallback to saving as palette BMP which is widely supported.

            # Create Palette
            # 0: Black (Ground)
            # 1: Gold (Jari)
            # 2: Red (Meena)

            # Only supports 8-bit single channel write in OpenCV usually
            # We can save as mapped pseudo-color image for verification
            preview = np.zeros((h, w, 3), dtype=np.uint8)
            preview[composite == 1] = [0, 215, 255]  # Gold (BGR)
            preview[composite == 2] = [0, 0, 255]   # Red

            # Add .preview.png for visualization
            cv2.imwrite(path + ".preview.png", preview)

            # Save Raw Indices for processing tools
            cv2.imwrite(path, composite)

            logger.info(f"Exported EP simulation to {path}")
            return True

        except Exception as e:
            logger.error(f"EP Export failed: {e}")
            return False
