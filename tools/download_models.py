import os
import sys
import zipfile

import requests

# Best-in-Class Models Configuration
MODELS = {
    "upscale": {
        "EDSR_x4.pb": "https://github.com/Saafke/EDSR_Tensorflow/raw/master/models/EDSR_x4.pb",
        "ESPCN_x4.pb": "https://github.com/fannymonori/TF-ESPCN/raw/master/export/ESPCN_x4.pb"
    },
    "segmentation": {
        "u2net.onnx": "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
    },
    "voice": {
        "vosk-model-small-en-us-0.15.zip": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    },
    "style": {
        "starry_night.t7": "https://github.com/linht-le/style-transfer-models/raw/master/models/eccv16/starry_night.t7",
        "mosaic.t7": "https://cs.stanford.edu/people/jcjohns/fast-neural-style/models/instance_norm/mosaic.t7"
    },
    "vision": {
        # HED Edge Detection (Use local if available, link broken)
        # "deploy.prototxt": "...",
        # "hed_pretrained_bsds.caffemodel": "...",

        # Auto Colorization (Alternative: Direct links)
        "colorization_deploy_v2.prototxt": "https://raw.githubusercontent.com/richzhang/colorization/master/colorization/models/colorization_deploy_v2.prototxt",
        "colorization_release_v2.caffemodel": "https://www.dropbox.com/s/dx0qvhhp5hbcx7z/colorization_release_v2.caffemodel?dl=1",
        "pts_in_hull.npy": "https://github.com/richzhang/colorization/raw/caffe/colorization/resources/pts_in_hull.npy"
    },
    "heavy": {
        # Meta's Segment Anything (ViT-B Base Model)
        "sam_vit_b_01ec64.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    },
    "agi": {
        # Llama 3.2 3B Instruct
        "Llama-3.2-3B-Instruct-Q4_K_M.gguf": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        # Phi-3.5 Mini Instruct
        "Phi-3.5-mini-instruct-Q4_K_M.gguf": "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf"
    },
    "flux": {
        # Flux.1 Schnell handled by Diffusers library auto-download.
        # "flux1-schnell-Q4_K_M.gguf": "..."
    },
    "segmentation": {
        "u2net.onnx": "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx",
        "u2net_human_seg.onnx": "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx"
    },
    "ecosystem": {
        # CLIP for semantic understanding
        "clip-vit-large-patch14.pt": "https://openaipublic.azureedge.net/clip/models/b8cca3fd41ae0c99ba7e8951adf17d267cdb84cd88be6f7c2e0eca1737a03836/ViT-L-14.pt",
        # Real-ESRGAN for superior upscaling
        "RealESRGAN_x4plus.pth": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        # MiDaS for depth estimation
        "dpt_beit_large_512.pt": "https://github.com/isl-org/MiDaS/releases/download/v3_1/dpt_beit_large_512.pt",
    }
}

DEST_DIR = os.path.join(os.getcwd(), "sj_das", "assets", "models")


def download_file(url, text, folder):
    dest_path = os.path.join(DEST_DIR, folder)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    local_filename = os.path.join(dest_path, text)

    if os.path.exists(local_filename):
        print(f"[SKIP] {text} already exists.")
        return

    print(f"[DOWNLOADING] {text} from {url}...")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"[SUCCESS] {text} downloaded.")

        # Unzip if zip
        if local_filename.endswith(".zip"):
            print(f"[EXTRACTING] {text}...")
            with zipfile.ZipFile(local_filename, 'r') as zip_ref:
                zip_ref.extractall(dest_path)
            print(f"[SUCCESS] Extracted to {dest_path}")

    except Exception as e:
        print(f"[ERROR] Failed to download {text}: {e}")


def main():
    print("--- SJ-DAS AI Model Downloader ---")
    print(f"Target Directory: {DEST_DIR}")

    # Upscalers
    for name, url in MODELS["upscale"].items():
        download_file(url, name, "super_res")

    # Segmentation
    for name, url in MODELS["segmentation"].items():
        download_file(url, name, "segmentation")

    # Voice
    for name, url in MODELS["voice"].items():
        download_file(url, name, "voice")

    # Styles
    for name, url in MODELS["style"].items():
        download_file(url, name, "style")

    # Advanced Vision
    for name, url in MODELS["vision"].items():
        download_file(url, name, "vision")

    # Heavy Duty
    for name, url in MODELS["heavy"].items():
        download_file(url, name, "sam")

    # AGI / LLM
    for name, url in MODELS["agi"].items():
        download_file(url, name, "llm")

    # Flux Image Generation
    for name, url in MODELS["flux"].items():
        download_file(url, name, "flux")

    # AI Ecosystem (CLIP, Depth, OCR, etc.)
    for name, url in MODELS["ecosystem"].items():
        download_file(url, name, "ecosystem")

    print("\nAll tasks completed. AI Engines are ready to load.")


if __name__ == "__main__":
    main()
