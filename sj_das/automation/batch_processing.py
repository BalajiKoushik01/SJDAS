"""
Batch Processing and Actions System for SJ-DAS.

Photoshop-style action recording, playback, and batch processing.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List

logger = logging.getLogger("SJ_DAS.BatchProcessing")


@dataclass
class ActionStep:
    """Single step in an action."""
    operation: str  # e.g., "resize", "filter", "adjust"
    parameters: Dict[str, Any]
    timestamp: str


class ActionRecorder:
    """
    Record and playback actions (Photoshop-style).

    Features:
        - Record user actions
        - Save/load actions
        - Playback actions
        - Batch processing
    """

    def __init__(self):
        self.recording = False
        self.current_action = []
        self.actions_library = {}
        self.actions_dir = Path("actions")
        self.actions_dir.mkdir(exist_ok=True)

    def start_recording(self, action_name: str):
        """Start recording a new action."""
        self.recording = True
        self.current_action = []
        self.current_action_name = action_name
        logger.info(f"Started recording action: {action_name}")

    def stop_recording(self) -> str:
        """Stop recording and save action."""
        self.recording = False

        if not self.current_action:
            logger.warning("No steps recorded")
            return None

        # Save action
        action_data = {
            'name': self.current_action_name,
            'steps': [asdict(step) for step in self.current_action],
            'created': datetime.now().isoformat()
        }

        self.actions_library[self.current_action_name] = action_data

        # Save to file
        action_file = self.actions_dir / f"{self.current_action_name}.json"
        with open(action_file, 'w') as f:
            json.dump(action_data, f, indent=2)

        logger.info(
            f"Saved action '{self.current_action_name}' with {len(self.current_action)} steps")
        return self.current_action_name

    def record_step(self, operation: str, parameters: Dict[str, Any]):
        """Record a single step."""
        if not self.recording:
            return

        step = ActionStep(
            operation=operation,
            parameters=parameters,
            timestamp=datetime.now().isoformat()
        )

        self.current_action.append(step)
        logger.debug(f"Recorded step: {operation}")

    def load_action(self, action_name: str) -> bool:
        """Load action from file."""
        action_file = self.actions_dir / f"{action_name}.json"

        if not action_file.exists():
            logger.error(f"Action not found: {action_name}")
            return False

        with open(action_file, 'r') as f:
            action_data = json.load(f)

        self.actions_library[action_name] = action_data
        logger.info(f"Loaded action: {action_name}")
        return True

    def playback_action(
        self,
        action_name: str,
        image_processor: Any,
        progress_callback: Callable[[int, int], None] = None
    ):
        """
        Playback recorded action.

        Args:
            action_name: Name of action to play
            image_processor: Object with methods for each operation
            progress_callback: Called with (current_step, total_steps)
        """
        if action_name not in self.actions_library:
            if not self.load_action(action_name):
                return False

        action = self.actions_library[action_name]
        steps = action['steps']

        logger.info(f"Playing action '{action_name}' ({len(steps)} steps)")

        for i, step_data in enumerate(steps):
            step = ActionStep(**step_data)

            # Call corresponding method on image processor
            if hasattr(image_processor, step.operation):
                method = getattr(image_processor, step.operation)
                method(**step.parameters)
            else:
                logger.warning(f"Operation not found: {step.operation}")

            if progress_callback:
                progress_callback(i + 1, len(steps))

        logger.info(f"Completed action: {action_name}")
        return True

    def list_actions(self) -> List[str]:
        """List all available actions."""
        actions = []

        for action_file in self.actions_dir.glob("*.json"):
            actions.append(action_file.stem)

        return sorted(actions)

    def delete_action(self, action_name: str) -> bool:
        """Delete an action."""
        action_file = self.actions_dir / f"{action_name}.json"

        if action_file.exists():
            action_file.unlink()
            if action_name in self.actions_library:
                del self.actions_library[action_name]
            logger.info(f"Deleted action: {action_name}")
            return True

        return False


class BatchProcessor:
    """
    Batch process multiple images.

    Features:
        - Process folder of images
        - Apply actions
        - Save to output folder
        - Progress tracking
    """

    def __init__(self, action_recorder: ActionRecorder):
        self.recorder = action_recorder

    def batch_process(
        self,
        input_files: List[Path],
        action_name: str,
        output_dir: Path,
        image_processor: Any,
        progress_callback: Callable[[int, int, str], None] = None
    ) -> Dict[str, Any]:
        """
        Batch process multiple images.

        Args:
            input_files: List of image files
            action_name: Action to apply
            output_dir: Output directory
            image_processor: Processor with load/save methods
            progress_callback: Called with (current, total, filename)

        Returns:
            Processing results
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            'total': len(input_files),
            'processed': 0,
            'failed': 0,
            'errors': []
        }

        logger.info(f"Starting batch processing: {len(input_files)} files")

        for i, input_file in enumerate(input_files):
            try:
                if progress_callback:
                    progress_callback(i + 1, len(input_files), input_file.name)

                # Load image
                image_processor.load_image(input_file)

                # Apply action
                self.recorder.playback_action(action_name, image_processor)

                # Save result
                output_file = output_dir / f"processed_{input_file.name}"
                image_processor.save_image(output_file)

                results['processed'] += 1
                logger.debug(f"Processed: {input_file.name}")

            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'file': str(input_file),
                    'error': str(e)
                })
                logger.error(f"Failed to process {input_file.name}: {e}")

        time = timestamp
        logger.info(
            f"Batch processing complete: {results['processed']}/{results['total']} successful")
        return results

    def show_dialog(self):
        """Show batch processing dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Batch Process",
            "Batch Processing dialog allows running actions on folders of images.\nFeature coming soon.")

    def batch_resize(
        self,
        input_files: List[Path],
        target_size: tuple[int, int],
        output_dir: Path,
        maintain_aspect: bool = True,
        progress_callback: Callable[[int, int, str], None] = None
    ) -> Dict[str, Any]:
        """Batch resize images."""
        import cv2

        output_dir.mkdir(parents=True, exist_ok=True)
        results = {'total': len(input_files), 'processed': 0, 'failed': 0}

        for i, input_file in enumerate(input_files):
            try:
                if progress_callback:
                    progress_callback(i + 1, len(input_files), input_file.name)

                # Load and resize
                img = cv2.imread(str(input_file))

                if maintain_aspect:
                    h, w = img.shape[:2]
                    target_w, target_h = target_size
                    aspect = w / h

                    if aspect > target_w / target_h:
                        new_w = target_w
                        new_h = int(target_w / aspect)
                    else:
                        new_h = target_h
                        new_w = int(target_h * aspect)

                    resized = cv2.resize(img, (new_w, new_h))
                else:
                    resized = cv2.resize(img, target_size)

                # Save
                output_file = output_dir / input_file.name
                cv2.imwrite(str(output_file), resized)

                results['processed'] += 1

            except Exception as e:
                results['failed'] += 1
                logger.error(f"Failed to resize {input_file.name}: {e}")

        return results

    def batch_convert_format(
        self,
        input_files: List[Path],
        output_format: str,  # 'png', 'jpg', 'bmp'
        output_dir: Path,
        quality: int = 95,
        progress_callback: Callable[[int, int, str], None] = None
    ) -> Dict[str, Any]:
        """Batch convert image format."""
        import cv2

        output_dir.mkdir(parents=True, exist_ok=True)
        results = {'total': len(input_files), 'processed': 0, 'failed': 0}

        for i, input_file in enumerate(input_files):
            try:
                if progress_callback:
                    progress_callback(i + 1, len(input_files), input_file.name)

                img = cv2.imread(str(input_file))

                output_file = output_dir / f"{input_file.stem}.{output_format}"

                if output_format.lower() in ['jpg', 'jpeg']:
                    cv2.imwrite(
                        str(output_file), img, [
                            cv2.IMWRITE_JPEG_QUALITY, quality])
                else:
                    cv2.imwrite(str(output_file), img)

                results['processed'] += 1

            except Exception as e:
                results['failed'] += 1
                logger.error(f"Failed to convert {input_file.name}: {e}")

        return results


class Droplet:
    """
    Create standalone droplet applications.

    A droplet is a standalone executable that applies
    a specific action to dragged files.
    """

    def __init__(self, action_name: str, action_recorder: ActionRecorder):
        self.action_name = action_name
        self.recorder = action_recorder

    def create_droplet(self, output_path: Path) -> bool:
        """
        Create droplet executable.

        Note: This creates a Python script droplet.
        For true executable, would need PyInstaller.
        """
        droplet_script = f'''#!/usr/bin/env python3
"""
Droplet: {self.action_name}
Auto-generated by SJ-DAS
"""

import sys
from pathlib import Path
from sj_das.batch_processing import ActionRecorder, BatchProcessor

def main():
    if len(sys.argv) < 2:
        print("Drag and drop files onto this droplet")
        return

    input_files = [Path(f) for f in sys.argv[1:]]
    output_dir = Path("droplet_output")

    recorder = ActionRecorder()
    processor = BatchProcessor(recorder)

    results = processor.batch_process(
        input_files,
        "{self.action_name}",
        output_dir,
        None  # Would need actual processor
    )

    print(f"Processed: {{results['processed']}}/{{results['total']}}")

if __name__ == "__main__":
    main()
'''

        output_path.write_text(droplet_script)
        output_path.chmod(0o755)  # Make executable

        logger.info(f"Created droplet: {output_path}")
        return True
