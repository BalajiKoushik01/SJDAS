import cv2
import numpy as np


class WeaveMapper:
    """
    Handles conversion of Design Mask -> Binary/Palette BMP for Electronic Jacquard.
    Maps color classes to specific binary weave structures.
    """

    def __init__(self):
        self.weaves = {}  # { class_id: binary_pattern_2d_array }
        self._init_default_weaves()

    def _init_default_weaves(self):
        """Initialize standard weaves (Satin, Twill, Plain)."""
        # 0: Background (Ground Weave - e.g. 1/7 satin or plain)
        # Simple Plain 1x1
        self.weaves[0] = np.array([[1, 0], [0, 1]], dtype=np.uint8)

        # 1: Red (Body) - 4-end Satin
        self.weaves[1] = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ], dtype=np.uint8)

        # 2: Green (Border) - Will same as Body usually, or heavier
        self.weaves[2] = self.weaves[1]

        # 3: Blue (Pallu) - Heavy/Float
        self.weaves[3] = np.ones((2, 2), dtype=np.uint8)  # Full lift (float)

    def set_weave(self, class_id, weave_matrix):
        """
        Assigns a binary weave matrix to a specific color class.
        weave_matrix: 2D numpy array (0/1)
        """
        self.weaves[class_id] = np.array(weave_matrix, dtype=np.uint8)

    def generate_loom_bmp(self, mask_arr, width, height, palette_mode=False):
        """
        Generates the final loom file.
        Args:
            mask_arr: (H, W) numpy array with class indices
            width: Output width (Hooks)
            height: Output height (Picks)
            palette_mode: If True, exports 8-bit BMP with palette (Color 1, 2...).
                          If False, exports 1-bit Binary BMP (actual weave).
        """
        # Resize mask to target loom dimensions nearest neighbor
        resized_mask = cv2.resize(
            mask_arr, (width, height), interpolation=cv2.INTER_NEAREST)

        if palette_mode:
            # Just export the class indices as 8-bit image
            # Loom software usually maps Color Index -> Weave locally
            return resized_mask.astype(np.uint8)
        else:
            # Binary Expansion
            # We must tile the weave structures
            output = np.zeros((height, width), dtype=np.uint8)

            for class_id, weave in self.weaves.items():
                # Create a tiled weave layer of full size
                # 1. Tile
                wh, ww = weave.shape
                # Calculate repeats needed
                rep_y = (height // wh) + 1
                rep_x = (width // ww) + 1
                tiled = np.tile(weave, (rep_y, rep_x))
                tiled = tiled[:height, :width]

                # 2. Mask
                region = (resized_mask == class_id)

                # 3. Apply
                output[region] = tiled[region]

            # Convert to 255 for visualization/standard BMP
            # Loom binary usually expects 0/1 bits packed.
            # But standard BMP view is 0=Black(Down), 255=White(Up).
            return output * 255
