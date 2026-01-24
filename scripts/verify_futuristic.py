
import sys
import os
import logging
import numpy as np

# Ensure project root is in path
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verifier")

def verify_futuristic():
    print("\n" + "="*50)
    print("Testing Futuristic AI Features")
    print("="*50)
    
    # 1. Test rembg
    try:
        print("[1/3] Testing Smart Background Eraser (rembg)...")
        from sj_das.ai.smart_eraser import get_smart_eraser
        eraser = get_smart_eraser()
        # Mock image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        res = eraser.remove_background(img)
        print(f"   [SUCCESS] rembg loaded. Output shape: {res.shape}")
    except Exception as e:
        print(f"   [FAIL] rembg error: {e}")

    # 2. Test Transformers LLM
    try:
        print("\n[2/3] Testing Pure-Python LLM (Transformers)...")
        from sj_das.core.engines.llm.transformers_engine import get_transformers_engine
        engine = get_transformers_engine()
        # Just check import, don't trigger download yet
        import transformers
        print(f"   [SUCCESS] Transformers {transformers.__version__} ready.")
    except Exception as e:
        print(f"   [FAIL] Transformers engine error: {e}")

    # 3. Test Virtual Try-On (Flux)
    try:
        print("\n[3/3] Testing Virtual Try-On (Flux)...")
        from sj_das.ai.virtual_try_on import get_tryon_engine
        tryon = get_tryon_engine()
        print("   [SUCCESS] Virtual Try-On Module ready.")
    except Exception as e:
        print(f"   [FAIL] Virtual Try-On error: {e}")

    # 4. Critical UI Check
    try:
        print("\n[4/4] Testing UI Framework (PyQt6)...")
        from PyQt6.QtWidgets import QApplication
        print("   [SUCCESS] PyQt6 is installed.")
    except ImportError:
        print("   [FAIL] PyQt6 MISSING! App will crash.")

if __name__ == "__main__":
    verify_futuristic()
