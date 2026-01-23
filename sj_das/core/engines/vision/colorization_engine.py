import os

import cv2
import numpy as np

from sj_das.utils.logger import logger


class ColorizationEngine:
    """
    AI Auto-Colorization for B&W Designs.
    Uses Zhang et al. (ECCV 2016) model.
    """

    def __init__(self):
        self.models_dir = os.path.join(
            os.getcwd(), 'sj_das', 'assets', 'models', 'vision')
        self.prototxt = os.path.join(
            self.models_dir, 'colorization_deploy_v2.prototxt')
        self.model = os.path.join(
            self.models_dir,
            'colorization_release_v2.caffemodel')
        self.points = os.path.join(self.models_dir, 'pts_in_hull.npy')
        self.net = None

    def load_model(self):
        if self.net is not None:
            return True

        if not (os.path.exists(self.prototxt) and os.path.exists(
                self.model) and os.path.exists(self.points)):
            logger.error("Colorization models missing.")
            return False

        try:
            self.net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)
            pts = np.load(self.points)

            # Add cluster centers as 1x1 convolutions
            class8 = self.net.getLayerId("class8_ab")
            conv8 = self.net.getLayerId("conv8_313_rh")
            pts = pts.transpose().reshape(2, 313, 1, 1)
            self.net.getLayer(class8).blobs = [pts.astype("float32")]
            self.net.getLayer(conv8).blobs = [np.full(
                [1, 313], 2.606, dtype="float32")]

            logger.info("Colorization Model Loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load colorization model: {e}")
            return False

    def colorize(self, image: np.ndarray) -> np.ndarray:
        if not self.load_model():
            return image

        try:
            # Check if grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                orig_L = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)[:, :, 0]
            else:
                gray = image
                orig_L = image  # simple assumption

            # Create blob
            img_rgb_norm = cv2.cvtColor(
                image, cv2.COLOR_BGR2RGB).astype("float32") / 255.0
            img_lab = cv2.cvtColor(img_rgb_norm, cv2.COLOR_RGB2Lab)

            input_l = img_lab[:, :, 0]  # Pull out L channel

            # Resize for network
            resized = cv2.resize(input_l, (224, 224))
            resized -= 50  # Mean subtraction

            self.net.setInput(cv2.dnn.blobFromImage(resized))
            ab = self.net.forward()[0, :, :, :].transpose((1, 2, 0))

            # Resize ab back to original
            ab = cv2.resize(ab, (image.shape[1], image.shape[0]))

            # Combine
            L = cv2.split(img_lab)[0]
            colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

            # Convert to BGR
            colorized = cv2.cvtColor(colorized, cv2.COLOR_Lab2BGR)
            colorized = np.clip(colorized, 0, 1)
            colorized = (255 * colorized).astype("uint8")

            return colorized

        except Exception as e:
            logger.error(f"Colorization failed: {e}")
            return image
