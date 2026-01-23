"""
Proactive Textile AI Assistant - Natural, context-aware design intelligence
Automatically suggests improvements and provides expert guidance
"""

from .textile_knowledge import (COLOR_KNOWLEDGE, DESIGN_GUIDELINES,
                                get_pattern_knowledge, get_weave_knowledge)


class ProactiveTextileAssistant:
    """
    Proactive AI assistant that analyzes designs and provides natural,
    context-aware suggestions automatically.
    """

    def __init__(self):
        self.last_suggestions = []
        self.suggestion_history = []

    def analyze_design(self, ai_prediction: dict,
                       design_metrics: dict = None) -> list[dict]:
        """
        Analyze design and generate proactive suggestions.

        Args:
            ai_prediction: AI model prediction results
            design_metrics: Optional metrics about canvas (dimensions, colors, etc.)

        Returns:
            List of suggestions with priority, text, and actions
        """
        suggestions = []

        if not ai_prediction:
            return suggestions

        # Extract predictions
        pattern = ai_prediction.get('pattern', {})
        weave = ai_prediction.get('weave', {})
        segmentation = ai_prediction.get('segmentation', {})

        pattern_type = pattern.get('type', 'Unknown')
        pattern_confidence = pattern.get('confidence', 0)
        weave_type = weave.get('type', 'Unknown')
        weave.get('confidence', 0)
        # Call Classifier if model available
        try:
            from sj_das.core.unified_ai_engine import get_engine
            engine = get_engine()

            # If we have an image (not passed here currently, but assumed available in context)
            # The 'ai_prediction' dict might already have it, or we need to rethink the flow.
            # The View calls this method. Let's assume 'design_metrics' contains the image or path?
            # For now, we rely on what's passed in ai_prediction which comes
            # from the engine.

            # Actually, let's update how this is called in View.
            # For now, let's inject the classification results INTO
            # ai_prediction if missing
            if 'style' not in ai_prediction and 'image' in design_metrics:
                res = engine.classify_style(design_metrics['image'])
                pattern_type = res['style']
                pattern_confidence = res['confidence']
            else:
                # Standard flow
                pass

        except BaseException:
            pass

        seg_confidence = segmentation.get('confidence', 0)

        # 1. Segmentation Quality Check
        if seg_confidence < 85:
            suggestions.append({
                'priority': 'medium',
                'category': 'quality',
                'icon': '⚠️',
                'title': 'Segmentation Needs Attention',
                'message': f"AI is {seg_confidence:.1f}% confident about the segmentation. "
                f"Consider manually refining the body/border/pallu boundaries "
                f"for better results.",
                'action': 'review_segmentation',
                'auto_apply': False
            })
        elif seg_confidence > 95:
            suggestions.append({
                'priority': 'info',
                'category': 'quality',
                'icon': '✅',
                'title': 'Perfect Segmentation',
                'message': f"AI has {seg_confidence:.1f}% confidence - segmentation looks excellent!",
                'action': None,
                'auto_apply': False
            })

        # 2. Pattern-Specific Guidance
        if pattern_type != "Unknown":
            pattern_info = get_pattern_knowledge(pattern_type)

            if pattern_info:
                # Provide contextual tips
                tips = pattern_info.get('tips', [])
                if tips:
                    suggestions.append({
                        'priority': 'info',
                        'category': 'knowledge',
                        'icon': '💡',
                        'title': f'{pattern_type} Design Tips',
                        'message': tips[0],  # Show most relevant tip
                        'action': 'show_all_tips',
                        'auto_apply': False,
                        'data': {'all_tips': tips}
                    })

                # Check proportions if design_metrics available
                if design_metrics:
                    prop_suggestions = self._check_proportions(
                        pattern_type, design_metrics, pattern_info
                    )
                    suggestions.extend(prop_suggestions)

        # 3. Weave-Specific Recommendations
        if weave_type != "Unknown":
            weave_info = get_weave_knowledge(weave_type)

            if weave_info:
                # Suggest loom requirements
                loom_reqs = weave_info.get('loom_requirements', {})
                if loom_reqs:
                    hooks = loom_reqs.get('hooks', '')
                    time = loom_reqs.get('production_time', '')

                    suggestions.append({
                        'priority': 'high',
                        'category': 'production',
                        'icon': '🏭',
                        'title': f'{weave_type} Weave Requirements',
                        'message': f"This design uses {weave_type} weave. "
                        f"You'll need a loom with {hooks} hooks. "
                        f"Production time: {time}.",
                        'action': 'check_loom_compatibility',
                        'auto_apply': False,
                        'data': loom_reqs
                    })

                # Provide usage context
                usage = weave_info.get('usage', [])
                if usage:
                    occasions = ", ".join(usage)
                    suggestions.append({
                        'priority': 'info',
                        'category': 'context',
                        'icon': '🎭',
                        'title': f'{weave_type} Weave - Perfect For',
                        'message': f"This weave is traditionally used for: {occasions}",
                        'action': None,
                        'auto_apply': False
                    })

        # 4. Confidence-based suggestions
        if pattern_confidence < 75:
            # Show top alternatives
            all_probs = pattern.get('all_probabilities', {})
            sorted_probs = sorted(
                all_probs.items(),
                key=lambda x: x[1],
                reverse=True)
            top_3 = sorted_probs[:3]

            alternatives = ", ".join(
                [f"{name} ({prob:.1f}%)" for name, prob in top_3])

            suggestions.append({
                'priority': 'medium',
                'category': 'analysis',
                'icon': '🔍',
                'title': 'Uncertain Pattern Classification',
                'message': f"AI sees multiple pattern possibilities: {alternatives}. "
                f"The design might be a hybrid or custom style.",
                'action': 'show_alternatives',
                'auto_apply': False,
                'data': {'probabilities': all_probs}
            })

        # 5. Proactive Color Suggestions
        if pattern_type in ["Border", "Pallu"]:
            color_suggestions = self._suggest_colors(pattern_type, weave_type)
            if color_suggestions:
                suggestions.extend(color_suggestions)

        # 6. Quality Best Practices
        quality_checks = self._check_quality_guidelines(
            ai_prediction, design_metrics)
        suggestions.extend(quality_checks)

        # Store for history
        self.last_suggestions = suggestions
        self.suggestion_history.append({
            'pattern': pattern_type,
            'weave': weave_type,
            'suggestions_count': len(suggestions)
        })

        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'info': 2, 'low': 3}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return suggestions

    def _check_proportions(self, pattern_type: str,
                           metrics: dict, pattern_info: dict) -> list[dict]:
        """Check if design proportions follow traditional guidelines."""
        suggestions = []

        if pattern_type == "Border":
            typical_width = pattern_info.get('typical_width_cm', (5, 15))
            current_width = metrics.get('border_width_cm', 0)

            if current_width < typical_width[0]:
                suggestions.append({
                    'priority': 'medium',
                    'category': 'design',
                    'icon': '📏',
                    'title': 'Border Might Be Too Narrow',
                    'message': f"Current border is {current_width}cm. Traditional borders are {typical_width[0]}-{typical_width[1]}cm wide. "
                    f"Consider widening for better visual impact.",
                    'action': 'adjust_border_width',
                    'auto_apply': False,
                    'data': {'suggested_width': typical_width[0] + 2}
                })
            elif current_width > typical_width[1]:
                suggestions.append({
                    'priority': 'low',
                    'category': 'design',
                    'icon': '📏',
                    'title': 'Wide Border - Bold Choice',
                    'message': f"Your {current_width}cm border is wider than typical ({typical_width[1]}cm max). "
                    f"This creates a bold, modern look!",
                    'action': None,
                    'auto_apply': False
                })

        elif pattern_type == "Pallu":
            typical_length = pattern_info.get('typical_length_cm', (100, 150))
            current_length = metrics.get('pallu_length_cm', 0)

            if current_length < typical_length[0]:
                suggestions.append({
                    'priority': 'high',
                    'category': 'design',
                    'icon': '📐',
                    'title': 'Pallu Might Be Too Short',
                    'message': f"Current pallu is {current_length}cm. Traditional pallus are {typical_length[0]}-{typical_length[1]}cm. "
                    f"A shorter pallu may not drape well.",
                    'action': 'extend_pallu',
                    'auto_apply': False,
                    'data': {'suggested_length': typical_length[0]}
                })

        return suggestions

    def _suggest_colors(self, pattern_type: str,
                        weave_type: str) -> list[dict]:
        """Suggest color combinations based on pattern and weave."""
        suggestions = []

        # Determine occasion from weave type
        if weave_type == "Jeri":
            occasion = "Bridal"
        elif weave_type == "Meena":
            occasion = "Festive"
        else:
            occasion = "Casual"

        colors = COLOR_KNOWLEDGE['traditional_combinations'].get(
            occasion, {}).get('popular', [])

        if colors:
            color_list = ", ".join([f"{c1}-{c2}" for c1, c2 in colors[:3]])

            suggestions.append({
                'priority': 'info',
                'category': 'design',
                'icon': '🎨',
                'title': f'Traditional {occasion} Color Combinations',
                'message': f"Popular choices for {weave_type} weave: {color_list}. "
                f"These combinations are culturally significant and visually appealing.",
                'action': 'apply_color_scheme',
                'auto_apply': False,
                'data': {'colors': colors}
            })

        return suggestions

    def _check_quality_guidelines(
            self, ai_prediction: dict, design_metrics: dict = None) -> list[dict]:
        """Check design against quality guidelines."""
        suggestions = []

        # Check for common mistakes
        DESIGN_GUIDELINES['common_mistakes']

        # If we have metrics, do detailed checks
        if design_metrics:
            border_width = design_metrics.get('border_width_cm', 0)
            if border_width < 5 and border_width > 0:
                suggestions.append({
                    'priority': 'medium',
                    'category': 'quality',
                    'icon': '⚡',
                    'title': 'Common Issue Detected',
                    'message': "Border is narrower than 5cm - this is a common mistake. "
                    "Wider borders (5-10cm) enhance traditional aesthetics.",
                    'action': 'fix_border_width',
                    'auto_apply': False
                })

        return suggestions

    def get_contextual_help(self, current_tool: str,
                            current_pattern: str = None) -> str:
        """Get contextual help based on current user action."""
        help_texts = {
            'brush': "💡 **Brush Tip**: Use soft brushes for blending colors in pallu designs. "
            "Traditional silk sarees often use gradients.",

            'fill': "💡 **Fill Tip**: Ensure you're filling the correct segment. "
            "Body, border, and pallu should have distinct colors for proper segmentation.",

            'select': "💡 **Selection Tip**: Use selection to isolate patterns before applying effects. "
                     "This helps maintain clean boundaries.",

            'text': "💡 **Text Tip**: Add motif labels or pattern codes for documentation. "
            "Many designers mark traditional motifs (peacock, mango, lotus).",
        }

        return help_texts.get(current_tool, "")

    def generate_smart_summary(self, ai_prediction: dict) -> str:
        """Generate a natural language summary of the design."""
        if not ai_prediction:
            return "Upload a design to see AI analysis"

        pattern = ai_prediction.get('pattern', {})
        weave = ai_prediction.get('weave', {})
        seg = ai_prediction.get('segmentation', {})

        pattern_type = pattern.get('type', 'Unknown')
        pattern_conf = pattern.get('confidence', 0)
        weave_type = weave.get('type', 'Unknown')
        weave.get('confidence', 0)
        seg_conf = seg.get('confidence', 0)

        summary = f"This appears to be a **{pattern_type}** design "

        if pattern_conf > 90:
            summary += f"(highly confident - {pattern_conf:.0f}%) "
        elif pattern_conf > 75:
            summary += f"(confident - {pattern_conf:.0f}%) "
        else:
            summary += f"(uncertain - {pattern_conf:.0f}%) "

        summary += f"with **{weave_type}** weave technique. "

        if seg_conf > 95:
            summary += "Segmentation is excellent. "
        elif seg_conf > 85:
            summary += "Segmentation looks good. "
        else:
            summary += "Segmentation may need manual refinement. "

        # Add weave-specific context
        weave_info = get_weave_knowledge(weave_type)
        if weave_info:
            usage = weave_info.get('usage', [])
            if usage:
                summary += f"Perfect for {', '.join(usage)}."

        return summary

    def execute_action(self, action: str, data: dict = None):
        """
        Execute an action requested by the AI.
        In a real implementation, this might trigger events or callbacks.
        Values are typically handled by the View via signals, but this
        provides a specific entry point if called directly.
        """
        if data is None:
            data = {}
        # For now, we just log it as the actual execution happens in the View
        # via the 'on_ai_action' slot or signal connections.
        print(f"AI Assistant executing action: {action} with data: {data}")
        return True


# Global singleton
_assistant_instance = None


def get_proactive_assistant() -> ProactiveTextileAssistant:
    """Get or create global assistant instance."""
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = ProactiveTextileAssistant()
    return _assistant_instance
