import numpy as np
from PIL import Image


class PhotoWeaveEngine:
    """
    Advanced Engine for converting Photos (Family Pictures) to Jacquard Weaves.
    Uses 'Floyd-Steinberg Dithering' or 'Ordered Dithering' to map
    continuous tone photos to limited yarn palettes (Binders) without banding.
    """

    def process_photo_for_loom(self, photo_path, width_hooks, palette_size=8):
        """
        Converts photo to dithered, loom-ready BMP.
        1. Resize -> 2. Contrast Enhance -> 3. Palette Mapping -> 4. Error Diffusion Dither.
        """
        # 1. Load with PIL (Better dithering support than CV2)
        try:
            img = Image.open(photo_path).convert("RGB")
        except BaseException:
            raise ValueError("Invalid Image")

        # 2. Resize
        aspect = img.height / img.width
        new_h = int(width_hooks * aspect)
        img = img.resize((width_hooks, new_h), Image.Resampling.LANCZOS)

        # 3. Enhance Contrast (Jacquard needs strong contrast)
        # Using numpy for speed
        arr = np.array(img)
        # Simple stretching
        p2, p98 = np.percentile(arr, (2, 98))
        arr = np.clip(arr, p2, p98)  # Clip outliers
        arr = (arr - p2) / (p98 - p2) * 255.0
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)

        # 4. Dithering & Quantization
        # Use Adaptive Quantization to pick the BEST colors for THIS image
        # instead of a fixed generic palette.
        # dither=Image.Dither.FLOYDSTEINBERG (1)

        # We use Adaptive method (default when palette not provided)
        dithered = img.quantize(
            colors=palette_size,
            method=1,
            dither=1)  # Method 1=MedianCut, 2=FastOctree

        # Note: If we need a fixed palette later, we can add a toggle.
        # But for "Photo" look, adaptive is mandatory.

        # Convert back to RGB for display/export
        final = dithered.convert("RGB")

        return np.array(final)  # Return as Numpy for Editor
