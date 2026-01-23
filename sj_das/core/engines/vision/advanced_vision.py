import os

import cv2
import numpy as np

from sj_das.utils.logger import logger


class AdvancedVisionEngine:
    """
    Advanced Computer Vision Capabilities.
    1. HED (Holistically-Nested Edge Detection): Deep Learning Sketch extraction.
    2. Auto-Colorization: Automatic coloring of B&W images.
    """

    def __init__(self):
        self.assets_dir = os.path.join(
            os.getcwd(), 'sj_das', 'assets', 'models', 'vision')

    def extract_sketch(self, image: np.ndarray) -> np.ndarray:
        """
        Uses HED Deep Learning model to extract high-quality artistic edges.
        Much better than Canny for textile motifs.
        """
        proto_path = os.path.join(self.assets_dir, "deploy.prototxt")
        model_path = os.path.join(
            self.assets_dir,
            "hed_pretrained_bsds.caffemodel")

        if not os.path.exists(proto_path) or not os.path.exists(model_path):
            logger.warning("HED Model not found. Falling back to Canny.")
            return cv2.Canny(image, 100, 200)

        try:
            class CropLayer(object):
                def __init__(self, params, blobs):
                    self.xstart = 0
                    self.xend = 0
                    self.ystart = 0
                    self.yend = 0

                def getMemoryShapes(self, inputs):
                    inputShape, targetShape = inputs[0], inputs[1]
                    batchSize, numChannels = inputShape[0], inputShape[1]
                    height, width = targetShape[2], targetShape[3]
                    self.ystart = (inputShape[2] - height) // 2
                    self.xstart = (inputShape[3] - width) // 2
                    self.yend = self.ystart + height
                    self.xend = self.xstart + width
                    return [[batchSize, numChannels, height, width]]

                def forward(self, inputs):
                    return [
                        inputs[0][:, :, self.ystart:self.yend, self.xstart:self.xend]]

            cv2.dnn_registerLayer('Crop', CropLayer)
            net = cv2.dnn.readNet(proto_path, model_path)

            h, w = image.shape[:2]
            blob = cv2.dnn.blobFromImage(image, scalefactor=1.0, size=(w, h),
                                         mean=(
                104.00698793, 116.66876762, 122.67891434),
                swapRB=False, crop=False)

            net.setInput(blob)
            out = net.forward()
            out = out[0, 0]
            out = cv2.resize(out, (w, h))
            out = (255 * out).astype("uint8")
            return out

        except Exception as e:
            logger.error(f"HED Error: {e}")
            return cv2.Canny(image, 100, 200)

    def colorize_bw(self, image: np.ndarray) -> np.ndarray:
        """
        Auto-Colorizes a B&W Image.
        """
        proto_path = os.path.join(
            self.assets_dir,
            "colorization_deploy_v2.prototxt")
        model_path = os.path.join(
            self.assets_dir,
            "colorization_release_v2.caffemodel")
        pts_path = os.path.join(self.assets_dir, "pts_in_hull.npy")

        if not os.path.exists(model_path):
            logger.warning("Colorization Model not found.")
            return image

        try:
            net = cv2.dnn.readNetFromCaffe(proto_path, model_path)
            pts = np.load(pts_path)

            # Add cluster centers as 1x1 convolutions to the model
            class8 = net.getLayerId("class8_ab")
            conv8 = net.getLayerId("conv8_313_rh")
            pts = pts.transpose().reshape(2, 313, 1, 1)
            net.getLayer(class8).blobs = [pts.astype("float32")]
            net.getLayer(conv8).blobs = [np.full(
                [1, 313], 2.606, dtype="float32")]

            # Processing
            normalized = image.astype("float32") / 255.0
            lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]  # Extract L

            l_resized = cv2.resize(l_channel, (224, 224))
            l_resized -= 50  # Subtract mean L

            net.setInput(cv2.dnn.blobFromImage(l_resized))
            ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

            ab_resized = cv2.resize(ab, (image.shape[1], image.shape[0]))

            # Merge
            new_lab = np.concatenate(
                (l_channel[:, :, np.newaxis], ab_resized), axis=2)
            new_bgr = cv2.cvtColor(new_lab, cv2.COLOR_LAB2BGR)
            new_bgr = np.clip(new_bgr * 255, 0, 255).astype("uint8")

            return new_bgr

        except Exception as e:
            logger.error(f"Colorization Error: {e}")
            return image
