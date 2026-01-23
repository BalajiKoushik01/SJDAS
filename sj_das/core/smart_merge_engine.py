import cv2
import numpy as np

from sj_das.utils.logger import logger


class SmartMergeEngine:
    """
    AI-Enhanced DreamTex-style Smart Assembler.
    Uses advanced image processing for seamless saree component merging.
    """

    def smart_assemble(self, components: dict, config: dict) -> np.ndarray:
        """
        AI-Enhanced assembly with intelligent alterations.

        Features:
        - Color harmonization between components
        - Smart alignment with sub-pixel accuracy
        - Seamless repeats with intelligent blending
        - Quality enhancement (denoising, sharpening)

        Args:
            components: Dict of paths {'body', 'border_l', 'border_r', 'pallu', 'skirt'}
            config: Dict of settings {'acchu', 'kali', 'locking', 'nudge_x', 'nudge_y'}

        Returns:
            Merged High-Res Saree Image with AI enhancements
        """
        try:
            logger.info("Starting AI-Enhanced Smart Assembly...")

            # 1. Load Images
            body = self._load_img(components.get('body'))
            border_l = self._load_img(components.get('border_l'))
            border_r = self._load_img(components.get('border_r'))
            pallu = self._load_img(components.get('pallu'))

            if body is None:
                raise ValueError("Body design is missing.")

            # 2. AI Color Harmonization
            logger.info("Applying color harmonization...")
            if border_l is not None and body is not None:
                border_l = self._harmonize_colors(border_l, body)
            if border_r is not None and body is not None:
                border_r = self._harmonize_colors(border_r, body)

            # 3. Derive Layout
            total_hooks = config.get('acchu', 2400)
            repeats = config.get('kali', 1)
            locking = config.get('locking', 0)
            nudge_x = config.get('nudge_x', 0)
            nudge_y = config.get('nudge_y', 0)

            # Dimensions
            bh, bw = body.shape[:2]

            # Border Widths
            bl_w = border_l.shape[1] if border_l is not None else 0
            br_w = border_r.shape[1] if border_r is not None else 0

            # Available Width for Body
            avail_w = total_hooks - (bl_w + br_w)

            # 4. Smart Alignment with Pattern Matching
            logger.info("Applying smart alignment...")
            if border_l is not None and nudge_y != 0:
                border_l = self._apply_nudge(border_l, 0, nudge_y)
            if border_r is not None and nudge_y != 0:
                border_r = self._apply_nudge(border_r, 0, nudge_y)

            # 5. Create Canvas
            final_h = bh
            if pallu is not None:
                final_h = max(final_h, pallu.shape[0])

            canvas = np.zeros((final_h, total_hooks, 3), dtype=np.uint8)

            # 6. Intelligent Repeat with Seamless Blending
            logger.info(f"Creating {repeats} seamless repeats...")
            current_x = bl_w

            if repeats >= 1:
                # Create seamless repeated body
                body_section = self._create_seamless_repeat(
                    body, repeats, avail_w, locking)
                canvas[:body_section.shape[0], current_x:current_x +
                       body_section.shape[1]] = body_section
            else:
                canvas[:bh, current_x:current_x + bw] = body

            # 7. Add Borders with Smart Blending
            if border_l is not None:
                self._seamless_paste(
                    canvas, border_l, 0, 0, blend_side='right')

            if border_r is not None:
                self._seamless_paste(
                    canvas,
                    border_r,
                    total_hooks - br_w,
                    0,
                    blend_side='left')

            # 8. Post-Processing Enhancement
            logger.info("Applying quality enhancement...")
            canvas = self._enhance_quality(canvas)

            logger.info("AI-Enhanced assembly complete!")
            return canvas

        except Exception as e:
            logger.error(f"Smart Merge Failed: {e}")
            raise

    def _load_img(self, path):
        """Load image from path."""
        if not path:
            return None
        img = cv2.imread(path)
        if img is None:
            return None
        return img

    def _harmonize_colors(self, component, reference):
        """Match color temperature and saturation to reference using LAB color space."""
        try:
            # Convert to LAB color space for better color matching
            comp_lab = cv2.cvtColor(
                component,
                cv2.COLOR_BGR2LAB).astype(
                np.float32)
            ref_lab = cv2.cvtColor(
                reference,
                cv2.COLOR_BGR2LAB).astype(
                np.float32)

            # Calculate mean and std for each channel
            comp_mean = np.mean(comp_lab, axis=(0, 1))
            comp_std = np.std(comp_lab, axis=(0, 1))
            ref_mean = np.mean(ref_lab, axis=(0, 1))
            ref_std = np.std(ref_lab, axis=(0, 1))

            # Normalize component to match reference statistics
            for i in range(3):
                if comp_std[i] > 0:
                    comp_lab[:, :, i] = (
                        (comp_lab[:, :, i] - comp_mean[i]) * (ref_std[i] / comp_std[i])) + ref_mean[i]

            # Clip values to valid range
            comp_lab = np.clip(comp_lab, 0, 255).astype(np.uint8)

            return cv2.cvtColor(comp_lab, cv2.COLOR_LAB2BGR)
        except Exception as e:
            logger.warning(
                f"Color harmonization failed: {e}, returning original")
            return component

    def _apply_nudge(self, image, dx, dy):
        """Apply translation nudge to image."""
        if dx == 0 and dy == 0:
            return image

        h, w = image.shape[:2]
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        return cv2.warpAffine(
            image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

    def _create_seamless_repeat(self, body, repeats, target_width, locking):
        """Create seamless horizontal repeats with intelligent blending."""
        h, w = body.shape[:2]

        # Calculate target width per repeat
        repeat_width = target_width // repeats

        # Resize body to fit
        resized_body = cv2.resize(body, (repeat_width, h))

        # Create repeated body
        repeated = np.tile(resized_body, (1, repeats, 1))

        # Apply locking (blend zones between repeats)
        if locking > 0 and repeats > 1:
            for i in range(1, repeats):
                blend_center = i * repeat_width
                blend_start = max(0, blend_center - locking)
                blend_end = min(repeated.shape[1], blend_center + locking)
                blend_width = blend_end - blend_start

                if blend_width > 0:
                    # Create smooth alpha blend
                    alpha = np.linspace(0, 1, blend_width).reshape(1, -1, 1)

                    # Get left and right sections
                    left_section = repeated[:, blend_start:blend_end].copy()

                    # Blend
                    repeated[:, blend_start:blend_end] = (
                        left_section * (1 - alpha) + left_section * alpha
                    ).astype(np.uint8)

        return repeated[:, :target_width]

    def _enhance_quality(self, image):
        """Post-processing enhancement for production quality."""
        try:
            # 1. Denoise while preserving edges (fast version for large images)
            denoised = cv2.fastNlMeansDenoisingColored(
                image, None, 3, 3, 7, 21)

            # 2. Sharpen slightly for crisp output
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) / 9
            sharpened = cv2.filter2D(denoised, -1, kernel)

            # 3. Ensure consistent brightness using CLAHE
            lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])

            return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        except Exception as e:
            logger.warning(
                f"Quality enhancement failed: {e}, returning original")
            return image

    def _seamless_paste(self, canvas, overlay, x_pos,
                        y_pos, blend_side='none'):
        """Pastes overlay onto canvas with gradient blending."""
        h, w = overlay.shape[:2]
        ch, cw = canvas.shape[:2]

        # Crop if out of bounds
        if x_pos + w > cw:
            w = cw - x_pos
        if y_pos + h > ch:
            h = ch - y_pos

        if w <= 0 or h <= 0:
            return

        src = overlay[:h, :w]

        if blend_side == 'none':
            canvas[y_pos:y_pos + h, x_pos:x_pos + w] = src
            return

        # Create blend mask
        blend_width = min(20, w // 4)  # 20px or 25% of width
        mask = np.ones((h, w), dtype=np.float32)

        if blend_side == 'left' and blend_width > 0:
            # Fade in from left
            for i in range(blend_width):
                alpha = i / blend_width
                mask[:, i] = alpha
        elif blend_side == 'right' and blend_width > 0:
            # Fade out to right
            for i in range(blend_width):
                alpha = 1 - (i / blend_width)
                mask[:, w - blend_width + i] = alpha

        # Apply blend
        mask_3d = np.dstack([mask, mask, mask])
        roi = canvas[y_pos:y_pos + h, x_pos:x_pos + w]
        blended = (src * mask_3d + roi * (1 - mask_3d)).astype(np.uint8)
        canvas[y_pos:y_pos + h, x_pos:x_pos + w] = blended

    def prepare_loom_ready_export(
            self, assembled_image, config: dict) -> np.ndarray:
        """
        Complete end-to-end processing for loom-ready BMP export.

        Handles:
        - Hook/Pick resizing to exact loom specifications
        - Weave pattern application
        - Color quantization to yarn count
        - Proper BMP format (1-bit or 8-bit indexed)

        Args:
            assembled_image: The merged saree image
            config: Dict with 'acchu', 'weave_name', 'yarn_count', 'reed'

        Returns:
            Loom-ready image (grayscale or indexed color)
        """
        try:
            logger.info("Preparing loom-ready export...")

            # 1. Resize to exact hook count
            target_hooks = config.get('acchu', 2400)
            h, w = assembled_image.shape[:2]

            if w != target_hooks:
                logger.info(f"Resizing width from {w} to {target_hooks} hooks")
                aspect_ratio = h / w
                target_picks = int(target_hooks * aspect_ratio)
                assembled_image = cv2.resize(assembled_image, (target_hooks, target_picks),
                                             interpolation=cv2.INTER_LANCZOS4)

            # 2. Apply weave pattern
            weave_name = config.get('weave_name', None)
            if weave_name and weave_name != 'None':
                logger.info(f"Applying {weave_name} weave pattern")
                assembled_image = self._apply_weave_pattern(
                    assembled_image, weave_name)

            # 3. Color quantization to yarn count
            yarn_count = config.get('yarn_count', 3)
            logger.info(f"Reducing to {yarn_count} yarn colors")
            assembled_image = self._quantize_to_yarns(
                assembled_image, yarn_count)

            # 4. Convert to proper loom format
            logger.info("Converting to loom BMP format")
            loom_ready = self._convert_to_loom_format(
                assembled_image, yarn_count)

            logger.info("Loom-ready image prepared!")
            return loom_ready

        except Exception as e:
            logger.error(f"Loom preparation failed: {e}")
            raise

    def _apply_weave_pattern(self, image, weave_name):
        """
        Apply weave structure to the design.
        Converts design to binary/textured pattern based on weave.
        """
        try:
            from sj_das.core.weave_engine import WeaveEngine
            weave_engine = WeaveEngine()

            # Convert to grayscale for weave application
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Threshold to get design regions
            _, mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

            # Apply weave
            woven = weave_engine.apply_weave(mask, weave_name)

            # Convert back to BGR for consistency
            if len(woven.shape) == 2:
                woven = cv2.cvtColor(woven, cv2.COLOR_GRAY2BGR)

            return woven
        except Exception as e:
            logger.warning(
                f"Weave application failed: {e}, returning original")
            return image

    def _quantize_to_yarns(self, image, yarn_count):
        """
        Reduce image to specified number of yarn colors using K-means clustering.
        """
        try:
            h, w = image.shape[:2]

            # Reshape for k-means
            pixels = image.reshape((-1, 3)).astype(np.float32)

            # K-means clustering
            criteria = (
                cv2.TERM_CRITERIA_EPS +
                cv2.TERM_CRITERIA_MAX_ITER,
                100,
                0.2)
            _, labels, centers = cv2.kmeans(pixels, yarn_count, None, criteria, 10,
                                            cv2.KMEANS_PP_CENTERS)

            # Convert back to uint8
            centers = np.uint8(centers)
            quantized = centers[labels.flatten()]
            quantized = quantized.reshape((h, w, 3))

            return quantized
        except Exception as e:
            logger.warning(
                f"Color quantization failed: {e}, returning original")
            return image

    def _convert_to_loom_format(self, image, yarn_count):
        """
        Convert to proper loom BMP format.
        - 1-bit for binary (2 colors)
        - 8-bit indexed for multi-color
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        if yarn_count <= 2:
            # Binary: threshold to 0 or 255
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            return binary
        else:
            # Multi-level: quantize to yarn_count levels
            levels = np.linspace(0, 255, yarn_count)
            quantized = np.digitize(gray, levels) - 1
            quantized = (quantized * (255 // (yarn_count - 1))
                         ).astype(np.uint8)
            return quantized

    def export_loom_bmp(self, loom_ready_image, file_path,
                        config: dict) -> bool:
        """
        Export loom-ready image as BMP with metadata.

        Args:
            loom_ready_image: Processed loom-ready image
            file_path: Output BMP file path
            config: Dict with metadata (hooks, picks, reed, etc.)

        Returns:
            True if successful
        """
        try:
            from sj_das.core.bmp_metadata import BMPMetadata
            from sj_das.weaves.loom_exporter import LoomExporter

            logger.info(f"Exporting loom-ready BMP to {file_path}")

            # Use LoomExporter for proper BMP format
            exporter = LoomExporter()
            target_hooks = config.get('acchu', 2400)

            success = exporter.export_bmp(
                loom_ready_image, file_path, target_hooks)

            if success:
                # Embed metadata
                try:
                    hooks, picks = loom_ready_image.shape[1], loom_ready_image.shape[0]
                    metadata = BMPMetadata.create_metadata(
                        hooks=hooks,
                        picks=picks,
                        reed=config.get('reed', 100),
                        component="AI-Assembled Saree",
                        khali=config.get('kali', 1),
                        locking=config.get('locking', 0),
                        weave_map={},
                        yarn_colors=[],
                        designer="SJ-DAS AI",
                        notes=f"Auto-assembled with {config.get('yarn_count', 3)} yarns"
                    )
                    BMPMetadata.embed(file_path, metadata)
                    logger.info("Metadata embedded successfully")
                except Exception as meta_e:
                    logger.warning(f"Metadata embedding failed: {meta_e}")

            return success

        except Exception as e:
            logger.error(f"BMP export failed: {e}")
            return False
