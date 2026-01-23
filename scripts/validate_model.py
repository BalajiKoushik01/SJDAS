from stylegan_model import StyleGenerator
import json
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn

# Add project root to path
sys.path.append(os.getcwd())

# Import model definition (assuming it matches training script)
# Import model definition


class ModelValidator:
    def __init__(self, model_path,
                 device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.model_path = model_path
        self.results = {}
        self.model = None

    def load_model(self):
        print(f"Loading model from {self.model_path}...")
        try:
            # Recreate model architecture
            # Correct parameters based on training config:
            # z_dim=128, w_dim=128 (default), resolution=512, num_classes=2
            # (Conditional)
            self.model = StyleGenerator(
                z_dim=128, w_dim=128, resolution=512, num_classes=2)
            checkpoint = torch.load(self.model_path, map_location=self.device)

            # Handle different checkpoint formats
            if 'model_state_dict' in checkpoint:
                # Filter out discriminator keys if they are in the same dict
                state_dict = {
                    k.replace(
                        'module.',
                        ''): v for k,
                    v in checkpoint['model_state_dict'].items() if 'discriminator' not in k}
                self.model.load_state_dict(state_dict, strict=True)
            elif 'g_ema' in checkpoint:  # Common StyleGAN key
                self.model.load_state_dict(checkpoint['g_ema'])
            else:
                self.model.load_state_dict(checkpoint)

            self.model.to(self.device).eval()
            print("Model loaded successfully.")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False

    def test_inference_speed(self, n_iter=50):
        print("Testing inference speed...")
        times = []
        with torch.no_grad():
            # Warmup
            z = torch.randn(1, 128).to(self.device)
            _ = self.model(z)

            for _ in range(n_iter):
                start = time.time()
                z = torch.randn(1, 128).to(self.device)
                _ = self.model(z)
                times.append(time.time() - start)

        avg_time = np.mean(times)
        fps = 1.0 / avg_time
        print(f"Average inference time: {avg_time*1000:.2f}ms ({fps:.1f} FPS)")
        self.results['speed'] = {
            'avg_ms': avg_time * 1000,
            'fps': fps,
            'device': self.device
        }

    def test_seamless_tiling(self, n_samples=10):
        print("Testing seamless tiling...")
        scores = []
        with torch.no_grad():
            for _ in range(n_samples):
                z = torch.randn(1, 128).to(self.device)
                img_tensor = self.model(z)

                # Convert to numpy [0, 255] used in OpenCV
                img = (
                    img_tensor.squeeze().permute(
                        1, 2, 0).cpu().numpy() + 1) * 127.5
                img = img.astype(np.uint8)

                # Calculate edge continuity (Top vs Bottom, Left vs Right)
                top_edge = img[0, :, :]
                bottom_edge = img[-1, :, :]
                left_edge = img[:, 0, :]
                right_edge = img[:, -1, :]

                diff_vertical = np.mean(
                    np.abs(
                        top_edge.astype(float) -
                        bottom_edge.astype(float)))
                diff_horizontal = np.mean(
                    np.abs(
                        left_edge.astype(float) -
                        right_edge.astype(float)))

                scores.append((diff_vertical + diff_horizontal) / 2)

        avg_diff = np.mean(scores)
        # Score < 10 is usually invisible to naked eye for 8-bit images
        print(f"Average edge discontinuity: {avg_diff:.2f} (Lower is better)")
        self.results['seamless_score'] = float(avg_diff)
        self.results['is_seamless'] = avg_diff < 15.0

    def test_diversity(self, n_samples=20):
        print("Testing output diversity...")
        # Simple diversity metric: Average pixel distance between generated samples
        # Ideally would use LPIPS, but keeping dependencies minimal
        embeddings = []
        with torch.no_grad():
            for _ in range(n_samples):
                z = torch.randn(1, 128).to(self.device)
                img = self.model(z)
                # Downsample for quick comparison
                thumb = torch.nn.functional.interpolate(
                    img, size=(64, 64), mode='bilinear')
                embeddings.append(thumb.view(-1).cpu().numpy())

        distances = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                dist = np.linalg.norm(embeddings[i] - embeddings[j])
                distances.append(dist)

        avg_dist = np.mean(distances)
        print(f"Diversity Score (Pixel Dist): {avg_dist:.2f}")
        self.results['diversity_score'] = float(avg_dist)

    def test_stability(self, n_iter=100):
        print(f"Testing stability ({n_iter} generations)...")
        success_count = 0
        try:
            with torch.no_grad():
                for i in range(n_iter):
                    z = torch.randn(1, 128).to(self.device)
                    _ = self.model(z)
                    success_count += 1
            print("Stability test passed.")
            self.results['stability'] = {'passed': True, 'success_rate': 100.0}
        except Exception as e:
            print(f"Stability test failed after {success_count} iters: {e}")
            self.results['stability'] = {
                'passed': False,
                'error': str(e),
                'success_count': success_count}

    def save_report(self, path='model_validation_report.json'):
        # Convert numpy types to python native types
        def convert(o):
            if isinstance(o, np.generic):
                return o.item()
            raise TypeError

        with open(path, 'w') as f:
            json.dump(self.results, f, indent=4, default=convert)
        print(f"JSON Report saved to {path}")

        # Generate Markdown Report
        md_path = "model_performance_report.md"
        with open(md_path, 'w') as f:
            f.write("# 🤖 StyleGAN Model Performance Report\n\n")
            f.write(f"**Model**: {self.model_path}\n")
            f.write(f"**Device**: {self.device}\n\n")

            f.write("## 1. Speed & Stability\n")
            speed = self.results.get('speed', {})
            f.write(
                f"- **Inference Speed**: {speed.get('avg_ms', 0):.2f} ms ({speed.get('fps', 0):.1f} FPS)\n")
            stab = self.results.get('stability', {})
            f.write(
                f"- **Stability Test**: {'✅ Passed' if stab.get('passed') else '❌ Failed'}\n")
            if not stab.get('passed'):
                f.write(f"  - Error: {stab.get('error')}\n")

            f.write("\n## 2. Quality Metrics\n")
            seamless = self.results.get('seamless_score', 0)
            is_seamless = self.results.get('is_seamless', False)
            f.write(
                f"- **Seamless Tiling Score**: {seamless:.2f} (Target < 15.0)\n")
            f.write(
                f"  - Status: {'✅ Seamless' if is_seamless else '⚠️ Visible Seams Detected'}\n")

            diversity = self.results.get('diversity_score', 0)
            f.write(
                f"- **Diversity Score**: {diversity:.2f} (Higher is more varied)\n")

            f.write("\n## 3. Conclusion\n")
            if stab.get('passed') and speed.get('fps', 0) > 10:
                f.write("✅ **Model is Production Ready** (Performance-wise)\n")
            else:
                f.write("⚠️ **Optimization Required**\n")

            if not is_seamless:
                f.write(
                    "> **Note**: Tiling artifacts may be visible. Consider post-processing seam removal.\n")

        print(f"Markdown Report saved to {md_path}")


if __name__ == "__main__":
    # Path to your trained model
    MODEL_PATH = "sj_das/models/stylegan_advanced/stylegan_final.pth"

    if not os.path.exists(MODEL_PATH):
        # Fallback to last checkpoint if final doesn't exist
        print(f"Final model not found at {MODEL_PATH}, checking directory...")
        p = Path("sj_das/models/stylegan_advanced")
        checkpoints = sorted(list(p.glob("*.pth")))
        if checkpoints:
            MODEL_PATH = str(checkpoints[-1])
            print(f"Using latest checkpoint: {MODEL_PATH}")
        else:
            print("No models found!")
            sys.exit(1)

    validator = ModelValidator(MODEL_PATH)
    if validator.load_model():
        validator.test_inference_speed()
        validator.test_seamless_tiling()
        validator.test_diversity()
        validator.test_stability()
        validator.save_report()
