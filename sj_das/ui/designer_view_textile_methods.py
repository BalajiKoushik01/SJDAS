def detect_pattern_from_image(self, *args):
    """Detect and extract pattern from any image (Google, photos, etc.)."""
    # Select image file
    path, _ = QFileDialog.getOpenFileName(
        self,
        "Select Image to Detect Pattern",
        "",
        "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
    )

    if not path:
        return

    try:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        # Ask for yarn count
        yarn_count, ok = QInputDialog.getInt(
            self,
            "Yarn Count",
            "How many yarn colors to detect?\n(2-3 typical for most designs)",
            3,  # Default 3 yarns
            2,
            32,
            1
        )

        if not ok:
            QApplication.restoreOverrideCursor()
            return

        # Create pattern detection engine
        pattern_engine = PatternDetectionEngine()

        # Detect pattern
        pattern_graph, info = pattern_engine.extract_from_url(path, yarn_count)

        # Convert graph to RGB for display
        # Create color map for visualization
        colors = [
            (255, 255, 255),  # White
            (0, 0, 0),        # Black
            (255, 0, 0),      # Red
            (0, 255, 0),      # Green
            (0, 0, 255),      # Blue
            (255, 255, 0),    # Yellow
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Cyan
        ]

        h, w = pattern_graph.shape
        rgb_pattern = np.zeros((h, w, 3), dtype=np.uint8)

        for i in range(min(yarn_count, len(colors))):
            mask = pattern_graph == i
            rgb_pattern[mask] = colors[i]

        # Load into editor
        self.editor.set_image(rgb_pattern)

        QApplication.restoreOverrideCursor()

        # Show info
        QMessageBox.information(
            self,
            "Pattern Detected",
            f"Pattern extracted successfully:\n\n"
            f"• Repeat Size: {info['repeat_width']}×{info['repeat_height']} pixels\n"
            f"• Yarn Colors: {info['num_colors']}\n"
            f"• Original: {info['original_size'][0]}×{info['original_size'][1]}\n\n"
            f"The detected pattern is now loaded in the editor.\n"
            f"You can refine it with editing tools!"
        )

    except Exception as e:
        QApplication.restoreOverrideCursor()
        QMessageBox.critical(
            self,
            "Pattern Detection Error",
            f"Failed to detect pattern:\n{str(e)}\n\n"
            f"Try with a clearer image showing repeating motifs."
        )


def show_card_sequence_editor(self, *args):
    """Show card sequence/details editor for jacquard control."""
    # Get current hooks from specs or use default
    hooks = getattr(self, 'current_loom_specs', {}).get('hooks', 480)

    # Show card sequence dialog
    dialog = CardSequenceDialog(hooks=hooks, parent=self)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Get card sequence configuration
        card_config = dialog.get_card_sequence()

        # Store for export
        if not hasattr(self, 'current_loom_specs'):
            self.current_loom_specs = {}

        self.current_loom_specs['card_sequence'] = card_config

        QMessageBox.information(
            self,
            "Card Sequence Configured",
            f"Card lifting sequence configured:\n\n"
            f"• Pattern: {card_config['pattern_type']}\n"
            f"• Cards: {card_config['num_cards']}\n"
            f"• Sequence: {', '.join(map(str, card_config['lifting_sequence']))}\n\n"
            f"This will be included in export metadata."
        )

    def suggest_weave_for_design(self, *args):
        """
        AI Advisor: Analyzes the visual style of the design and suggests
        the appropriate Weave Structure and Hook Count.
        """
        try:
            from sj_das.core.unified_ai_engine import get_engine
            engine = get_engine()

            # Get Image
            image_q = self.editor.get_image()
            if image_q.isNull():
                QMessageBox.warning(
                    self, "No Design", "Please create or import a design first.")
                return

            # Convert to Numpy
            ptr = image_q.bits()
            ptr.setsize(image_q.sizeInBytes())
            arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            # 1. AI Analysis
            if hasattr(self, 'status_label'):
                self.status_label.setText("AI: Identifying textile style...")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            result = engine.classify_style(img_bgr)

            QApplication.restoreOverrideCursor()

            style = result.get('style', 'Unknown')
            conf = result.get('confidence', 0)

            if hasattr(self, 'status_label'):
                self.status_label.setText(
                    f"AI: Identified {style} ({conf:.1f}%)")

            # 2. Map Style to Spec
            specs = {
                'Banarasi': {'weave': 'Satin', 'hooks': 480, 'desc': 'Rich satin weave suitable for heavy gold zari.'},
                'Kanjivaram': {'weave': 'Double Veldhari', 'hooks': 960, 'desc': 'Durable double-warp structure for heavy silk.'},
                'Chanderi': {'weave': 'Plain', 'hooks': 240, 'desc': 'Lightweight plain weave for semi-transparent look.'},
                'Paithani': {'weave': 'Meena', 'hooks': 480, 'desc': 'Intricate Meenakari work requiring specific threading.'},
                'Patola': {'weave': 'Double Ikat', 'hooks': 600, 'desc': 'Complex geometric double-ikat simulation.'},
                'Unknown': {'weave': 'Twill', 'hooks': 480, 'desc': 'Standard universal weave.'}
            }

            rec = specs.get(style, specs['Unknown'])

            # 3. Present Advice
            msg = (f"<h3>AI Design Analysis</h3>"
                   f"Detected Style: <b>{style}</b> ({conf:.1f}% confidence)<br><br>"
                   f"<b>Recommendation:</b><br>"
                   f"• Weave Structure: {rec['weave']}<br>"
                   f"• Loom Hooks: {rec['hooks']}<br>"
                   f"• Reasoning: {rec['desc']}<br><br>"
                   f"<i>Would you like to apply these settings to the Loom Configuration?</i>")

            reply = QMessageBox.question(self, "AI Weave Advisor", msg,
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                # Apply
                if not hasattr(self, 'current_loom_specs'):
                    self.current_loom_specs = {}

                self.current_loom_specs['hooks'] = rec['hooks']
                self.current_loom_specs['weave_type'] = rec['weave']
                if hasattr(self, 'status_label'):
                    self.status_label.setText(f"Applied {rec['weave']} specs.")

        except Exception as e:
            QApplication.restoreOverrideCursor()
            from sj_das.utils.logger import logger
            logger.error(f"AI Weave Advice Error: {e}")
            QMessageBox.warning(self, "AI Error", "Could not analyze design.")
