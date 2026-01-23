import os

import cv2
import numpy as np

from sj_das.utils.logger import logger


class StyleTransferEngine:
    """
    Applies artistic styles to images using pre-trained Neural Networks (.t7).
    """

    def __init__(self):
        self.models_dir = os.path.join(
            os.getcwd(), 'sj_das', 'assets', 'models', 'style')
        self.available_styles = {
            'Mosaic': 'mosaic.t7',
            'Starry Night': 'starry_night.t7'
        }
        self.net = None
        self.current_style = None

    def load_style(self, style_name):
        if style_name not in self.available_styles:
            logger.error(f"Style {style_name} not found.")
            return False

        model_path = os.path.join(
            self.models_dir,
            self.available_styles[style_name])
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return False

        try:
            self.net = cv2.dnn.readNetFromTorch(model_path)
            self.current_style = style_name
            logger.info(f"Loaded Style: {style_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to load style model: {e}")
            return False

    def apply_style(self, image: np.ndarray) -> np.ndarray:
        if self.net is None:
            logger.error("No style loaded.")
            return image

        try:
            # Resize for speed/memory (maintain aspect ratio)
            h, w = image.shape[:2]
            # Max dimension 800ish for reasonable speed on CPU
            scale = 1.0
            if max(h, w) > 800:
                scale = 800 / max(h, w)
                input_blob = cv2.resize(image, (0, 0), fx=scale, fy=scale)
            else:
                input_blob = image.copy()

            # Preprocess
            blob = cv2.dnn.blobFromImage(input_blob, 1.0, (input_blob.shape[1], input_blob.shape[0]),
                                         (103.939, 116.779, 123.680), swapRB=False, crop=False)

            self.net.setInput(blob)
            output = self.net.forward()

            # Postprocess
            output = output.reshape((3, output.shape[2], output.shape[3]))
            output[0] += 103.939
            output[1] += 116.779
            output[2] += 123.680
            output = output.transpose(1, 2, 0)
            output = np.clip(output, 0, 255).astype(np.uint8)

            # Resize back if needed
            if scale != 1.0:
                output = cv2.resize(
                    output, (w, h), interpolation=cv2.INTER_CUBIC)

            return output

        except Exception as e:
            logger.error(f"Style transfer failed: {e}")
            return image
