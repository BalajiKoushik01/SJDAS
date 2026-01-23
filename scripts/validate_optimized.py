from sj_das.ai.model_manager import ModelManager
import logging
import os
import sys

import numpy as np

# Add project root
sys.path.append(os.getcwd())

# Setup Logging
logging.basicConfig(level=logging.INFO)


def calculate_seamless_score(img):
    # Calculate edge continuity
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

    return (diff_vertical + diff_horizontal) / 2


def main():
    print("Initializing optimized ModelManager...")
    manager = ModelManager()

    if not manager.load_stylegan():
        print("Failed to load model")
        sys.exit(1)

    print("\n-------------------------------------------")
    print(" Testing Seamless Optimization (N=20 samples)")
    print("-------------------------------------------")

    raw_scores = []
    optimized_scores = []

    for i in range(20):
        # Generate Raw (No Optimization) using private method call hack or just temporary disable
        # Actually ModelManager allows passing flag now? No, need to update ModelManager logic or expose it.
        # Wait, I added `optimize_seamless` arg to `generate_textile`!

        # Raw
        img_raw = manager.generate_textile(seed=i, optimize_seamless=False)
        score_raw = calculate_seamless_score(img_raw)
        raw_scores.append(score_raw)

        # Optimized
        img_opt = manager.generate_textile(seed=i, optimize_seamless=True)
        score_opt = calculate_seamless_score(img_opt)
        optimized_scores.append(score_opt)

        if i < 3:
            print(f"Sample {i}: Raw={score_raw:.2f} -> Opt={score_opt:.2f}")

    avg_raw = np.mean(raw_scores)
    avg_opt = np.mean(optimized_scores)

    print("\n-------------------------------------------")
    print(f"Final Results:")
    print(f"Original Score: {avg_raw:.2f}")
    print(f"Optimized Score: {avg_opt:.2f}")
    print(f"Improvement: {(1 - avg_opt/avg_raw)*100:.1f}%")

    if avg_opt < 15:
        print("✅ SUCCESS: Target (<15) Achieved!")
    else:
        print("! TARGET MISSED: Need stronger blending.")


if __name__ == "__main__":
    main()
