
import os
import sys
import logging
from pathlib import Path
import requests
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SJ_DAS.ModelDownloader")

def download_file(url, dest_path):
    """Download a file with progress bar."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 # 1 Kibibyte
        
        with open(dest_path, 'wb') as file, tqdm(
            desc=os.path.basename(dest_path),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                size = file.write(data)
                bar.update(size)
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False

def main():
    print("="*60)
    print("   SJ-DAS AI Model Downloader")
    print("   Target: Qwen2.5-Coder-7B-Instruct (GGUF)")
    print("   (Switched from GLM-4 due to download restrictions)")
    print("="*60)
    
    # Target Directory
    base_dir = Path(__file__).parent.parent / "assets" / "models" / "llm"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Qwen2.5-Coder-7B-Instruct-GGUF (Excellent Coding Model, ~5GB)
    # Using 'Qwen' official or 'bartowski' (reliable quantizer)
    model_name = "Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf"
    
    mirrors = [
        # Mirror 1: bartowski (High reliability)
        "https://huggingface.co/bartowski/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf",
        # Mirror 2: Qwen Official (If available in GGUF - usually not directly but let's try a known one)
        # Fallback to another quant
        "https://huggingface.co/MaziyarPanahi/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-7B-Instruct.Q4_K_M.gguf"
    ]
    
    dest_path = base_dir / model_name
    
    if dest_path.exists():
        print(f"\n[INFO] Model already exists at:\n{dest_path}")
        print("To re-download, delete the file first.")
        return
        
    print(f"\nDownloading to: {dest_path}")
    print("Size: ~4.7 GB")
    print("This provides state-of-the-art coding assistance.\n")
    
    for i, url in enumerate(mirrors):
        print(f"\nAttempting Mirror {i+1}...")
        print(f"URL: {url}")
        
        if download_file(url, dest_path):
            print("\n[SUCCESS] AI Model downloaded successfully!")
            print("Restarting the app will now enable AI features.")
            return
        else:
            print(f"[WARN] Mirror {i+1} failed. Trying next...")
            
    print("\n[ERROR] All mirrors failed.")
    print("Please download manually from: https://huggingface.co/bartowski/Qwen2.5-Coder-7B-Instruct-GGUF")
    print(f"Save as: {dest_path}")

if __name__ == "__main__":
    main()
