def export_for_loom(self):
    """Export design as loom-ready BMP with metadata."""
    # Get current image from editor
    current_img = self.editor.get_current_image()

    if current_img is None or current_img.size == 0:
        QMessageBox.warning(
            self,
            "No Design",
            "Please create or load a design first")
        return

    # Extract unique colors from image
    if len(current_img.shape) == 3:
        unique_colors_np = np.unique(current_img.reshape(-1, 3), axis=0)
        unique_colors = [QColor(int(c[2]), int(c[1]), int(c[0]))
                         for c in unique_colors_np[:32]]
    else:
        # Grayscale - use single color
        unique_colors = [QColor(0, 0, 0), QColor(255, 255, 255)]

    # Show export dialog
    dialog = LoomExportDialog(unique_colors, parent=self)

    # Pre-fill from import specs if available
    if hasattr(self, 'current_loom_specs'):
        dialog.spin_hooks.setValue(self.current_loom_specs.get("hooks", 480))
        dialog.spin_reed.setValue(self.current_loom_specs.get("reed", 100))
        component = self.current_loom_specs.get("component", "Body")
        dialog.combo_component.setCurrentText(component)

    if dialog.exec() != QDialog.DialogCode.Accepted:
        return

    # Get export configuration
    config = dialog.get_export_config()

    # Ask for save location
    filename, _ = QFileDialog.getSaveFileName(
        self,
        "Export for Loom",
        f"design_{config['component'].lower()}.bmp",
        "BMP Files (*.bmp)"
    )

    if not filename:
        return

    try:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        # Create exporter
        exporter = LoomExporter()

        # Calculate picks (height) from current image
        hooks = config["hooks"]
        current_h, current_w = current_img.shape[:2]
        picks = int(current_h * (hooks / current_w))

        # Export with metadata
        success = exporter.export(
            image=current_img,
            output_path=filename,
            hooks=hooks,
            picks=picks,
            reed=config["reed"],
            component=config["component"],
            weave_map=config["weave_map"],
            validate_float=config["validate_float"],
            designer=config["designer"],
            notes=config["notes"]
        )

        QApplication.restoreOverrideCursor()

        if success:
            # Show summary
            file_size = os.path.getsize(filename)
            QMessageBox.information(
                self,
                "Export Successful",
                f"Loom-ready BMP created:\n\n"
                f"• File: {os.path.basename(filename)}\n"
                f"• Dimensions: {hooks} × {picks}\n"
                f"• Reed: {config['reed']}\n"
                f"• Component: {config['component']}\n"
                f"• Colors: {len(config['weave_map'])}\n"
                f"• Size: {file_size / 1024:.1f} KB\n\n"
                f"Metadata embedded for loom machine."
            )
        else:
            QMessageBox.critical(
                self, "Export Failed", "Failed to create BMP file")

    except Exception as e:
        QApplication.restoreOverrideCursor()
        QMessageBox.critical(self, "Export Error", str(e))
