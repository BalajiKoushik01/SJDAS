import numpy as np


class WeaveEngine:
    def __init__(self):
        # Define standard weave structures as binary matrices (0/1)
        # 1 = Warp Up (Black/Marked), 0 = Weft Up (White/Unmarked)
        self.weaves = {
            "Plain (1/1)": np.array([
                [1, 0],
                [0, 1]
            ], dtype=np.uint8),

            "Twill (2/1)": np.array([
                [1, 1, 0],
                [1, 0, 1],
                [0, 1, 1]
            ], dtype=np.uint8),

            "Twill (3/1)": np.array([
                [1, 1, 1, 0],
                [1, 1, 0, 1],
                [1, 0, 1, 1],
                [0, 1, 1, 1]
            ], dtype=np.uint8),

            "Satin (5-end)": np.array([
                [1, 0, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1],
                [0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0]
            ], dtype=np.uint8),

            "Satin (8-end)": np.array([
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0]
            ], dtype=np.uint8),

            "Basket (2x2)": np.array([
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1]
            ], dtype=np.uint8),

            "Honeycomb": np.array([
                [1, 1, 0, 0, 1, 1],
                [1, 0, 1, 1, 0, 1],
                [0, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 0],
                [1, 0, 1, 1, 0, 1],
                [1, 1, 0, 0, 1, 1]
            ], dtype=np.uint8)
        }

    def get_weave_names(self):
        return list(self.weaves.keys())

    def apply_weave(self, binary_mask, weave_name):
        """
        Applies the selected weave structure to the masked area.
        binary_mask: 2D numpy array where 255 (or 1) indicates the region to fill.
        weave_name: Key from self.weaves
        """
        if weave_name not in self.weaves:
            raise ValueError(f"Unknown weave: {weave_name}")

        pattern = self.weaves[weave_name]
        p_h, p_w = pattern.shape
        img_h, img_w = binary_mask.shape

        # Tile the pattern to cover the image
        tiled = np.tile(pattern, (img_h // p_h + 1, img_w // p_w + 1))
        tiled = tiled[:img_h, :img_w]

        # Apply mask: Only show weave where mask is active
        # Assuming mask is 255 for active region
        result = np.zeros_like(binary_mask, dtype=np.uint8)

        # Where mask is active, take the tiled pattern value (scaled to 255)
        # Where mask is inactive, keep 0
        mask_bool = binary_mask > 128
        result[mask_bool] = tiled[mask_bool] * 255

        return result
