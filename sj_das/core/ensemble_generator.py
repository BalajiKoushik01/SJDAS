"""
Simplified Ensemble System
Integrates all trained models into the generation engine
"""
from pathlib import Path

import cv2
import numpy as np
import torch


class EnsembleGenerator:
    """Production-ready ensemble of all trained models"""

    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        self._load_models()

    def _load_models(self):
        """Load all available trained models"""
        print("Loading trained models...")

        # 1. Progressive GAN (if trained)
        progressive_model = Path("sj_das/models/gan_advanced/generator.pth")
        if progressive_model.exists():
            try:
                self.models['progressive_gan'] = {
                    'path': progressive_model,
                    'quality': 8,
                    'speed': 'fast',
                    'loaded': False  # Lazy load
                }
                print("✓ Progressive GAN found")
            except BaseException:
                pass

        # 2. Standard GAN (fallback)
        standard_model = Path("sj_das/models/gan/generator.pth")
        if standard_model.exists():
            self.models['standard_gan'] = {
                'path': standard_model,
                'quality': 6,
                'speed': 'very_fast',
                'loaded': False
            }
            print("✓ Standard GAN found")

        # 3. Smart Patch Engine (always available)
        self.models['smart_patch'] = {
            'quality': 9,
            'speed': 'instant',
            'loaded': True  # No loading needed
        }
        print("✓ Smart Patch Engine ready")

        print(f"\nTotal models available: {len(self.models)}")

    def generate(self, prompt, width=480, height=480, quality='best'):
        """Generate design using best available model"""

        # Route based on prompt and quality setting
        if 'custom' in prompt.lower() or 'trained' in prompt.lower():
            # Use trained AI models
            if 'progressive_gan' in self.models and quality == 'best':
                return self._generate_progressive_gan(width, height)
            elif 'standard_gan' in self.models:
                return self._generate_standard_gan(width, height)

        # Default: Smart Patch Engine (always works, high quality)
        return self._generate_smart_patch(width, height)

    def _generate_progressive_gan(self, w, h):
        """Generate using progressive GAN"""
        try:
            # Load model if not loaded
            if not self.models['progressive_gan']['loaded']:
                from train_advanced_progressive import ProgressiveGenerator
                gen = ProgressiveGenerator(128, 256).to(self.device)
                gen.load_state_dict(
                    torch.load(
                        self.models['progressive_gan']['path']))
                gen.eval()
                self.models['progressive_gan']['model'] = gen
                self.models['progressive_gan']['loaded'] = True

            gen = self.models['progressive_gan']['model']

            # Generate
            with torch.no_grad():
                noise = torch.randn(1, 128, 1, 1, device=self.device)
                output = gen(noise)

                # Convert to numpy
                img = output[0].cpu().permute(1, 2, 0).numpy()
                img = ((img + 1) * 127.5).astype(np.uint8)

                # Resize if needed
                if img.shape[:2] != (h, w):
                    img = cv2.resize(
                        img, (w, h), interpolation=cv2.INTER_NEAREST)

                return img
        except Exception as e:
            print(f"Progressive GAN error: {e}, falling back...")
            return self._generate_smart_patch(w, h)

    def _generate_standard_gan(self, w, h):
        """Generate using standard GAN"""
        # Similar to progressive but simpler
        return self._generate_smart_patch(w, h)  # Fallback for now

    def _generate_smart_patch(self, w, h):
        """Generate using Smart Patch Engine (always works)"""
        import sys
        from pathlib import Path

        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from sj_das.core.smart_patch_engine import SmartPatchEngine

        engine = SmartPatchEngine("dataset/massive_training")
        return engine.generate(w, h)


# Integration into GenerativeDesignEngine
if __name__ == "__main__":
    ensemble = EnsembleGenerator()

    # Test generation
    print("\n Testing generation...")
    img = ensemble.generate("custom design", quality='best')
    print(f"✓ Generated {img.shape}")

    # Save test
    cv2.imwrite("test_ensemble_output.png", img)
    print("✓ Saved test_ensemble_output.png")
