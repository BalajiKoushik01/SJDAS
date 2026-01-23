"""
Batch Processing System for SJ-DAS.
Process multiple files with same AI operations.
"""

import os

import cv2
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (QComboBox, QDialog, QFileDialog, QHBoxLayout,
                             QLabel, QListWidget, QMessageBox, QProgressBar,
                             QPushButton, QVBoxLayout)


class BatchProcessor(QThread):
    """Background thread for batch processing."""

    progress = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(int, int)  # success_count, fail_count

    def __init__(self, files, operation, params=None):
        super().__init__()
        self.files = files
        self.operation = operation
        self.params = params or {}
        self.should_stop = False

    def run(self):
        """Process all files."""
        success = 0
        failed = 0

        for i, file_path in enumerate(self.files):
            if self.should_stop:
                break

            try:
                filename = os.path.basename(file_path)
                self.progress.emit(i + 1, len(self.files), filename)

                # Load image
                image = cv2.imread(file_path)
                if image is None:
                    failed += 1
                    continue

                # Apply operation
                result = self._apply_operation(
                    image, self.operation, self.params)

                # Save result
                output_path = self._get_output_path(file_path)
                cv2.imwrite(output_path, result)

                success += 1

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                failed += 1

        self.finished.emit(success, failed)

    def _apply_operation(self, image, operation, params):
        """Apply the selected operation."""
        if operation == "Resize":
            width = params.get('width', 2400)
            height = params.get('height', 3000)
            return cv2.resize(image, (width, height))

        elif operation == "Color Reduction":
            colors = params.get('colors', 8)
            return self._reduce_colors(image, colors)

        elif operation == "Denoise":
            return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

        elif operation == "Sharpen":
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            return cv2.filter2D(image, -1, kernel)

        elif operation == "Grayscale":
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        else:
            return image

    def _reduce_colors(self, image, n_colors):
        """Reduce image to n colors using k-means."""
        import numpy as np

        h, w = image.shape[:2]
        pixels = image.reshape((-1, 3)).astype(np.float32)

        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10,
                                        cv2.KMEANS_PP_CENTERS)

        centers = np.uint8(centers)
        quantized = centers[labels.flatten()]
        return quantized.reshape((h, w, 3))

    def _get_output_path(self, input_path):
        """Generate output path."""
        directory = os.path.dirname(input_path)
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)

        output_dir = os.path.join(directory, "batch_output")
        os.makedirs(output_dir, exist_ok=True)

        return os.path.join(output_dir, f"{name}_processed{ext}")

    def stop(self):
        """Stop processing."""
        self.should_stop = True


class BatchProcessDialog(QDialog):
    """Batch processing dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []
        self.processor = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Batch Processing")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # File list
        layout.addWidget(QLabel("<b>Files to Process:</b>"))

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # File buttons
        file_btn_layout = QHBoxLayout()

        add_btn = QPushButton("Add Files...")
        add_btn.clicked.connect(self.add_files)
        file_btn_layout.addWidget(add_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_files)
        file_btn_layout.addWidget(clear_btn)

        layout.addLayout(file_btn_layout)

        # Operation selection
        layout.addWidget(QLabel("<b>Operation:</b>"))

        self.operation_combo = QComboBox()
        self.operation_combo.addItems([
            "Resize",
            "Color Reduction",
            "Denoise",
            "Sharpen",
            "Grayscale"
        ])
        layout.addWidget(self.operation_combo)

        # Progress
        layout.addWidget(QLabel("<b>Progress:</b>"))

        self.progress_label = QLabel("Ready")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Action buttons
        action_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        action_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        action_layout.addWidget(self.stop_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        action_layout.addWidget(close_btn)

        layout.addLayout(action_layout)

    def add_files(self):
        """Add files to process."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff);;All Files (*.*)"
        )

        if files:
            self.files.extend(files)
            for file in files:
                self.file_list.addItem(os.path.basename(file))

    def clear_files(self):
        """Clear file list."""
        self.files.clear()
        self.file_list.clear()

    def start_processing(self):
        """Start batch processing."""
        if not self.files:
            QMessageBox.warning(
                self, "No Files", "Please add files to process.")
            return

        operation = self.operation_combo.currentText()

        # Create processor
        self.processor = BatchProcessor(self.files, operation)
        self.processor.progress.connect(self.on_progress)
        self.processor.finished.connect(self.on_finished)

        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setMaximum(len(self.files))
        self.progress_bar.setValue(0)

        # Start
        self.processor.start()

    def stop_processing(self):
        """Stop processing."""
        if self.processor:
            self.processor.stop()

    def on_progress(self, current, total, filename):
        """Update progress."""
        self.progress_bar.setValue(current)
        self.progress_label.setText(
            f"Processing {current}/{total}: {filename}")

    def on_finished(self, success, failed):
        """Processing finished."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        msg = f"Batch processing complete!\n\n"
        msg += f"✅ Successful: {success}\n"
        msg += f"❌ Failed: {failed}\n\n"
        msg += f"Output saved to: batch_output/"

        QMessageBox.information(self, "Complete", msg)
        self.progress_label.setText("Complete!")
