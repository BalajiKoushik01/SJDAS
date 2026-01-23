import os

import torch
from diffusers import FluxPipeline
from huggingface_hub import snapshot_download


def download_flux():
    print("--- Flux.1-Schnell Downloader ---")
    print("This requires ~12GB of disk space.")

    model_id = "black-forest-labs/FLUX.1-schnell"
    dest_dir = os.path.join(os.getcwd(), "sj_das", "assets", "models", "flux")

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    print(f"Downloading {model_id} to cache...")
    try:
        # We trigger the download by instantiating or using snapshot_download
        # snapshot_download is safer as it doesn't try to load model into RAM
        snapshot_download(
            repo_id=model_id,
            local_dir=dest_dir,
            local_dir_use_symlinks=False)
        print("Flux Download Complete.")
    except Exception as e:
        print(f"Flux Download Failed: {e}")


if __name__ == "__main__":
    download_flux()
