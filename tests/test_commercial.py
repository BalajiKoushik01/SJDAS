"""
Professional Test Suite for SJ-DAS Commercial Features.
Covers Licensing, Manufacturing Logic (Channel Splitting), and Theme System.
"""

import json
import os
from pathlib import Path

import cv2
import numpy as np
import pytest

from sj_das.core.licensing import LicenseManager
from sj_das.ui.theme_manager import ThemeManager
from sj_das.weaves.channel_splitter import ChannelSplitter


# --- LICENSING TESTS ---
class TestLicensing:
    def test_trial_default(self):
        """Ensure system defaults to Trial Mode without key."""
        # Use a temporary key path to avoid messing with real one
        mgr = LicenseManager()
        mgr.license_file = "non_existent.key"

        is_pro = mgr.validate()
        assert is_pro is False
        assert mgr.status == "TRIAL"

    def test_pro_activation(self, tmp_path):
        """Ensure valid key activates Pro Mode."""
        mgr = LicenseManager()
        key_file = tmp_path / "license.key"
        mgr.license_file = str(key_file)

        # Create valid key
        data = {
            "machine_id": mgr.machine_id,
            "expiry": "2099-12-31"  # Future date
        }

        with open(key_file, 'w') as f:
            json.dump(data, f)

        is_pro = mgr.validate()
        assert is_pro is True
        assert mgr.status == "PRO"

    def test_expired_license(self, tmp_path):
        """Ensure expired key fails."""
        mgr = LicenseManager()
        key_file = tmp_path / "license_expired.key"
        mgr.license_file = str(key_file)

        data = {
            "machine_id": mgr.machine_id,
            "expiry": "2000-01-01"  # Past date
        }

        with open(key_file, 'w') as f:
            json.dump(data, f)

        is_pro = mgr.validate()
        assert is_pro is False
        assert mgr.status == "EXPIRED"

# --- MANUFACTURING TESTS ---


class TestChannelSplitter:
    def test_splitting_logic(self):
        """Test channel separation on synthetic data."""
        splitter = ChannelSplitter()

        # Create Synthetic Image (100x100)
        # Background: Black (Body)
        # Jari: Yellow (Hue ~30)
        # Meena: Red (Hue ~0/180)

        img = np.zeros((100, 100, 3), dtype=np.uint8)

        # Draw Jari (Gold/Yellow)
        # RGB: (255, 215, 0)
        cv2.rectangle(img, (10, 10), (40, 40), (255, 215, 0), -1)

        # Draw Meena (Red)
        # RGB: (255, 0, 0)
        cv2.rectangle(img, (60, 60), (90, 90), (255, 0, 0), -1)

        masks = splitter.split_channels(img)

        # Assertions
        assert "jari" in masks
        assert "meena" in masks
        assert "body" in masks

        # Jari mask should have pixels in top-left
        assert np.any(masks["jari"][10:40, 10:40])
        # Meena mask should have pixels in bottom-right
        assert np.any(masks["meena"][60:90, 60:90])

    def test_threshold_updates(self):
        """Test dynamic threshold adjustment."""
        splitter = ChannelSplitter()

        lower = np.array([0, 0, 0])
        upper = np.array([180, 255, 255])

        splitter.set_jari_range(lower, upper)
        assert np.array_equal(splitter.jari_lower, lower)

# --- THEME TESTS ---


class TestThemeSystem:
    def test_theme_load(self):
        """Test ThemeManager validation."""
        mgr = ThemeManager()
        # Should default to safe values even if file missing
        assert mgr.current_theme in mgr.THEMES

    def test_stylesheet_generation(self):
        """Test CSS generation."""
        mgr = ThemeManager()
        css = mgr.get_stylesheet()

        assert "background-color" in css
        assert "QPushButton" in css
        # Check if colors are injected
        assert "#" in css


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
