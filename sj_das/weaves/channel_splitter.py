"""
Channel Splitter Module.
Separates a textile design into manufacturing channels:
1. Jari (Metallic Gold/Silver)
2. Meena (Colored Silk Work)
3. Body (Base Fabric)

Critical for generating Jacquard cards.
"""

import logging

import cv2
import numpy as np

logger = logging.getLogger("SJ_DAS.ChannelSplitter")


class ChannelSplitter:
    """
    Separates design into weave channels.
    """

    def __init__(self):
        # Default Gold Range (HSV) - Tunable
        # Gold is usually yellowish with high value
        self.jari_lower = np.array([10, 100, 100])
        self.jari_upper = np.array([40, 255, 255])

    def split_channels(self, image: np.ndarray) -> dict:
        """
        Split image into Jari, Meena, and Body masks.

        Args:
            image: RGB Input Image

        Returns:
            Dict containing 'jari', 'meena', 'body' binary masks (0-255)
        """
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

            # 1. Detect Jari (Gold/Metallic)
            jari_mask = cv2.inRange(hsv, self.jari_lower, self.jari_upper)

            # Simple morphological cleanup for Jari
            kernel = np.ones((3, 3), np.uint8)
            jari_mask = cv2.morphologyEx(jari_mask, cv2.MORPH_OPEN, kernel)

            # 2. Detect Everything NON-Background (Design)
            # Assuming background is the dominant color or specific color?
            # For now, let's assume anything NOT Jari is potentially Meena if
            # it has saturation

            # Saturation Threshold
            s = hsv[:, :, 1]
            colored_mask = cv2.threshold(s, 50, 255, cv2.THRESH_BINARY)[1]

            # Meena = Colored - Jari
            # (Pixels that are colored but NOT gold)
            meena_mask = cv2.bitwise_and(
                colored_mask, cv2.bitwise_not(jari_mask))

            # 3. Body (Background)
            # Body = Not Jari AND Not Meena
            combined_design = cv2.bitwise_or(jari_mask, meena_mask)
            body_mask = cv2.bitwise_not(combined_design)

            logger.info("Channels split successfully")

            return {
                "jari": jari_mask,
                "meena": meena_mask,
                "body": body_mask
            }

        except Exception as e:
            logger.error(f"Failed to split channels: {e}")
            return {}

    def set_jari_range(self, lower: list, upper: list):
        """Update Jari detection thresholds."""
        self.jari_lower = np.array(lower)
        self.jari_upper = np.array(upper)
