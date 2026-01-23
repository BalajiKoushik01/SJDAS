"""
AI Insights Panel - Real-time display of AI analysis and proactive suggestions
Shows pattern/weave predictions, confidence scores, and smart recommendations
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QFrame, QGroupBox, QLabel, QProgressBar,
                             QPushButton, QScrollArea, QVBoxLayout, QWidget)


class AIInsightsPanel(QWidget):
    """Panel showing AI predictions and proactive suggestions."""

    apply_suggestion = pyqtSignal(str, dict)  # action, data

    def __init__(self):
        super().__init__()
        self.current_prediction = None
        self.current_suggestions = []
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("🤖 AI Design Intelligence")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Summary Section
        self.summary_label = QLabel("Load a design to see AI analysis")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("""
            QLabel {
                background: #2d2d2d;
                border: 1px solid #FFD700;
                border-radius: 5px;
                padding: 10px;
                color: white;
            }
        """)
        layout.addWidget(self.summary_label)

        # Pattern Analysis Group
        pattern_group = QGroupBox("Pattern Analysis")
        pattern_layout = QVBoxLayout()

        self.pattern_type_label = QLabel("Type: ---")
        self.pattern_confidence = QProgressBar()
        self.pattern_confidence.setTextVisible(True)
        self.pattern_confidence.setFormat("%p% Confident")

        pattern_layout.addWidget(self.pattern_type_label)
        pattern_layout.addWidget(self.pattern_confidence)
        pattern_group.setLayout(pattern_layout)
        layout.addWidget(pattern_group)

        # Weave Analysis Group
        weave_group = QGroupBox("Weave Detection")
        weave_layout = QVBoxLayout()

        self.weave_type_label = QLabel("Type: ---")
        self.weave_confidence = QProgressBar()
        self.weave_confidence.setTextVisible(True)
        self.weave_confidence.setFormat("%p% Confident")

        weave_layout.addWidget(self.weave_type_label)
        weave_layout.addWidget(self.weave_confidence)
        weave_group.setLayout(weave_layout)
        layout.addWidget(weave_group)

        # Segmentation Quality
        seg_group = QGroupBox("Segmentation Quality")
        seg_layout = QVBoxLayout()

        self.seg_confidence = QProgressBar()
        self.seg_confidence.setTextVisible(True)
        self.seg_confidence.setFormat("%p% Accurate")

        seg_layout.addWidget(self.seg_confidence)
        seg_group.setLayout(seg_layout)
        layout.addWidget(seg_group)

        # Suggestions Section
        suggestions_label = QLabel("💡 Smart Suggestions")
        suggestions_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(suggestions_label)

        # Scrollable suggestions area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self.suggestions_widget = QWidget()
        self.suggestions_layout = QVBoxLayout(self.suggestions_widget)
        self.suggestions_layout.setSpacing(8)
        self.suggestions_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self.suggestions_widget)
        layout.addWidget(scroll, 1)  # Give scroll area most space

        # Actions
        self.refresh_btn = QPushButton("🔄 Refresh Analysis")
        self.refresh_btn.clicked.connect(self.request_refresh)
        layout.addWidget(self.refresh_btn)

    def update_insights(self, prediction: dict, suggestions: list):
        """Update panel with new AI insights."""
        self.current_prediction = prediction
        self.current_suggestions = suggestions

        if not prediction:
            self.summary_label.setText("No prediction available")
            return

        # Update summary
        from sj_das.ai.proactive_assistant import get_proactive_assistant
        assistant = get_proactive_assistant()
        summary = assistant.generate_smart_summary(prediction)
        self.summary_label.setText(summary)

        # Update pattern
        pattern = prediction.get('pattern', {})
        pattern_type = pattern.get('type', 'Unknown')
        pattern_conf = pattern.get('confidence', 0)

        self.pattern_type_label.setText(f"Type: {pattern_type}")
        self.pattern_confidence.setValue(int(pattern_conf))
        self._set_confidence_color(self.pattern_confidence, pattern_conf)

        # Update weave
        weave = prediction.get('weave', {})
        weave_type = weave.get('type', 'Unknown')
        weave_conf = weave.get('confidence', 0)

        self.weave_type_label.setText(f"Type: {weave_type}")
        self.weave_confidence.setValue(int(weave_conf))
        self._set_confidence_color(self.weave_confidence, weave_conf)

        # Update segmentation
        seg = prediction.get('segmentation', {})
        seg_conf = seg.get('confidence', 0)

        self.seg_confidence.setValue(int(seg_conf))
        self._set_confidence_color(self.seg_confidence, seg_conf)

        # Update suggestions
        self._update_suggestions(suggestions)

    def _set_confidence_color(
            self, progress_bar: QProgressBar, confidence: float):
        """Set progress bar color based on confidence level."""
        if confidence >= 90:
            color = "#4CAF50"  # Green
        elif confidence >= 75:
            color = "#FFD700"  # Gold
        elif confidence >= 60:
            color = "#FF9800"  # Orange
        else:
            color = "#F44336"  # Red

        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                background: #2d2d2d;
            }}
            QProgressBar::chunk {{
                background: {color};
            }}
        """)

    def _update_suggestions(self, suggestions: list):
        """Update suggestions display."""
        # Clear existing suggestions
        while self.suggestions_layout.count():
            child = self.suggestions_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not suggestions:
            no_suggestions = QLabel("✅ No issues found - design looks great!")
            no_suggestions.setStyleSheet("color: #4CAF50; padding: 10px;")
            self.suggestions_layout.addWidget(no_suggestions)
            return

        # Add suggestion cards
        for suggestion in suggestions:
            card = self._create_suggestion_card(suggestion)
            self.suggestions_layout.addWidget(card)

        # Add stretch at the end
        self.suggestions_layout.addStretch()

    def _create_suggestion_card(self, suggestion: dict) -> QFrame:
        """Create a suggestion card widget."""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)

        # Priority colors
        priority_colors = {
            'high': '#F44336',
            'medium': '#FF9800',
            'info': '#2196F3',
            'low': '#9E9E9E'
        }

        priority = suggestion.get('priority', 'info')
        color = priority_colors.get(priority, '#9E9E9E')

        card.setStyleSheet(f"""
            QFrame {{
                background: #2d2d2d;
                border-left: 4px solid {color};
                border-radius: 4px;
                padding: 8px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(5)

        # Title
        title_text = f"{suggestion.get('icon', '💡')} {suggestion.get('title', 'Suggestion')}"
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        # Message
        message = QLabel(suggestion.get('message', ''))
        message.setWordWrap(True)
        message.setStyleSheet("color: #ddd; font-size: 8pt;")
        layout.addWidget(message)

        # Action button if available
        action = suggestion.get('action')
        if action and not suggestion.get('auto_apply'):
            btn = QPushButton("Apply Suggestion")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background: {color}dd;
                }}
            """)
            btn.clicked.connect(
                lambda checked, a=action, d=suggestion.get('data', {}):
                self.apply_suggestion.emit(a, d)
            )
            layout.addWidget(btn)

        return card

    def request_refresh(self):
        """Request AI analysis refresh."""
        # Signal to parent to re-run AI analysis
        self.apply_suggestion.emit('refresh_analysis', {})
