"""
Weave Mapper Module.
Maps colors/channels to binary weave structures (Hook Plans).
"""

import logging

import cv2
import numpy as np

logger = logging.getLogger("SJ_DAS.WeaveMapper")


class WeaveMapper:
    """
    Manages weave structures and maps them to image areas.
    """

    def __init__(self):
        # Basic Weave Library (Binary Patterns)
        # 1 = Warp UP (Hook Up), 0 = Warp DOWN (Hook Down)
        self.weaves = {
            "plain": np.array([[1, 0], [0, 1]], dtype=np.uint8),
            "twill_3_1": np.array([
                [1, 1, 1, 0],
                [0, 1, 1, 1],
                [1, 0, 1, 1],
                [1, 1, 0, 1]
            ], dtype=np.uint8),
            "satin_5": np.array([  # 5-end Satin
                [1, 0, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1],
                [0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0]
            ], dtype=np.uint8),
            "solid": np.array([[1]], dtype=np.uint8)  # All Up
        }

    def generate_graph_paper(self, mask: np.ndarray,
                             weave_name: str) -> np.ndarray:
        """
        Fill a masked area with a specific weave structure.

        Args:
            mask: Binary mask defining the area to fill (0 or 255)
            weave_name: Key from self.weaves

        Returns:
            Binary image (0/1) representing the hook plan for that area.
        """
        if weave_name not in self.weaves:
            logger.warning(f"Weave '{weave_name}' not found, using plain.")
            weave_name = "plain"

        weave = self.weaves[weave_name]
        h, w = mask.shape
        wh, ww = weave.shape

        # Tile the weave to cover the whole image
        # Calculate full tiles needed
        ny = (h // wh) + 1
        nx = (w // ww) + 1

        tiled = np.tile(weave, (ny, nx))

        # Crop to size
        tiled = tiled[:h, :w]

        # Apply Mask (Where mask is 0, output is 0)
        # We assume output is for this channel.
        # Actually, output should be: Weave Pattern WHERE Mask is Active.

        # Ensure mask is binary 0/1
        binary_mask = (mask > 128).astype(np.uint8)

        result = tiled * binary_mask

        return result

    def combine_channels(self, channel_plans: list[np.ndarray]) -> np.ndarray:
        """
        Combine multiple channel plans into one master hook plan.
        Usually simple OR for Jari+Meena, but complex logic is possible.
        """
        if not channel_plans:
            return None

        # Start with zeroes
        master = np.zeros_like(channel_plans[0])

        for plan in channel_plans:
            master = cv2.bitwise_or(master, plan)

        return master
