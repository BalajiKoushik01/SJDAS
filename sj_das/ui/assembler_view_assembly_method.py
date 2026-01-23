def configure_assembly(self):
    """Open assembly configuration dialog."""
    # Create and show assembly config dialog
    dialog = AssemblyConfigDialog(parent=self)

    if dialog.exec() == dialog.DialogCode.Accepted:
        # Get configuration
        config = dialog.get_assembly_config()

        # Create assembly engine
        engine = AssemblyEngine()

        try:
            # Assemble components
            assembled_img = engine.assemble(
                components=config['components'],
                assembly_type=config['assembly_type'],
                khali=config['khali'],
                locking=config['locking']
            )

            # Update status
            self.lbl_status.setText(
                f"Assembly complete: {assembled_img.shape[1]}×{assembled_img.shape[0]} "
                f"({config['khali']} repeats)"
            )

            # Ask for save location
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Assembled BMP",
                f"assembled_{config['khali']}x_khali.bmp",
                "BMP Files (*.bmp)"
            )

            if filename:
                # Calculate dimensions
                hooks, picks = assembled_img.shape[1], assembled_img.shape[0]

                # Create metadata
                metadata = BMPMetadata.create_metadata(
                    hooks=hooks,
                    picks=picks,
                    reed=config['reed'],
                    component="Assembly",
                    khali=config['khali'],
                    locking=config['locking'],
                    weave_map={},
                    yarn_colors=[],
                    designer="SJ-DAS",
                    notes=f"{config['assembly_type']} - {config['pattern_type']}"
                )

                # Save BMP
                cv2.imwrite(filename, assembled_img)

                # Embed metadata
                BMPMetadata.embed(filename, metadata)

                # Show success
                QMessageBox.information(
                    self,
                    "Assembly Exported",
                    f"Saree assembly saved successfully!\n\n"
                    f"• File: {os.path.basename(filename)}\n"
                    f"• Dimensions: {hooks}×{picks}\n"
                    f"• Khali: {config['khali']} repeats\n"
                    f"• Pattern: {config['pattern_type']}\n"
                    f"• Metadata: Embedded"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Assembly Error",
                f"Failed to assemble design:\n{str(e)}"
            )
