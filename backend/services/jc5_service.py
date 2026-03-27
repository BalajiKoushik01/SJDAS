import numpy as np
import os

class JC5Encoder:
    """
    Production-grade bit-packer for Stäubli JC5 Format.
    Migrated from SJDAS Desktop Core to Backend Services.
    """
    def __init__(self, hooks: int = 600):
        self.hooks = hooks

    def encode(self, matrix: np.ndarray, output_path: str) -> str:
        """
        Converts a 2D binary matrix into a JC5 binary file.
        Rows = Picks, Cols = Hooks.
        """
        h, w = matrix.shape
        if w != self.hooks:
            # Resize if necessary to match loom configuration
            import cv2
            matrix = cv2.resize(matrix, (self.hooks, h), interpolation=cv2.INTER_NEAREST)
            w = self.hooks

        with open(output_path, 'wb') as f:
            # 1. Official Header
            header_text = f"JC5 FORMAT | HOOKS:{self.hooks} | PICKS:{h} | SJDAS-CLOUD-GEN\r\n"
            f.write(header_text.encode('ascii'))

            # 2. Bit-Packing (8 hooks per byte)
            # numpy.packbits handles the heavy lifting
            packed = np.packbits(matrix, axis=1)
            f.write(packed.tobytes())

            # 3. Footer
            f.write(b'\x1A') # Standard EOF for many Jacquard controllers

        return output_path
