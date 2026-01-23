"""
Design Prompt Parser - Convert natural language to design parameters
Extracts textile-specific information from text prompts
"""

import re
from dataclasses import dataclass


@dataclass
class DesignParameters:
    """Structured design parameters extracted from prompt."""
    design_type: str  # border, pallu, blouse, full_saree
    style: str | None = None  # kanchipuram, banarasi, paithani
    occasion: str | None = None  # bridal, festive, casual
    colors: list[str] = None
    motifs: list[str] = None
    weave: str | None = None  # jeri, ani, meena
    width_mm: int | None = None
    length_mm: int | None = None
    complexity: str = "medium"  # simple, medium, complex, elaborate

    def __post_init__(self):
        if self.colors is None:
            self.colors = []
        if self.motifs is None:
            self.motifs = []


class PromptParser:
    """Parse natural language prompts into design parameters."""

    def __init__(self):
        # Design type keywords
        self.design_types = {
            'border': ['border', 'edge', 'side'],
            'pallu': ['pallu', 'pallav', 'end piece'],
            'blouse': ['blouse', 'blouse piece'],
            'full_saree': ['full saree', 'complete saree', 'entire saree']
        }

        # Style keywords
        self.styles = {
            'kanchipuram': ['kanchipuram', 'kanchi', 'kancheepuram'],
            'banarasi': ['banarasi', 'banaras', 'varanasi', 'benarasi'],
            'paithani': ['paithani', 'paithan'],
            'chanderi': ['chanderi'],
            'mysore': ['mysore', 'mysuru'],
            'tussar': ['tussar', 'tassar']
        }

        # Occasion keywords
        self.occasions = {
            'bridal': ['bridal', 'wedding', 'marriage', 'bride'],
            'festive': ['festive', 'festival', 'celebration', 'diwali', 'puja'],
            'casual': ['casual', 'daily', 'everyday', 'office', 'regular'],
            'formal': ['formal', 'party', 'function']
        }

        # Color keywords
        self.colors = {
            'red': ['red', 'crimson', 'maroon', 'scarlet'],
            'gold': ['gold', 'golden', 'zari'],
            'green': ['green', 'emerald'],
            'blue': ['blue', 'navy', 'royal blue'],
            'purple': ['purple', 'violet'],
            'pink': ['pink', 'rose'],
            'orange': ['orange', 'saffron'],
            'yellow': ['yellow'],
            'white': ['white', 'ivory', 'cream'],
            'black': ['black'],
            'silver': ['silver']
        }

        # Motif keywords
        self.motifs = {
            'peacock': ['peacock', 'mayil'],
            'elephant': ['elephant', 'gaja', 'hathi'],
            'mango': ['mango', 'paisley', 'kairi'],
            'lotus': ['lotus', 'kamal'],
            'flower': ['flower', 'floral', 'bloom'],
            'geometric': ['geometric', 'square', 'triangle', 'diamond'],
            'temple': ['temple', 'gopuram', 'architecture'],
            'leaf': ['leaf', 'leaves'],
            'vine': ['vine', 'creeper'],
            'bird': ['bird'],
            'deer': ['deer'],
            'fish': ['fish']
        }

        # Weave keywords
        self.weaves = {
            'jeri': ['jeri', 'jari', 'zari', 'metallic'],
            'ani': ['ani', 'ananda', 'plain'],
            'meena': ['meena', 'meenakari'],
            'None': ['simple', 'basic']
        }

        # Complexity indicators
        self.complexity_keywords = {
            'simple': ['simple', 'basic', 'plain', 'minimal'],
            'medium': ['medium', 'moderate', 'standard', 'traditional'],
            'complex': ['complex', 'detailed', 'intricate'],
            'elaborate': ['elaborate', 'heavy', 'premium', 'rich', 'grand']
        }

        # Dimension patterns
        self.dimension_patterns = [
            r'(\d+)\s*(?:inches?|in|")',
            r'(\d+)\s*(?:cm|centimeters?)',
            r'(\d+)\s*(?:mm|millimeters?)',
            r'(\d+)\s*(?:meters?|m)'
        ]

    def parse(self, prompt: str) -> DesignParameters:
        """
        Parse a natural language prompt into structured parameters.

        Args:
            prompt: Text description like "Create a red and gold Kanchipuram bridal border"

        Returns:
            DesignParameters object with extracted information
        """
        prompt_lower = prompt.lower()

        # Extract each parameter
        design_type = self._extract_design_type(prompt_lower)
        style = self._extract_style(prompt_lower)
        occasion = self._extract_occasion(prompt_lower)
        colors = self._extract_colors(prompt_lower)
        motifs = self._extract_motifs(prompt_lower)
        weave = self._extract_weave(prompt_lower)
        dimensions = self._extract_dimensions(prompt, design_type)
        complexity = self._extract_complexity(prompt_lower, motifs, weave)

        return DesignParameters(
            design_type=design_type,
            style=style,
            occasion=occasion,
            colors=colors,
            motifs=motifs,
            weave=weave,
            width_mm=dimensions[0],
            length_mm=dimensions[1],
            complexity=complexity
        )

    def _extract_design_type(self, text: str) -> str:
        """Extract design type from text."""
        for dtype, keywords in self.design_types.items():
            if any(kw in text for kw in keywords):
                return dtype
        return 'border'  # Default

    def _extract_style(self, text: str) -> str | None:
        """Extract regional style."""
        for style, keywords in self.styles.items():
            if any(kw in text for kw in keywords):
                return style
        return None

    def _extract_occasion(self, text: str) -> str | None:
        """Extract occasion type."""
        for occasion, keywords in self.occasions.items():
            if any(kw in text for kw in keywords):
                return occasion
        return None

    def _extract_colors(self, text: str) -> list[str]:
        """Extract color list."""
        found = []
        for color, keywords in self.colors.items():
            if any(kw in text for kw in keywords) and color not in found:
                found.append(color)
        return found if found else ['red', 'gold']  # Default

    def _extract_motifs(self, text: str) -> list[str]:
        """Extract motif list."""
        found = []
        for motif, keywords in self.motifs.items():
            if any(kw in text for kw in keywords) and motif not in found:
                found.append(motif)
        return found

    def _extract_weave(self, text: str) -> str | None:
        """Extract weave type."""
        for weave, keywords in self.weaves.items():
            if any(kw in text for kw in keywords):
                return weave if weave != 'None' else None
        return None

    def _extract_dimensions(
            self, text: str, design_type: str) -> tuple[int | None, int | None]:
        """Extract width and length in millimeters."""
        width_mm = None
        length_mm = None

        # Try to find dimensions
        for pattern in self.dimension_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                value = float(matches[0])

                # Convert to mm
                if 'inch' in pattern or '"' in pattern:
                    value_mm = int(value * 25.4)
                elif 'cm' in pattern:
                    value_mm = int(value * 10)
                elif 'mm' in pattern:
                    value_mm = int(value)
                elif 'meter' in pattern or ' m' in pattern:
                    value_mm = int(value * 1000)
                else:
                    value_mm = int(value)

                # Assign based on context
                if 'width' in text.lower() or design_type == 'border':
                    width_mm = value_mm
                elif 'length' in text.lower() or design_type == 'pallu':
                    length_mm = value_mm
                else:
                    width_mm = value_mm  # Default to width

        # Apply defaults if not found
        if design_type == 'border' and width_mm is None:
            width_mm = 75  # Default 75mm (3 inches)
        elif design_type == 'pallu' and length_mm is None:
            length_mm = 1200  # Default 1.2 meters

        return (width_mm, length_mm)

    def _extract_complexity(
            self, text: str, motifs: list[str], weave: str | None) -> str:
        """Determine complexity level."""
        # Check explicit keywords
        for level, keywords in self.complexity_keywords.items():
            if any(kw in text for kw in keywords):
                return level

        # Infer from other parameters
        score = 0

        if weave in ['jeri', 'meena']:
            score += 2
        if len(motifs) > 2:
            score += 1
        if len(motifs) > 0:
            score += 1

        if score == 0:
            return 'simple'
        elif score <= 2:
            return 'medium'
        elif score == 3:
            return 'complex'
        else:
            return 'elaborate'

    def suggest_enhancements(self, params: DesignParameters) -> list[str]:
        """Suggest enhancements based on extracted parameters."""
        suggestions = []

        # Style-based suggestions
        if params.style == 'kanchipuram':
            if 'gold' not in params.colors:
                suggestions.append(
                    "Consider adding gold/zari for authentic Kanchipuram look")
            if not params.weave:
                suggestions.append(
                    "Kanchipuram traditionally uses Jeri (zari) weave")

        # Occasion-based
        if params.occasion == 'bridal':
            if params.complexity != 'elaborate':
                suggestions.append(
                    "Bridal designs are typically 'elaborate' complexity")
            if 'red' not in params.colors and 'maroon' not in params.colors:
                suggestions.append("Red is traditional for bridal sarees")

        # Motif suggestions
        if not params.motifs:
            if params.occasion == 'bridal':
                suggestions.append(
                    "Consider peacock or lotus motifs for bridal designs")
            elif params.occasion == 'casual':
                suggestions.append(
                    "Geometric patterns work well for casual wear")

        return suggestions


# Global instance
_parser_instance = None


def get_prompt_parser() -> PromptParser:
    """Get or create global parser instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = PromptParser()
    return _parser_instance


# Example usage
if __name__ == "__main__":
    parser = PromptParser()

    examples = [
        "Create a red and gold Kanchipuram bridal border with peacock motifs, 6 inches wide",
        "Design a simple geometric border for daily wear saree",
        "Traditional pallu for wedding, elaborate work with temple architecture motifs",
        "Casual blue and white border, 3 inches"
    ]

    for prompt in examples:
        print(f"\nPrompt: {prompt}")
        params = parser.parse(prompt)
        print(f"Type: {params.design_type}")
        print(f"Style: {params.style}")
        print(f"Occasion: {params.occasion}")
        print(f"Colors: {params.colors}")
        print(f"Motifs: {params.motifs}")
        print(f"Weave: {params.weave}")
        print(f"Dimensions: {params.width_mm}mm x {params.length_mm}mm")
        print(f"Complexity: {params.complexity}")
