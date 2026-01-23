"""
Intelligent Auto-Correction System - Watch edits and fix issues automatically
Detects proportion errors, color problems, symmetry issues, and more
"""

from dataclasses import dataclass
from typing import Any, Optional

import cv2
import numpy as np


@dataclass
class CorrectionIssue:
    """Represents an issue that was or can be corrected."""
    issue_type: str
    severity: str  # 'low', 'medium', 'high'
    description: str
    auto_fixable: bool
    fix_applied: bool = False
    before_value: Optional[Any] = None
    after_value: Optional[Any] = None


class EditWatcher:
    """Watches editing actions and detects issues in real-time."""

    def __init__(self):
        self.auto_fix_enabled = True
        self.issues_detected = []
        self.fixes_applied = []

        # Thresholds
        self.MIN_BORDER_WIDTH_MM = 50  # 5cm
        self.MIN_PALLU_LENGTH_MM = 1000  # 1 meter
        self.MIN_CONTRAST_PERCENT = 30  # 30% brightness difference

    def watch_edit(self, action: str, image_before: np.ndarray,
                   image_after: np.ndarray, metadata: dict = None) -> tuple[np.ndarray, list[CorrectionIssue]]:
        """
        Watch an edit action and apply auto-corrections if needed.

        Args:
            action: Type of edit ('resize', 'color_change', 'draw', etc.)
            image_before: Image state before edit
            image_after: Image state after edit
            metadata: Additional context (dimensions, pattern type, etc.)

        Returns:
            Tuple of (corrected_image, list_of_issues)
        """
        issues = []
        corrected = image_after.copy()

        if action in ['resize', 'crop', 'scale']:
            issues.extend(self._check_proportions(corrected, metadata))

        if action in ['color_change', 'paint', 'fill']:
            issues.extend(self._check_colors(corrected, metadata))

        if action in ['draw', 'paint', 'paste']:
            issues.extend(self._check_symmetry(corrected, metadata))

        # Apply auto-fixes if enabled
        if self.auto_fix_enabled:
            for issue in issues:
                if issue.auto_fixable and not issue.fix_applied:
                    corrected = self._apply_fix(corrected, issue, metadata)
                    issue.fix_applied = True
                    self.fixes_applied.append(issue)

        self.issues_detected.extend(issues)
        return corrected, issues

    def _check_proportions(self, image: np.ndarray,
                           metadata: dict) -> list[CorrectionIssue]:
        """Check if proportions follow traditional guidelines."""
        issues = []

        if not metadata:
            return issues

        pattern_type = metadata.get('pattern_type')
        width_mm = metadata.get('width_mm', 0)
        length_mm = metadata.get('length_mm', 0)

        # Check border width
        if pattern_type == 'border' and width_mm > 0 and width_mm < self.MIN_BORDER_WIDTH_MM:
            issues.append(CorrectionIssue(
                issue_type='border_too_narrow',
                severity='medium',
                description=f"Border width ({width_mm}mm) is below traditional minimum ({self.MIN_BORDER_WIDTH_MM}mm)",
                auto_fixable=True,
                before_value=width_mm,
                after_value=self.MIN_BORDER_WIDTH_MM
            ))

        # Check pallu length
        if pattern_type == 'pallu' and length_mm > 0 and length_mm < self.MIN_PALLU_LENGTH_MM:
            issues.append(CorrectionIssue(
                issue_type='pallu_too_short',
                severity='high',
                description=f"Pallu length ({length_mm}mm) is below traditional minimum ({self.MIN_PALLU_LENGTH_MM}mm)",
                auto_fixable=True,
                before_value=length_mm,
                after_value=self.MIN_PALLU_LENGTH_MM
            ))

        return issues

    def _check_colors(self, image: np.ndarray,
                      metadata: dict) -> list[CorrectionIssue]:
        """Check color contrast and cultural appropriateness."""
        issues = []

        # Calculate average brightness
        if image.size == 0:
            return issues

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        avg_brightness = np.mean(gray)

        # Check for low contrast (too uniform)
        std_brightness = np.std(gray)
        if std_brightness < 20:  # Very low variance
            issues.append(CorrectionIssue(
                issue_type='low_contrast',
                severity='medium',
                description=f"Design has low color contrast (std: {std_brightness:.1f}). Consider using more contrasting colors for visibility.",
                auto_fixable=True,
                before_value=std_brightness,
                after_value=40
            ))

        # Check brightness extremes
        if avg_brightness < 30:
            issues.append(CorrectionIssue(
                issue_type='too_dark',
                severity='low',
                description="Design is very dark. Consider lightening for better visibility.",
                auto_fixable=True
            ))
        elif avg_brightness > 225:
            issues.append(CorrectionIssue(
                issue_type='too_bright',
                severity='low',
                description="Design is very bright. Consider darkening for traditional look.",
                auto_fixable=True
            ))

        return issues

    def _check_symmetry(self, image: np.ndarray,
                        metadata: dict) -> list[CorrectionIssue]:
        """Check if design is symmetric (important for borders)."""
        issues = []

        pattern_type = metadata.get('pattern_type') if metadata else None

        # Symmetry mainly matters for borders
        if pattern_type != 'border':
            return issues

        h, w = image.shape[:2]

        # Check left-right symmetry
        left_half = image[:, :w // 2]
        right_half = image[:, w // 2:]
        right_half_flipped = np.fliplr(right_half)

        # Resize to same size if needed
        if left_half.shape != right_half_flipped.shape:
            min_w = min(left_half.shape[1], right_half_flipped.shape[1])
            left_half = left_half[:, :min_w]
            right_half_flipped = right_half_flipped[:, :min_w]

        # Calculate difference
        diff = np.mean(
            np.abs(
                left_half.astype(
                    np.float32) -
                right_half_flipped.astype(
                    np.float32)))

        if diff > 30:  # Significant asymmetry
            issues.append(CorrectionIssue(
                issue_type='asymmetric',
                severity='medium',
                description=f"Border is asymmetric (difference: {diff:.1f}). Traditional borders should be symmetric.",
                auto_fixable=True,
                before_value=diff,
                after_value=0
            ))

        return issues

    def _apply_fix(self, image: np.ndarray, issue: CorrectionIssue,
                   metadata: dict) -> np.ndarray:
        """Apply automatic fix for an issue."""

        if issue.issue_type == 'border_too_narrow':
            return self._fix_border_width(image, issue.after_value, metadata)

        elif issue.issue_type == 'pallu_too_short':
            return self._fix_pallu_length(image, issue.after_value, metadata)

        elif issue.issue_type == 'low_contrast':
            return self._fix_contrast(image)

        elif issue.issue_type == 'too_dark':
            return self._fix_brightness(image, increase=True)

        elif issue.issue_type == 'too_bright':
            return self._fix_brightness(image, increase=False)

        elif issue.issue_type == 'asymmetric':
            return self._fix_symmetry(image)

        return image

    def _fix_border_width(self, image: np.ndarray, target_width_mm: int,
                          metadata: dict) -> np.ndarray:
        """Scale border to correct width."""
        current_width = metadata.get('width_mm', image.shape[1])
        scale_factor = target_width_mm / current_width

        new_width = int(image.shape[1] * scale_factor)
        resized = cv2.resize(image, (new_width, image.shape[0]),
                             interpolation=cv2.INTER_LANCZOS4)

        return resized

    def _fix_pallu_length(self, image: np.ndarray, target_length_mm: int,
                          metadata: dict) -> np.ndarray:
        """Extend pallu to correct length."""
        current_length = metadata.get('length_mm', image.shape[0])
        scale_factor = target_length_mm / current_length

        new_height = int(image.shape[0] * scale_factor)
        resized = cv2.resize(image, (image.shape[1], new_height),
                             interpolation=cv2.INTER_LANCZOS4)

        return resized

    def _fix_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast using CLAHE."""
        # Convert to LAB
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        # Merge and convert back
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        return enhanced

    def _fix_brightness(self, image: np.ndarray, increase: bool) -> np.ndarray:
        """Adjust overall brightness."""
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)

        if increase:
            v = np.clip(v.astype(np.int16) + 30, 0, 255).astype(np.uint8)
        else:
            v = np.clip(v.astype(np.int16) - 30, 0, 255).astype(np.uint8)

        hsv = cv2.merge([h, s, v])
        adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

        return adjusted

    def _fix_symmetry(self, image: np.ndarray) -> np.ndarray:
        """Make border symmetric by mirroring left side."""
        h, w = image.shape[:2]

        # Take left half
        left_half = image[:, :w // 2]

        # Mirror it
        right_half = np.fliplr(left_half)

        # Combine
        symmetric = np.hstack([left_half, right_half])

        # Resize to original width if needed
        if symmetric.shape[1] != w:
            symmetric = cv2.resize(symmetric, (w, h),
                                   interpolation=cv2.INTER_LANCZOS4)

        return symmetric

    def get_correction_summary(self) -> str:
        """Get a summary of all corrections applied."""
        if not self.fixes_applied:
            return "No auto-corrections needed - design looks great!"

        summary = f"Applied {len(self.fixes_applied)} auto-corrections:\n"
        for issue in self.fixes_applied:
            summary += f"  • {issue.description}\n"

        return summary


# Global instance
_watcher_instance = None


def get_edit_watcher() -> EditWatcher:
    """Get or create global watcher instance."""
    global _watcher_instance
    if _watcher_instance is None:
        _watcher_instance = EditWatcher()
    return _watcher_instance
