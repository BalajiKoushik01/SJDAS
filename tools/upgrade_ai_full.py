import os
import shutil
from pathlib import Path

import requests
from tqdm import tqdm

# Configuration
MODELS_DIR = Path("sj_das/assets/models")
SAM_DIR = MODELS_DIR / "sam"
SD_DIR = MODELS_DIR / "stable_diffusion"
VOICE_DIR = MODELS_DIR / "voice"

URLS = {
    "sam_huge": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
    "dreamshaper": "https://civitai.com/api/download/models/128713",  # DreamShaper 8 Pruned
}

PATHS = {
    "sam_huge": SAM_DIR / "sam_vit_h_4b8939.pth",
    "dreamshaper": SD_DIR / "dreamshaper_8.safetensors",
}

OLD_FILES = [
    SAM_DIR / "sam_vit_b_01ec64.pth",
    # Add Vosk folders if found separately
]


def download_file(url, dest_path):
    if dest_path.exists():
        # Check if file size is reasonable (not just an empty placeholder)
        if dest_path.stat().st_size > 100 * 1024 * 1024:  # > 100MB
            print(f"✅ {dest_path.name} already exists.")
            return
        else:
            print(
                f"⚠️ {dest_path.name} exists but looks incomplete. Redownloading...")

    print(f"⬇️ Downloading {dest_path.name}...")
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(dest_path, 'wb') as file, tqdm(
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
        print("Done.")
    except Exception as e:
        print(f"❌ Error downloading {dest_path.name}: {e}")
        if dest_path.exists():
            dest_path.unlink()


def cleanup_old_models():
    print("\n🧹 Cleaning up old models...")
    for old_file in OLD_FILES:
        if old_file.exists():
            try:
                if old_file.is_dir():
                    shutil.rmtree(old_file)
                else:
                    old_file.unlink()
                print(f"Deleted old model: {old_file.name}")
            except Exception as e:
                print(f"Failed to delete {old_file.name}: {e}")

    # Clean Vosk
    for item in VOICE_DIR.glob("vosk-*"):
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            print(f"Deleted legacy voice model: {item.name}")
        except Exception as e:
            print(f"Failed to delete {item.name}: {e}")


if __name__ == "__main__":
    print("=== Best-in-Class AI Upgrade Tool ===")

    cleanup_old_models()

    download_file(URLS["sam_huge"], PATHS["sam_huge"])
    download_file(URLS["dreamshaper"], PATHS["dreamshaper"])

    print("\nNote: Whisper model will be downloaded automatically by faster-whisper on first run.")
    print("Note: Owl-ViT model will be downloaded automatically by transformers on first run.")
    print("=== Upgrade Complete ===")
