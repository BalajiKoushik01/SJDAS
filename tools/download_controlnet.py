import os

import requests


def download_controlnet():
    print("--- ControlNet (Canny) Downloader ---")
    print("Downloading 'control_v11p_sd15_canny.pth' (1.45 GB)...")

    url = "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth"
    dest_dir = os.path.join(
        os.getcwd(),
        "sj_das",
        "assets",
        "models",
        "controlnet")

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    filename = os.path.join(dest_dir, "control_v11p_sd15_canny.pth")

    if os.path.exists(filename):
        print("ControlNet model already exists. Skipping.")
        return

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                # 10MB chunks
                for chunk in r.iter_content(chunk_size=1024 * 1024 * 10):
                    if chunk:
                        f.write(chunk)
                        print(".", end="", flush=True)
        print("\nControlNet Download Complete.")
    except Exception as e:
        print(f"\nFailed to download ControlNet: {e}")


if __name__ == "__main__":
    download_controlnet()
