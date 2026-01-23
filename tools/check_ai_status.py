import os
from pathlib import Path

MODELS_DIR = Path("sj_das/assets/models")
SAM = MODELS_DIR / "sam/sam_vit_h_4b8939.pth"
SD = MODELS_DIR / "stable_diffusion/dreamshaper_8.safetensors"
LLM = MODELS_DIR / "llm/Llama-3.2-3B-Instruct-Q4_K_M.gguf"


def check_status():
    print("=== AI Model Status Check ===\n")

    models = [
        ("Llama 3.2 (Intelligence)", LLM, 2.0),
        ("SAM Huge (Segmentation)", SAM, 2.4),
        ("DreamShaper 8 (Vision)", SD, 2.0)
    ]

    all_ready = True
    for name, path, expected_gb in models:
        if path.exists():
            size_gb = path.stat().st_size / (1024**3)
            status = "✅ Ready" if size_gb > (
                expected_gb * 0.9) else "⚠️ Downloading..."
            print(f"{name:<30} : {status:<15} ({size_gb:.2f} GB)")
            if "Downloading" in status:
                all_ready = False
        else:
            print(f"{name:<30} : ❌ Missing")
            all_ready = False

    print("\n" + "=" * 30)
    if all_ready:
        print("🎉 All Systems Operational!")
    else:
        print("⏳ Downloads in progress. Please wait.")


if __name__ == "__main__":
    check_status()
