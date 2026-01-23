"""
Dataset Alignment Tool for Replication Engine.
Ensures images in dataset/replication/A and B match in filename and dimensions.
"""

import os
from pathlib import Path

from PIL import Image


def align_dataset():
    root = Path("../dataset/replication")
    dir_A = root / "A"
    dir_B = root / "B"

    # Validation
    if not dir_A.exists() or not dir_B.exists():
        print(f"Error: Missing directories. Expected {dir_A} and {dir_B}")
        return

    files_A = {f.stem: f for f in dir_A.glob("*")}
    files_B = {f.stem: f for f in dir_B.glob("*")}

    common = set(files_A.keys()) & set(files_B.keys())
    print(f"Found {len(common)} paired images (by filename).")

    if len(common) == 0:
        print("No matching filenames found. Please name source and target identically (e.g. design1.png)")
        return

    # Resize Logic (Align B to A or fixed size?)
    # For now, we just resize both to 512x512 for standard training?
    # Or keep aspect ratio? Pix2Pix likes squares.

    target_size = (256, 256)

    output_dir = root / "aligned"
    os.makedirs(output_dir / "A", exist_ok=True)
    os.makedirs(output_dir / "B", exist_ok=True)

    for name in common:
        path_A = files_A[name]
        path_B = files_B[name]

        try:
            img_A = Image.open(path_A).convert("RGB").resize(target_size)
            img_B = Image.open(path_B).convert("RGB").resize(target_size)

            img_A.save(output_dir / "A" / f"{name}.png")
            img_B.save(output_dir / "B" / f"{name}.png")
            print(f"Aligned {name}")

        except Exception as e:
            print(f"Failed {name}: {e}")

    print(f"Done! Aligned images saved to {output_dir}")
    print("Point train_replication.py to this folder for best results.")


if __name__ == "__main__":
    align_dataset()
