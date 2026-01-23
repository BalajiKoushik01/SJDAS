import cv2
import numpy as np

from sj_das.utils.logger import logger


class StyleTransferEngine:
    """
    Artistic Style Transfer using OpenCV.
    Safe, fast implementation (Non-Neural fallback) to ensure stability.
    """

    def apply_style(self, image: np.ndarray, style_name: str) -> np.ndarray:
        """
        Applies an artistic style.
        Args:
            image: BGR
            style_name: 'watercolor', 'sketch', 'oil', 'cartoon', 'neon'
        """
        h, w = image.shape[:2]

        try:
            # 1. Check for Neural Style Models (.t7)
            # star -> starry_night.t7
            # mosaic -> mosaic.t7
            model_map = {
                'starry_night': 'starry_night.t7',
                'mosaic': 'mosaic.t7',
                'candy': 'candy.t7'
            }

            if style_name in model_map:
                import os
                model_dir = os.path.join(
                    os.getcwd(), 'sj_das', 'assets', 'models', 'style')
                model_path = os.path.join(model_dir, model_map[style_name])

                if os.path.exists(model_path):
                    # Neural Style Transfer
                    net = cv2.dnn.readNetFromTorch(model_path)

                    # Preprocessing
                    blob = cv2.dnn.blobFromImage(
                        image, 1.0, (w, h), (103.939, 116.779, 123.680), swapRB=False, crop=False)
                    net.setInput(blob)
                    out = net.forward()

                    # Postprocessing
                    out = out.reshape(3, out.shape[2], out.shape[3])
                    out[0] += 103.939
                    out[1] += 116.779
                    out[2] += 123.680
                    out /= 255.0
                    out = out.transpose(1, 2, 0)
                    out = np.clip(out, 0.0, 1.0)
                    out = (out * 255).astype(np.uint8)
                    return out

            # 2. Fallback to Algorithmic Styles
            if style_name == 'watercolor':
                # Sigma_s controls smoothing, sigma_r controls edge preservation
                # Recolor + Stylization
                res = cv2.stylization(image, sigma_s=60, sigma_r=0.6)
                return res

            elif style_name == 'sketch':
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                inv = 255 - gray
                blur = cv2.GaussianBlur(inv, (21, 21), 0)
                # Dodge blend

                def dodge(a, b):
                    return cv2.divide(a, 255 - b, scale=256)
                res = dodge(gray, blur)
                # Convert back to 3ch
                return cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)

            elif style_name == 'oil':
                # Oil Painting effect (requires contrib module usually, or custom)
                # Checking availability
                if hasattr(cv2, 'xphoto'):
                    res = cv2.xphoto.oilPainting(image, 7, 1)
                    return res
                else:
                    # Simulation: Bilateral + Quantize
                    blur = cv2.bilateralFilter(image, 9, 75, 75)
                    return blur  # Simple fallback

            elif style_name == 'cartoon':
                # Edges
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                gray = cv2.medianBlur(gray, 5)
                edges = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

                # Color
                color = cv2.bilateralFilter(image, 9, 250, 250)

                # Combine
                res = cv2.bitwise_and(color, color, mask=edges)
                return res

            elif style_name == 'neon':
                # Edge glow
                # Find edges (Canny) -> Colorize -> Add
                edges = cv2.Canny(image, 100, 200)
                edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                # Colorize edges (e.g. Cyan)
                edges_color[:, :, 0] = 255  # B
                edges_color[:, :, 1] = 255  # G
                edges_color[:, :, 2] = 0   # R

                # Glow
                blur = cv2.GaussianBlur(edges_color, (15, 15), 0)
                res = cv2.addWeighted(image, 0.5, blur, 1.0, 0)
                return res

            return image

        except Exception as e:
            logger.error(f"Style Error: {e}")
            return image
