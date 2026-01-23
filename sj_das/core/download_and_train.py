"""
Dataset Downloader for Training
Downloads textile pattern datasets from public sources
"""
import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))


def download_kaggle_dataset():
    """
    Downloads African Fabric Images dataset from Kaggle
    Requires: kaggle API credentials in ~/.kaggle/kaggle.json
    """
    print("=" * 60)
    print("DATASET DOWNLOADER FOR AI TRAINING")
    print("=" * 60)

    # Create download directory
    download_dir = Path("dataset/training_data")
    download_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 Download directory: {download_dir.absolute()}")

    # Check if kaggle is installed
    try:
        subprocess.run(["kaggle", "--version"],
                       check=True, capture_output=True)
        print("✓ Kaggle CLI found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n⚠️  Kaggle CLI not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip",
                       "install", "kaggle"], check=True)
        print("✓ Kaggle CLI installed")

    # Download dataset
    dataset_name = "ayomikunsamuel/african-fabric-images"
    print(f"\n📥 Downloading dataset: {dataset_name}")
    print("   This may take a few minutes...")

    try:
        result = subprocess.run(
            ["kaggle", "datasets", "download", "-d",
                dataset_name, "-p", str(download_dir), "--unzip"],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("✓ Dataset downloaded successfully!")

            # Count files
            image_files = list(download_dir.rglob("*.jpg")) + \
                list(download_dir.rglob("*.png"))
            print(f"✓ Found {len(image_files)} images")

            return str(download_dir)
        else:
            print(f"✗ Download failed: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print("✗ Download timed out")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\n💡 Note: Kaggle requires API credentials.")
        print("   Visit: https://www.kaggle.com/docs/api#authentication")
        return None


if __name__ == "__main__":
    result = download_kaggle_dataset()
    if result:
        print(f"\n✅ Dataset ready at: {result}")
        print("\n🚀 Starting training...")

        # Trigger training
        from sj_das.core.gan_trainer import PatternGANTrainer

        trainer = PatternGANTrainer(result, output_dir="sj_das/models/gan")
        trainer.train(epochs=50, batch_size=16)
    else:
        print("\n❌ Dataset download failed")
        print("   Falling back to local dataset...")

        # Use local dataset instead
        local_dir = "dataset/designs"
        if Path(local_dir).exists():
            print(f"   Using: {local_dir}")
            from sj_das.core.gan_trainer import PatternGANTrainer
            trainer = PatternGANTrainer(
                local_dir, output_dir="sj_das/models/gan")
            trainer.train(epochs=50, batch_size=16)
