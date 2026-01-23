"""
Comprehensive Silk Saree Dataset Downloader
Downloads multiple silk saree design datasets from Kaggle and public sources
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

# Add project root to path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))


class SilkSareeDatasetDownloader:
    def __init__(self):
        self.base_dir = Path("dataset/silk_saree_designs")
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Multiple dataset sources
        self.kaggle_datasets = [
            {
                "name": "indian-saree-patterns",
                "kaggle_id": "sakshibutala/indian-saree-patterns",
                "description": "1000+ Indian saree patterns (4 classes)"
            },
            {
                "name": "indo-fashion",
                "kaggle_id": "validmodel/indo-fashion-dataset",
                "description": "106K images, 15 categories including sarees"
            }
        ]

    def check_kaggle_cli(self):
        """Install Kaggle CLI if not present"""
        try:
            subprocess.run(["kaggle", "--version"],
                           check=True, capture_output=True)
            print("✓ Kaggle CLI found")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n📥 Installing Kaggle CLI...")
            try:
                subprocess.run([sys.executable, "-m", "pip",
                               "install", "kaggle"], check=True)
                print("✓ Kaggle CLI installed")
                return True
            except Exception as e:
                print(f"✗ Failed to install Kaggle: {e}")
                return False

    def download_kaggle_dataset(self, dataset_info):
        """Download a specific Kaggle dataset"""
        dataset_dir = self.base_dir / dataset_info["name"]
        dataset_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📥 Downloading: {dataset_info['description']}")
        print(f"   Dataset ID: {dataset_info['kaggle_id']}")

        try:
            result = subprocess.run(
                ["kaggle", "datasets", "download", "-d", dataset_info["kaggle_id"],
                 "-p", str(dataset_dir), "--unzip"],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )

            if result.returncode == 0:
                # Count images
                images = list(dataset_dir.rglob(
                    "*.jpg")) + list(dataset_dir.rglob("*.png")) + list(dataset_dir.rglob("*.jpeg"))
                print(
                    f"✓ Downloaded {len(images)} images to {dataset_dir.name}")
                return True
            else:
                print(f"✗ Download failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("✗ Download timed out (dataset too large)")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def download_sample_images(self):
        """Download sample silk saree images from public sources"""
        samples_dir = self.base_dir / "public_samples"
        samples_dir.mkdir(parents=True, exist_ok=True)

        # Public domain / Creative Commons silk saree pattern URLs
        sample_urls = [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Kanchipuram_silk_saree.jpg/800px-Kanchipuram_silk_saree.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Silk_Sarees_01.jpg/640px-Silk_Sarees_01.jpg",
        ]

        print("\n📥 Downloading sample silk saree images...")
        count = 0

        for i, url in enumerate(sample_urls):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    filename = samples_dir / f"silk_saree_sample_{i+1}.jpg"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    count += 1
                    print(f"   ✓ Downloaded sample {i+1}")
            except Exception as e:
                print(f"   ✗ Failed sample {i+1}: {e}")

        print(f"✓ Downloaded {count} sample images")
        return count > 0

    def organize_dataset(self):
        """Organize all downloaded images into a unified structure"""
        organized_dir = self.base_dir / "organized"
        organized_dir.mkdir(parents=True, exist_ok=True)

        print("\n📁 Organizing dataset...")

        # Find all images
        all_images = list(self.base_dir.rglob("*.jpg")) + \
            list(self.base_dir.rglob("*.png")) + \
            list(self.base_dir.rglob("*.jpeg")) + \
            list(self.base_dir.rglob("*.bmp"))

        # Copy to organized folder (avoiding duplicates)
        copied = 0
        for img in all_images:
            if "organized" not in str(img):
                try:
                    dest = organized_dir / f"{img.parent.name}_{img.name}"
                    if not dest.exists():
                        import shutil
                        shutil.copy2(img, dest)
                        copied += 1
                except Exception:
                    pass

        print(f"✓ Organized {copied} images into {organized_dir}")
        return str(organized_dir)

    def run(self):
        """Execute complete download workflow"""
        print("=" * 70)
        print("SILK SAREE DATASET DOWNLOADER")
        print("=" * 70)
        print(f"\n📁 Base directory: {self.base_dir.absolute()}\n")

        # Check Kaggle CLI
        has_kaggle = self.check_kaggle_cli()

        datasets_downloaded = 0

        if has_kaggle:
            # Try downloading Kaggle datasets
            print("\n" + "=" * 70)
            print("KAGGLE DATASETS")
            print("=" * 70)

            for dataset in self.kaggle_datasets:
                if self.download_kaggle_dataset(dataset):
                    datasets_downloaded += 1
                time.sleep(2)  # Rate limiting

        # Download public samples
        print("\n" + "=" * 70)
        print("PUBLIC DOMAIN SAMPLES")
        print("=" * 70)
        self.download_sample_images()

        # Organize everything
        print("\n" + "=" * 70)
        print("ORGANIZATION")
        print("=" * 70)
        organized_path = self.organize_dataset()

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        total_images = len(list(self.base_dir.rglob("*.jpg"))) + \
            len(list(self.base_dir.rglob("*.png"))) + \
            len(list(self.base_dir.rglob("*.jpeg")))

        print(f"✓ Total images downloaded: {total_images}")
        print(f"✓ Organized dataset: {organized_path}")

        if datasets_downloaded == 0 and total_images == 0:
            print("\n⚠️  Note: Kaggle datasets require API credentials")
            print("   Visit: https://www.kaggle.com/docs/api")
            print("   Place kaggle.json in: ~/.kaggle/")

        return organized_path if total_images > 0 else None


if __name__ == "__main__":
    downloader = SilkSareeDatasetDownloader()
    result = downloader.run()

    if result:
        print("\n✅ Dataset ready for training!")
        print(f"   Location: {result}")

        # Trigger training
        print("\n🚀 Starting AI training on silk saree dataset...")
        try:
            from sj_das.core.gan_trainer import PatternGANTrainer
            trainer = PatternGANTrainer(result, output_dir="sj_das/models/gan")
            print(
                f"   Training with {len(list(Path(result).glob('*')))} images...")
            trainer.train(epochs=100, batch_size=32)
        except Exception as e:
            print(f"✗ Training error: {e}")
    else:
        print("\n❌ No datasets downloaded")
