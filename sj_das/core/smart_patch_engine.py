import random
from pathlib import Path

import cv2
import numpy as np


class SmartPatchEngine:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        # Recursive search for all images
        all_files = sorted(
            list(
                self.data_dir.rglob("*.jpg")) +
            list(
                self.data_dir.rglob("*.bmp")) +
            list(
                self.data_dir.rglob("*.png")))

        self.bodies = []
        self.borders = []
        self.pallus = []
        self.others = []

        for f in all_files:
            name = f.name.lower()
            if "body" in name:
                self.bodies.append(f)
            elif "boder" in name or "border" in name:
                self.borders.append(f)
            elif "pallu" in name:
                self.pallus.append(f)
            else:
                self.others.append(f)

        # If specific categories empty, fallback to 'others' or all
        if not self.bodies:
            self.bodies = all_files
        if not self.borders:
            self.borders = all_files

    def generate(self, width, height, style="mix"):
        """
        Generates a high-res design matching the Dataset Style.
        Structure: Body Pattern (Tiled/Mirrored).
        """
        if not self.bodies:
            return self._generate_noise(width, height)

        # 1. Pick Source (Prefer Body for main area)
        src_path = random.choice(self.bodies)
        src = cv2.imread(str(src_path))
        if src is None:
            return self._generate_noise(width, height)

        # 2. Smart Composition
        # The user's files are often full "Body" repeats.
        # We should extract a seamless seed from it and tile it.

        # Determine crop size (try to get a meaningful chunk, e.g. 240x240)
        crop_w = min(width, src.shape[1], 240)
        crop_h = min(height, src.shape[0], 240)

        patch = self._get_smart_crop(src, crop_w, crop_h)

        # 3. Create Full Canvas
        np.zeros((height, width, 3), dtype=np.uint8)

        # Tile the patch to fill canvas (NEAREST neighbor to keep logic)
        # Mirroring creates better seamlessness for random crops

        # Create a 2x2 mirror unit
        top = np.hstack([patch, cv2.flip(patch, 1)])
        bot = np.hstack([cv2.flip(patch, 0), cv2.flip(cv2.flip(patch, 0), 1)])
        unit = np.vstack([top, bot])  # Size is (2*crop_h, 2*crop_w)

        # Tile 'unit' across canvas
        # Faster way: resize if style permits, or tile loop

        # Let's tile-loop for exact pixel grid
        uh, uw = unit.shape[:2]

        # Calculate reps
        reps_x = (width // uw) + 1
        reps_y = (height // uh) + 1

        # Tile
        tiled = np.tile(unit, (reps_y, reps_x, 1))

        # Crop to exact result
        final = tiled[:height, :width]

        return final

    def _get_smart_crop(self, img, w, h):
        ih, iw = img.shape[:2]

        # If image is too small, resize UP with Nearest
        if iw < w or ih < h:
            scale = max(w / iw, h / ih)
            nw, nh = int(iw * scale) + 1, int(ih * scale) + 1
            img = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_NEAREST)
            ih, iw = img.shape[:2]

        # Random Crop
        x = random.randint(0, iw - w)
        y = random.randint(0, ih - h)
        return img[y:y + h, x:x + w]

    def _generate_noise(self, w, h):
        return np.zeros((h, w, 3), dtype=np.uint8)
