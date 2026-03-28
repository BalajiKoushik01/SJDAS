import sys
import os
import cv2
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.decode_service import DecodeParams, run_full_pipeline

def test_decode_pipeline():
    print("Testing Decode Pipeline...")
    
    # Create a dummy image for testing
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    dummy_path = "tests/dummy_saree.png"
    cv2.imwrite(dummy_path, dummy_img)
    
    params = DecodeParams(
        image_path=dummy_path,
        hook_count=1200,
        color_count=6
    )
    
    try:
        result = run_full_pipeline(params)
        print("\nPipeline Result:")
        print(f"Style: {result.style_label} ({result.style_confidence:.2f})")
        print(f"Layers: {len(result.layers)}")
        print(f"Colors: {len(result.colors)}")
        print(f"SVG URL: {result.svg_url}")
        print(f"Analysis: {result.analysis_card}")
        
        if result.style_label != "Unknown":
            print("SUCCESS: Pipeline executed logically even with missing models.")
        else:
            print("FAILURE: Pipeline returned Unknown style.")
            
    except Exception as e:
        print(f"ERROR during pipeline execution: {e}")
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)

if __name__ == "__main__":
    test_decode_pipeline()
