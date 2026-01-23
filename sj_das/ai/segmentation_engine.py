
"""
Segmentation Engine for SJ-DAS.
Handles intelligent separation of Saree components (Body, Border, Pallu).
"""

import logging

import cv2
import numpy as np

logger = logging.getLogger("SJ_DAS.Segmentation")


class SegmentationEngine:
    """
    AI-based Segmentation Engine.
    Uses Computer Vision heuristics as fallback when model is not available.
    """

    def __init__(self):
        self.classes = ['background', 'body', 'border', 'pallu']
        logger.info("Segmentation Engine Initialized")

    def segment_saree(self, image_path: str) -> dict:
        """
        Segment a saree image into components.
        Prioritizes Deep Learning (UNet) from UnifiedAIEngine,
        fails back to Heuristics if model unavailable.
        """
        try:
            # Load Image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")

            h, w = img.shape[:2]
            logger.info(f"Segmenting image: {w}x{h}")

            # --- METHOD 1: DEEP LEARNING (Unified AI) ---
            try:
                from sj_das.core.unified_ai_engine import get_engine
                engine = get_engine()

                # Check if we have a robust model loaded
                if 'unet' in engine.available_models:
                    logger.info("Using AI Model for Segmentation...")
                    masks = engine.predict_segmentation(img)

                    if masks:
                        # Convert masks to temp files for UI consumption
                        # (In V2 UI will accept numpy directly, but current UI uses paths)
                        import os
                        import tempfile
                        temp_dir = tempfile.gettempdir()

                        results = {}
                        for name, mask in masks.items():
                            if name == 'background':
                                continue  # Don't return BG usually

                            # Highlight mask for visibility (e.g. Red for Body)
                            # Actually UI just wants a path to an image representing that layer
                            # Usually the masked original content, OR just the mask?
                            # Looking at code: "self.layers_panel.add_layer(name, path)"
                            # And "image = QImage(path)". So it expects an
                            # image file.

                            # Let's save the Cutout (Component)
                            component = cv2.bitwise_and(img, img, mask=mask)

                            # Make transparent? Qt handles transparency if PNG
                            # Add Alpha channel
                            b, g, r = cv2.split(component)
                            rgba = cv2.merge([b, g, r, mask])

                            path = os.path.join(
                                temp_dir, f"sj_das_seg_{name}.png")
                            cv2.imwrite(path, rgba)
                            results[name.capitalize()] = path

                        if results:
                            return results
            except Exception as e:
                logger.warning(
                    f"AI Segmentation failed, falling back to heuristics: {e}")

            # --- METHOD 2: HEURISTICS (Fallback) ---
            logger.info("Using Heuristic Fallback...")

            # 1. Pallu (Usually the rightmost 20-30% or bottom)
            # Let's assume right side for landscape, bottom for portrait
            if w > h:
                pallu_rect = (int(w * 0.75), 0, w - int(w * 0.75), h)
                border_h = int(h * 0.1)
                border_rect_top = (0, 0, w, border_h)
                border_rect_bot = (0, h - border_h, w, border_h)
            else:
                pallu_rect = (0, int(h * 0.75), w, h - int(h * 0.75))
                border_w = int(w * 0.1)
                # Actually Left/Right for portrait
                border_rect_top = (0, 0, border_w, h)
                border_rect_bot = (w - border_w, 0, border_w, h)

            import os
            import tempfile
            temp_dir = tempfile.gettempdir()

            results = {}

            # Create patches
            # Body (Base)
            body = img.copy()
            # Fade out others? No, simple crop.

            # Pallu
            x, y, pw, ph = pallu_rect
            pallu = img[y:y + ph, x:x + pw]
            path_p = os.path.join(temp_dir, "sj_das_pallu.png")
            cv2.imwrite(path_p, pallu)
            results['Pallu'] = path_p

            # Borders
            # Just do top/bottom for standard saree landscape
            if w > h:
                bh = int(h * 0.1)
                border = img[:bh, :]
                path_b = os.path.join(temp_dir, "sj_das_border.png")
                cv2.imwrite(path_b, border)
                results['Border'] = path_b

                # Crop body
                body = body[bh:h - bh, :int(w * 0.75)]
                path_body = os.path.join(temp_dir, "sj_das_body.png")
                cv2.imwrite(path_body, body)
                results['Body'] = path_body
            else:
                # Minimal fallback
                results['Full Design'] = image_path

            return results

        except Exception as e:
            logger.error(f"Segmentation failed: {e}")
            return {}
