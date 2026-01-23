import os

import cv2
import numpy as np
from PIL import Image
from PyQt6.QtGui import QImage


class GenerativeDesignEngine:
    """Generate designs based on prompts using ensemble of AI models"""

    def __init__(self):
        # Premium Palette (Saree Standard)
        # Premium Palette (Saree Standard)
        self.palette = [
            (40, 0, 60),    # 0: Background (Maroon)
            (0, 215, 255),  # 1: Gold Zari
            (255, 100, 0),  # 2: Royal Blue
            (0, 200, 0),    # 3: Parrot Green
            (255, 0, 128),  # 4: Pink
            (255, 255, 255)  # 5: Silver/White
        ]

        from sj_das.core.remote_ai import RemoteAIEngine
        self.remote_ai = RemoteAIEngine()

    def set_api_key(self, key):
        self.remote_ai.configure(key)

    def generate_border(self, prompt, width_hooks, height_picks):
        """
        Generates a Seamless Saree Border based on prompt.
        Args:
            prompt (str): e.g., "Peacock Design with Gold Zari"
            width_hooks (int): Loom width (e.g., 240, 480)
            height_picks (int): Border height
        Returns:
            QImage: Loom-ready indexed image.
        """
        print(
            f"Generating Pattern: '{prompt}' for {width_hooks}x{height_picks}")

        # 1. Initialize Canvas (Background)
        # Using BGR for OpenCV
        # 1. Initialize Canvas (Background)
        bg_color = self.palette[0]
        np.full((height_picks, width_hooks, 3), bg_color, dtype=np.uint8)

        # 2. Initialize Logic
        prompt = prompt.lower()

        # 3. Check for Custom Local Model (Prioritize Trained AI)
        ai_triggers = [
            "custom",
            "trained",
            "my design",
            "saree",
            "border",
            "peacock",
            "motif",
            "silk",
            "zari",
            "traditional"]

        # Log to centralized logger
        from sj_das.core.logging_config import log
        log.info(
            f"Generating for prompt: '{prompt}' (Size: {width_hooks}x{height_picks})")

        if any(trigger in prompt for trigger in ai_triggers):
            log.info("Trigger matched Local AI. Calling _generate_with_gan...")
            print(
                f"Trigger '{prompt}' matches Local AI. Using Trained Progressive GAN...")

            # Call directly - if it fails, let it raise Exception so user sees it!
            # We want to know WHY it fails, not just hide it with bad
            # procedural art.
            gan_res = self._generate_with_gan(width_hooks, height_picks)

            if gan_res is not None:
                logging.info("GAN Generation Successful")
                self._add_zari_border(gan_res)
                gan_res = self._quantize_to_palette(gan_res)
                return self._numpy_to_qimage(gan_res)
            else:
                # If None returned without exception, throw one
                raise RuntimeError(
                    "AI generated empty result (None). Check logs.")

        # NOTE: Remote AI is tried first below. Procedural is Fallback.

    def _draw_complex_lattice(self, canvas, w, h):
        """Generates 'Malli Moggu' (Jasmine Bud) Lattice."""
        color_grid = self.palette[5]  # Silver
        color_bud = self.palette[1]  # Gold

        spacing = 40

        # Draw Diamond Grid
        for i in range(-h, w + h, spacing):
            # Diagonal /
            cv2.line(canvas, (i, 0), (i + h, h),
                     color_grid, 1, lineType=cv2.LINE_4)
            # Diagonal \
            cv2.line(canvas, (i, h), (i + h, 0),
                     color_grid, 1, lineType=cv2.LINE_4)

        # Draw Bud at centers (Midpoints of diamonds)
        # Centers are where diagonals cross.
        # This occurs at (i + spacing/2, ...)

        # Simplified: Scan grid properties
        # Center of diamond is (x, y).
        # If we draw dots at grid intersections:
        # i intersects j?
        # Let's simple-scan pixels or mathematical points.

        half = spacing // 2
        for y in range(0, h, half):
            for x in range(0, w, half):
                # Checker pattern
                if (x // half + y // half) % 2 == 0:
                    cv2.circle(
                        canvas, (x, y), 3, color_bud, -1, lineType=cv2.LINE_4)

    def generate_variations(self, prompt, w, h, count=3):
        """Generates variations of a design."""
        variations = []
        for i in range(count):
            # Perturb prompt or seed?
            # For now, just append "variation" which might trigger random seeds in remote AI
            # or different branches in procedural
            var_prompt = f"{prompt} variation {i+1}"
            img = self.generate_border(var_prompt, w, h)
            variations.append(img)
        return variations

    def _cubic_bezier(self, t, p0, p1, p2, p3):
        """Calculates point on cubic bezier curve at t."""
        return (1 - t)**3 * p0 + 3 * (1 - t)**2 * t * \
            p1 + 3 * (1 - t) * t**2 * p2 + t**3 * p3

    def _draw_organic_curve(self, canvas, points, color, thickness=1):
        """Draws a smooth curve from control points onto the raster grid."""
        # Rasterize Bezier
        steps = 100
        path_pts = []
        for i in range(steps + 1):
            t = i / steps
            pt = self._cubic_bezier(
                t, np.array(
                    points[0]), np.array(
                    points[1]), np.array(
                    points[2]), np.array(
                    points[3]))
            path_pts.append(pt.astype(int))

        # Anti-aliased for shape, but we might want aliased for loom?
        cv2.polylines(canvas, [np.array(path_pts)], False,
                      color, thickness, lineType=cv2.LINE_AA)
        # Actually for LOOM we want ALIASED or strictly quantized.
        # Let's use standard lineType=cv2.LINE_4 for pixel perfect.
        # cv2.polylines(canvas, [np.array(path_pts)], False, color, thickness, lineType=cv2.LINE_4)

    def _draw_peacock_repeat(self, canvas, w, h):
        """Draws organic 'Peacock' motifs using Bezier curves."""
        repeat_size = 160
        gold = self.palette[1]
        blue = self.palette[2]
        green = self.palette[3]

        for x_offset in range(0, w, repeat_size):
            cx = x_offset + repeat_size // 2
            cy = h // 2 + 10

            # --- Peacock Body (S-Curve) ---
            # Head, Neck_Top, Neck_Bot, Body_Base
            [
                [cx - 20, cy - 40],  # Head
                [cx - 40, cy - 20],  # Neck out
                [cx + 10, cy],      # Neck in
                [cx - 10, cy + 30]  # Base
            ]

            # Fill Body (Approximated by circles for bulk + curve for spine)
            cv2.circle(canvas, (cx - 20, cy - 40), 12, blue, -1)  # Head
            cv2.ellipse(canvas, (cx - 10, cy + 10),
                        (15, 30), -20, 0, 360, blue, -1)  # Body

            # Beak & Crest
            cv2.line(canvas, (cx - 30, cy - 40), (cx - 40, cy - 35), gold, 2)
            cv2.line(canvas, (cx - 20, cy - 52), (cx - 25, cy - 60), gold, 1)
            cv2.line(canvas, (cx - 15, cy - 52), (cx - 10, cy - 60), gold, 1)

            # --- Feathers (Fan) ---
            # Draw arc of circles
            for angle in range(-60, 70, 20):
                rad_dist = 50
                rad_x = int(cx + rad_dist * np.sin(np.radians(angle)))
                rad_y = int(cy - 20 - rad_dist * np.cos(np.radians(angle)))

                # Feather Eye
                cv2.circle(canvas, (rad_x, rad_y), 10, green, -1)
                cv2.circle(canvas, (rad_x, rad_y), 4, gold, -1)

                # Connection to body
                cv2.line(canvas, (cx, cy - 20), (rad_x, rad_y), green, 1)

    def _draw_paisley_repeat(self, canvas, w, h):
        # Mango / Paisley Motif
        repeat_size = 100
        pink = self.palette[4]
        gold = self.palette[1]

        for x in range(0, w, repeat_size):
            cx, cy = x + 50, h // 2
            # Main Drop
            cv2.ellipse(canvas, (cx, cy + 10), (20, 30), 0, 0, 360, pink, -1)
            # Curved Top (The 'Mango' tip)
            cv2.circle(canvas, (cx - 10, cy - 15), 15, pink, -1)
            # Detail
            cv2.circle(canvas, (cx, cy), 5, gold, -1)

    def generate_border(self, prompt, width_hooks, height_picks):
        """
        Generates a Seamless Saree Border based on prompt.
        """
        print(
            f"Generating Pattern: '{prompt}' for {width_hooks}x{height_picks}")

        # 1. Initialize Canvas
        bg_color = self.palette[0]
        canvas = np.full((height_picks, width_hooks, 3),
                         bg_color, dtype=np.uint8)

        # 2. Remote AI First (If Configured)
        # 2. Remote AI First (Default: Cloud Generation)
        # Even without a key, RemoteAIEngine now falls back to Pollinations
        # (Key-Free)
        print("Attempting Remote AI Generation (Cloud)...")
        pil_image, status = self.remote_ai.generate_design(
            f"{prompt}, border design")

        if pil_image:
            # Resize to fit loop using NEAREST NEIGHBOR (Graph Paper Style)
            pil_image = pil_image.resize(
                (width_hooks, height_picks), Image.NEAREST)

            # Convert to QImage
            data = np.array(pil_image)
            # Ensure RGB
            if len(data.shape) == 3 and data.shape[2] == 4:
                data = cv2.cvtColor(data, cv2.COLOR_RGBA2RGB)
            elif len(data.shape) == 2:
                data = cv2.cvtColor(data, cv2.COLOR_GRAY2RGB)

            # Quantize Colors (Map to Palette)
            data = self._quantize_to_palette(data)

            # RGB->BGR for internal logic
            return self._numpy_to_qimage(data[:, :, ::-1])
        else:
            print(f"Remote AI Failed ({status}). Falling back to procedural.")

        # 3. Procedural Logic (Fallback / Default)
        if "peacock" in prompt:
            self._draw_peacock_repeat(canvas, width_hooks, height_picks)
        elif "paisley" in prompt or "mango" in prompt:
            self._draw_paisley_repeat(canvas, width_hooks, height_picks)
        elif "lattice" in prompt or "check" in prompt or "diamond" in prompt:
            self._draw_complex_lattice(canvas, width_hooks, height_picks)
        elif "geometric" in prompt:
            self._draw_geometric_motif(canvas, width_hooks, height_picks)
        else:
            # Default to Traditional Veldhari
            self._draw_floral_motif(canvas, width_hooks, height_picks)

        # 4. Add Zari Borders
        self._add_zari_border(canvas)

        # 5. Enforce strict palette (cleanup any anti-aliasing)
        canvas = self._quantize_to_palette(canvas)

        return self._numpy_to_qimage(canvas)

    def _quantize_to_palette(self, image):
        """
        Snap all pixels to nearest palette color (Graph Paper Style).
        No gradients, no anti-aliasing - strict palette enforcement.
        """
        h, w, c = image.shape

        # Convert palette to numpy array for distance calculation
        palette_array = np.array(self.palette, dtype=np.float32)

        # Reshape image for vectorized distance calculation
        pixels = image.reshape(-1, 3).astype(np.float32)

        # For each pixel, find nearest palette color
        # Using broadcasting: (n_pixels, 1, 3) - (1, n_colors, 3)
        distances = np.linalg.norm(
            pixels[:, np.newaxis, :] - palette_array[np.newaxis, :, :],
            axis=2
        )

        # Get index of nearest color
        nearest_indices = np.argmin(distances, axis=1)

        # Map to palette colors
        quantized = palette_array[nearest_indices].astype(np.uint8)

        # Reshape back
        return quantized.reshape(h, w, c)

    def _generate_with_gan(self, w, h):
        """
        Generates pattern using trained Progressive GAN models (64, 128, 256)
        Falls back to Smart Patch Engine if AI fails
        """
        from sj_das.core.logging_config import log
        try:
            # Try Progressive GAN models first
            from sj_das.core.unified_ai_engine import get_engine

            engine = get_engine()
            log.info(
                f"Unified Engine Loaded. Models: {engine.available_models.keys()}")

            # Generate with best quality model (256x256)
            print("Using trained Progressive GAN (256x256)...")
            img = engine.generate(
                "custom trained design", w, h, quality='best')

            if img is not None:
                log.info(f"Generated with AI: {img.shape}")
                print(f"✓ Generated with AI: {img.shape}")
                return img
            else:
                log.warning("Unified Engine returned None")

        except Exception as e:
            log.error(f"Progressive GAN failed: {e}", exc_info=True)
            # Re-raise so UI sees it
            raise RuntimeError(f"Progressive GAN Failed: {e}")

        # Fallback to Smart Patch Engine
        try:
            from sj_das.core.smart_patch_engine import SmartPatchEngine

            # Use absolute path for robustness
            base_path = os.path.dirname(
                os.path.abspath(__file__))  # sj_das/core
            project_root = os.path.dirname(os.path.dirname(
                os.path.dirname(base_path)))  # sj_das_project

            data_dir = os.path.join(
                project_root, "dataset", "massive_training")
            if not os.path.exists(data_dir):
                data_dir = os.path.join(project_root, "dataset", "designs")
                if not os.path.exists(data_dir):
                    data_dir = os.path.join(project_root, "dataset")

            if not os.path.exists(data_dir):
                data_dir = os.path.join(project_root, "dataset")

            log.info(f"Using Smart Patch Dataset: {data_dir}")

            engine = SmartPatchEngine(data_dir)
            img = engine.generate(w, h, style="mirror_quad")

            if img is not None:
                logging.info(f"Generated with Smart Patch: {img.shape}")
                print(f"✓ Generated with Smart Patch: {img.shape}")
                return img

        except Exception as e:
            log.error(f"Smart Generation Error: {e}", exc_info=True)
            print(f"Smart Generation Error: {e}")

        return None

    def _draw_cellular_automata(self, canvas, w, h):
        """Generates Rule 30 Cellular Automata Pattern (Complex Logic)."""
        # Grid: 0 or 1
        cells = np.zeros(w, dtype=np.uint8)
        cells[w // 2] = 1  # Seed

        color_fg = self.palette[1]  # Gold

        for y in range(h):
            # Draw current generation
            row_mask = cells == 1
            # Assignment slices handled by numpy
            for x in np.where(row_mask)[0]:
                # Pixel Perfect Draw (1px)
                canvas[y, x] = color_fg

            l = np.roll(cells, -1)
            r = np.roll(cells, 1)
            c = cells
            cells = np.bitwise_xor(l, np.bitwise_or(c, r))

    def _draw_fractal_mandala(self, canvas, w, h):
        """Generates a Kaleidoscopic Fractal (Symmetry)."""
        center_x, center_y = w // 2, h // 2
        radius = min(w, h) // 2 - 20

        # 1. Generate one wedge of random noise/shapes
        wedge = np.zeros((h, w, 3), dtype=np.uint8)

        for _ in range(20):
            rx = np.random.randint(center_x, center_x + radius)
            ry = np.random.randint(center_y, center_y + radius)
            # Small radius for pixel look
            s_rad = np.random.randint(2, 8)
            color = self.palette[np.random.randint(1, 5)]
            cv2.circle(wedge, (rx, ry), s_rad, color, -1, lineType=cv2.LINE_4)

        # 2. Rotate and blend (8-way symmetry)
        for angle in range(0, 360, 45):
            rad = np.radians(angle)
            c, s = np.cos(rad), np.sin(rad)
            R = np.array(((c, -s), (s, c)))

            # Draw a pattern rotated
            pts = np.array([[0, -50], [20, 0], [0, 100],
                           [-20, 0]], dtype=np.float32)
            pts_rot = pts @ R.T
            pts_rot[:, 0] += center_x
            pts_rot[:, 1] += center_y
            pts_final = pts_rot.astype(int)

            color = self.palette[(angle // 45) % 4 + 1]
            cv2.fillConvexPoly(canvas, pts_final, color, lineType=cv2.LINE_4)
            # Remove Polylines to avoid border noise, keep it fill-only for
            # clean blocks

    def _draw_geometric_motif(self, canvas, w, h):
        # Diamonds
        color = (0, 215, 255)  # Gold
        for i in range(0, w, 60):
            pts = np.array([[i + 30, h // 2 - 40], [i + 60, h // 2],
                           [i + 30, h // 2 + 40], [i, h // 2]], np.int32)
            cv2.fillPoly(canvas, [pts], color, lineType=cv2.LINE_4)

    def _draw_floral_motif(self, canvas, w, h):
        """Generates 'Veldhari' style continuous creeper pattern (Pinterest Graphic Style)."""
        # Pixel-perfect jagged lines (No anti-aliasing) for Graph Paper look
        color_stem = self.palette[3]  # Green
        color_flower = self.palette[4]  # Pink
        color_gold = self.palette[1]   # Gold

        freq = 4  # Cycles
        amp = h // 3

        # Veldhari: Sine wave with dot/diamond at peaks
        for x in range(w):
            # Main Vine
            angle = (x / w) * (2 * np.pi * freq)
            y = int(h // 2 + amp * np.sin(angle))

            # Draw pixel manually for graph look
            if 0 <= y < h:
                canvas[y, x] = color_stem
                canvas[y + 1, x] = color_stem  # Thicken slightly

            # Crossing Vine (Double Veldhari)
            y2 = int(h // 2 + amp * np.sin(angle + np.pi))
            if 0 <= y2 < h:
                canvas[y2, x] = color_gold

        # Motifs at peaks
        pts_per_cycle = w // freq
        for i in range(freq * 2):
            cx = int((i + 0.25) * pts_per_cycle / 2)
            cy = h // 2

            # Rudraksha / Diamond Motif at center
            r = 12
            # Diamond shape manually
            pts = np.array([
                [cx, cy - r], [cx + r, cy], [cx, cy + r], [cx - r, cy]
            ], np.int32)
            cv2.fillConvexPoly(canvas, pts, color_flower, lineType=cv2.LINE_4)

            # Center dot
            cv2.rectangle(canvas, (cx - 2, cy - 2),
                          (cx + 2, cy + 2), color_gold, -1)

    def _draw_complex_lattice(self, canvas, w, h):
        """Generates 'Malli Moggu' (Jasmine Bud) Lattice."""
        color_grid = self.palette[5]  # Silver
        self.palette[1]  # Gold

        spacing = 40

        # Draw Diamond Grid
        for i in range(-h, w + h, spacing):
            # Diagonal /
            cv2.line(canvas, (i, 0), (i + h, h),
                     color_grid, 1, lineType=cv2.LINE_4)
            # Diagonal \
            cv2.line(canvas, (i, h), (i + h, 0),
                     color_grid, 1, lineType=cv2.LINE_4)

        # Draw Bud at intersections
        # intersections are at ... logic needed
        # Simplified: Loop through grid points
        # Grid is at (x, y) where lines cross
        pass  # To be implemented if 'lattice' requested

    def _add_zari_border(self, canvas):
        # Gold Strips at top and bottom
        h, w = canvas.shape[:2]
        gold = (0, 215, 255)
        cv2.rectangle(canvas, (0, 0), (w, 20), gold, -1, lineType=cv2.LINE_4)
        cv2.rectangle(canvas, (0, h - 20), (w, h),
                      gold, -1, lineType=cv2.LINE_4)

    def inpaint_design(self, image_bgr, mask_uint8, prompt):
        """
        Smart Inpainting: Generates new content for masked area.
        Uses Poisson Blending for seamless integration.
        """
        # 1. Bounding Box of Mask
        pts = cv2.findNonZero(mask_uint8)
        if pts is None:
            return image_bgr
        x, y, w, h = cv2.boundingRect(pts)

        print(f"Inpainting area: {w}x{h} with prompt '{prompt}'")

        # 2. Generate Content for this size
        # Generate raw texture/pattern
        patch = self.generate_border(prompt, w, h)

        # Convert QImage result back to BGR Numpy
        patch = patch.convertToFormat(QImage.Format.Format_RGB888)
        ptr = patch.bits()
        ptr.setsize(h * w * 3)
        patch_arr = np.array(ptr).reshape(h, w, 3)
        # QImage RGB -> BGR for OpenCV
        patch_bgr = patch_arr[:, :, ::-1].copy()

        # 3. Seamless Clone (Poisson Blending)
        # Center of blend
        center = (x + w // 2, y + h // 2)

        # Create mask for patch (255 where we want to paste)
        # We need the source mask to match source size
        patch_mask = mask_uint8[y:y + h, x:x + w].copy()

        try:
            # Check sizes
            if patch_bgr.shape[:2] != patch_mask.shape[:2]:
                patch_bgr = cv2.resize(
                    patch_bgr, (patch_mask.shape[1], patch_mask.shape[0]))

            # Normal Clone attempts to preserve background texture/lighting
            # Mixed Clone is even better for transparency
            result = cv2.seamlessClone(
                patch_bgr,
                image_bgr,
                patch_mask,
                center,
                cv2.NORMAL_CLONE)
            return result

        except Exception as e:
            print(f"Seamless Clone failed: {e}. Falling back to direct copy.")
            # Fallback: Direct Copy
            out = image_bgr.copy()
            roi = out[y:y + h, x:x + w]

            # Boolean indexing copy
            mask_bool = patch_mask > 0
            roi[mask_bool] = patch_bgr[mask_bool]

            out[y:y + h, x:x + w] = roi
            return out

    def _numpy_to_qimage(self, img):
        h, w, c = img.shape
        # RGB Swapped for QImage
        img_rgb = img[..., ::-1].copy()
        return QImage(img_rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888)
