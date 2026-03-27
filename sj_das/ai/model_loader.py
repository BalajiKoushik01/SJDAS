"""
AI Model Loader - Load and manage trained textile segmentation model
Provides inference for segmentation, pattern classification, and weave detection
"""

from pathlib import Path
import logging

try:
    import cv2
    import numpy as np
    import torch
    import torch.nn.functional as F
    _AI_LIBS_AVAILABLE = True
except Exception as e:
    logging.warning(f"ModelLoader: Core AI libraries unavailable: {e}")
    cv2 = None
    np = None
    torch = None
    F = None
    _AI_LIBS_AVAILABLE = False

# Import model architecture
try:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from textile_model import TextileSegmentationModel
    TEXTILE_MODEL_AVAILABLE = True
except Exception as e:
    logging.warning(f"Textile segmentation model architecture not available: {e}")
    TEXTILE_MODEL_AVAILABLE = False
    TextileSegmentationModel = None


class TextileAIModel:
    """Manages the trained AI model for textile design analysis."""

    def __init__(self, model_path: str = "models/textile_ai/best_model.pth"):
        self.model_path = Path(model_path)
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.loaded = False

        # Class mappings
        self.pattern_types = {
            0: "Border", 1: "Pallu", 2: "Blouse", 3: "Broket", 4: "Other"
        }
        self.weave_types = {
            0: "Jeri", 1: "Ani", 2: "Meena", 3: "Other"
        }
        self.segment_types = {
            0: "Body", 1: "Border", 2: "Pallu"
        }

    def load_model(self) -> bool:
        """Load the trained model from checkpoint."""
        try:
            if not self.model_path.exists():
                print(f"Model not found: {self.model_path}")
                return False

            print(f"Loading AI model from {self.model_path}...")

            # Load checkpoint
            checkpoint = torch.load(self.model_path, map_location=self.device)

            # Initialize model
            self.model = TextileSegmentationModel()
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()

            self.loaded = True

            # Print model info
            print("✅ Model loaded successfully!")
            print(f"   Device: {self.device}")
            print(f"   Epoch: {checkpoint.get('epoch', 'unknown')}")
            print(f"   Val Loss: {checkpoint.get('val_loss', 'unknown'):.4f}")
            print(
                f"   Seg Acc: {checkpoint.get('val_seg_acc', 'unknown'):.2f}%")
            print(
                f"   Pattern Acc: {checkpoint.get('val_pattern_acc', 'unknown'):.2f}%")
            print(
                f"   Weave Acc: {checkpoint.get('val_weave_acc', 'unknown'):.2f}%")

            return True

        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def preprocess_image(self, image: 'np.ndarray') -> 'torch.Tensor':
        """Preprocess image for model input."""
        if not cv2 or not np or not torch: return None
        # Resize to model input size (512x512)
        img = cv2.resize(image, (512, 512), interpolation=cv2.INTER_LINEAR)

        # Convert to RGB if needed
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        elif img.shape[2] == 3 and image.dtype == np.uint8:
            # Assume BGR, convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Normalize (ImageNet stats)
        img = img.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img = (img - mean) / std

        # To tensor [B, C, H, W]
        tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)

        return tensor.float()

    def predict(self, image: 'np.ndarray') -> dict:
        """
        Run complete prediction on image using optimized inference.
        """
        if not self.loaded and not self.load_model():
            return None

        try:
            # Preprocess
            original_shape = image.shape[:2]
            tensor = self.preprocess_image(image).to(self.device)

            # Optimization: Use Half Precision (FP16) if on CUDA
            use_amp = self.device.type == 'cuda'

            # Inference
            with torch.no_grad():
                if use_amp:
                    with torch.cuda.amp.autocast():
                        outputs = self.model(tensor)
                else:
                    outputs = self.model(tensor)

            # Process segmentation
            seg_logits = outputs['segmentation']
            seg_probs = F.softmax(seg_logits, dim=1)
            seg_pred = seg_logits.argmax(dim=1).squeeze().cpu().numpy()

            # Resize back to original
            seg_mask = cv2.resize(
                seg_pred.astype(np.uint8),
                (original_shape[1], original_shape[0]),
                interpolation=cv2.INTER_NEAREST
            )

            # Process pattern classification
            pattern_logits = outputs['pattern']
            pattern_probs = F.softmax(pattern_logits, dim=1)
            pattern_pred = pattern_logits.argmax(dim=1).item()
            pattern_confidence = pattern_probs[0, pattern_pred].item() * 100

            # Process weave detection
            weave_logits = outputs['weave']
            weave_probs = F.softmax(weave_logits, dim=1)
            weave_pred = weave_logits.argmax(dim=1).item()
            weave_confidence = weave_probs[0, weave_pred].item() * 100

            # Calculate segmentation confidence (average certainty)
            seg_confidence = seg_probs.max(dim=1)[0].mean().item() * 100

            return {
                'segmentation': {
                    'mask': seg_mask,
                    'confidence': seg_confidence,
                    'labels': self.segment_types
                },
                'pattern': {
                    'type': self.pattern_types[pattern_pred],
                    'type_id': pattern_pred,
                    'confidence': pattern_confidence,
                    'all_probabilities': {
                        self.pattern_types[i]: pattern_probs[0, i].item() * 100
                        for i in range(len(self.pattern_types))
                    }
                },
                'weave': {
                    'type': self.weave_types[weave_pred],
                    'type_id': weave_pred,
                    'confidence': weave_confidence,
                    'all_probabilities': {
                        self.weave_types[i]: weave_probs[0, i].item() * 100
                        for i in range(len(self.weave_types))
                    }
                }
            }

        except Exception as e:
            print(f"Prediction error: {e}")
            return None

    def predict_segmentation(
            self, image: 'np.ndarray') -> tuple['np.ndarray', float]:
        """Quick segmentation prediction."""
        result = self.predict(image)
        if result:
            return result['segmentation']['mask'], result['segmentation']['confidence']
        return None, 0.0

    def predict_pattern_type(self, image: 'np.ndarray') -> tuple[str, float]:
        """Quick pattern classification."""
        result = self.predict(image)
        if result:
            return result['pattern']['type'], result['pattern']['confidence']
        return "Unknown", 0.0

    def predict_weave_type(self, image: 'np.ndarray') -> tuple[str, float]:
        """Quick weave detection."""
        result = self.predict(image)
        if result:
            return result['weave']['type'], result['weave']['confidence']
        return "Unknown", 0.0

    def get_confidence_scores(self, image: 'np.ndarray') -> dict[str, float]:
        """Get all confidence scores."""
        result = self.predict(image)
        if result:
            return {
                'segmentation': result['segmentation']['confidence'],
                'pattern': result['pattern']['confidence'],
                'weave': result['weave']['confidence']
            }
        return {'segmentation': 0.0, 'pattern': 0.0, 'weave': 0.0}


# Global singleton instance
_model_instance = None


def get_ai_model() -> TextileAIModel:
    """Get or create global AI model instance."""
    global _model_instance
    if _model_instance is None:
        _model_instance = TextileAIModel()
    return _model_instance
