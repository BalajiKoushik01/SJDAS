from pathlib import Path

import cv2
import requests


class DatasetExpander:
    def __init__(self, data_dir="dataset/designs"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Public Domain / Creative Commons Pattern URLs
        self.urls = [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Textielfabriek_te_Helmond_Nederlandse_textiel_19e_eeuw_20e_eeuw%2C_objectnr_5132.JPG/640px-Textielfabriek_te_Helmond_Nederlandse_textiel_19e_eeuw_20e_eeuw%2C_objectnr_5132.JPG",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Kelmscott_House%2C_Hammersmith%2C_London_-_Willow_pattern_wallpaper_by_William_Morris_%281874%29.jpg/640px-Kelmscott_House%2C_Hammersmith%2C_London_-_Willow_pattern_wallpaper_by_William_Morris_%281874%29.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Morris_Peacock_and_Dragon_woven_textile_1878.jpg/466px-Morris_Peacock_and_Dragon_woven_textile_1878.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Textile_%28France%29%2C_1725%E2%80%9350_%28CH_18570395%29.jpg/640px-Textile_%28France%29%2C_1725%E2%80%9350_%28CH_18570395%29.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Textile_Design_with_Vertical_Rows_of_Pairs_of_Branches_with_Leaves_and_Pomegranates_Separated_by_Vertical_Stripes_of_Ribbons_Rendered_with_Dots_MET_DP833130.jpg/456px-Textile_Design_with_Vertical_Rows_of_Pairs_of_Branches_with_Leaves_and_Pomegranates_Separated_by_Vertical_Stripes_of_Ribbons_Rendered_with_Dots_MET_DP833130.jpg",
            # Add more as needed
        ]

    def download_new_samples(self):
        print(f"Downloading {len(self.urls)} new samples from internet...")
        count = 0
        for i, url in enumerate(self.urls):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    fname = self.data_dir / f"downloaded_{i}.jpg"
                    with open(fname, 'wb') as f:
                        f.write(response.content)
                    count += 1
            except Exception as e:
                print(f"Failed to download {url}: {e}")
        print(f"Downloaded {count} new base images.")

    def augment_dataset(self, factor=4):
        """Augments dataset by rotating and flipping."""
        print("Augmenting Dataset...")
        files = list(self.data_dir.glob(
            "*.jpg")) + list(self.data_dir.glob("*.png")) + list(self.data_dir.glob("*.bmp"))

        new_count = 0
        for f in files:
            try:
                # Skip already augmented
                if "_aug_" in f.name:
                    continue

                img = cv2.imread(str(f))
                if img is None:
                    continue

                # 1. Flip H
                img_fh = cv2.flip(img, 1)
                cv2.imwrite(
                    str(self.data_dir / f"{f.stem}_aug_fh.jpg"), img_fh)
                new_count += 1

                # 2. Rotate 90
                img_r90 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                cv2.imwrite(
                    str(self.data_dir / f"{f.stem}_aug_r90.jpg"), img_r90)
                new_count += 1

                # 3. Rotate 180
                img_r180 = cv2.rotate(img, cv2.ROTATE_180)
                cv2.imwrite(str(self.data_dir /
                                f"{f.stem}_aug_r180.jpg"), img_r180)
                new_count += 1

            except Exception:
                pass

        print(f"Added {new_count} augmented images.")


if __name__ == "__main__":
    expander = DatasetExpander()
    expander.download_new_samples()
    expander.augment_dataset()
