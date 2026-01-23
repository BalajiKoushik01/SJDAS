
import json
import os

import cv2


class ProjectManager:
    """
    Handles Saving/Loading of SJ-DAS Projects (.sjdas format).
    A project is a folder containing:
    - meta.json (Configuration, Loom Settings)
    - original.png (Source Image)
    - mask.png (Segmentation Mask)
    """

    def save_project(self, folder_path, data):
        """
        data = {
            'original': np_array,
            'mask': np_array,
            'meta': dict
        }
        """
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Save Images
        if data['original'] is not None:
            cv2.imwrite(
                os.path.join(
                    folder_path,
                    "original.png"),
                data['original'])

        if data['mask'] is not None:
            cv2.imwrite(os.path.join(folder_path, "mask.png"), data['mask'])

        # Save Meta
        with open(os.path.join(folder_path, "meta.json"), 'w') as f:
            json.dump(data['meta'], f, indent=4)

    def load_project(self, folder_path):
        """Returns dict or None"""
        if not os.path.exists(folder_path):
            return None

        res = {'original': None, 'mask': None, 'meta': {}}

        # Load Images
        p_orig = os.path.join(folder_path, "original.png")
        if os.path.exists(p_orig):
            res['original'] = cv2.imread(p_orig)

        p_mask = os.path.join(folder_path, "mask.png")
        if os.path.exists(p_mask):
            # Load as grayscale/indexed?
            # Mask is stored as visual colors or raw indices?
            # Ideally raw indices. But cv2.imwrite usually saves 3ch if given 3ch, or 1ch.
            # Our mask is 1ch index or 1ch visual?
            # In designer_view, we save get_mask_array (1ch).
            res['mask'] = cv2.imread(p_mask, cv2.IMREAD_UNCHANGED)

        # Load Meta
        p_meta = os.path.join(folder_path, "meta.json")
        if os.path.exists(p_meta):
            with open(p_meta) as f:
                res['meta'] = json.load(f)

        return res
