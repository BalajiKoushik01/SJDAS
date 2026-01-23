"""
Textile-Specific Prompt Templates for AI Models.

Provides optimized prompts for design analysis, recommendations,
and generation tasks specific to textile and saree design.
"""

from typing import Dict, Optional


class PromptTemplates:
    """Collection of textile-specific prompt templates."""

    # Design Analysis Templates
    ANALYZE_DESIGN = """Analyze this textile design in detail:

Design Description: {design_description}
{image_analysis}

Provide a comprehensive analysis covering:
1. **Pattern Type**: Identify the pattern style (geometric, floral, traditional motif, etc.)
2. **Color Palette**: Describe the color scheme and harmony
3. **Weave Structure**: Recommend appropriate weave structure (Plain, Twill, Satin, Jacquard)
4. **Quality Assessment**: Evaluate design quality and manufacturability
5. **Cultural Context**: If applicable, identify traditional influences
6. **Recommendations**: Suggest improvements or variations

Be specific and technical in your analysis."""

    # Color Recommendation Templates
    RECOMMEND_COLORS = """Based on this design context:
{context}

Suggest an optimal color palette for this textile design.

Consider:
- **Traditional Combinations**: Classic Indian textile color pairings
- **Contrast and Harmony**: Balance between vibrant and subtle tones
- **Cultural Significance**: Colors appropriate for the occasion/style
- **Manufacturing Feasibility**: Colors achievable with standard dyes
- **Market Trends**: Current preferences in saree design

Provide:
1. Primary colors (3-5 colors with names and hex codes if possible)
2. Accent colors (2-3 complementary colors)
3. Rationale for each color choice
4. Example combinations for different design elements (border, pallu, body)"""

    # Pattern Suggestion Templates
    SUGGEST_PATTERNS = """Current Design: {current_design}
{preferences}

Suggest 3-5 pattern variations that would work well with this design.

For each variation, provide:
1. **Pattern Name**: Descriptive name for the variation
2. **Design Concept**: What makes this pattern unique
3. **Visual Description**: How it would look
4. **Weave Compatibility**: Which weave structures work best
5. **Target Audience**: Who would appreciate this design
6. **Manufacturing Notes**: Any special considerations

Focus on patterns that are:
- Aesthetically pleasing and balanced
- Manufacturable on Jacquard looms
- Culturally appropriate for traditional sarees
- Market-viable"""

    # Weave Structure Explanation
    EXPLAIN_WEAVE = """Explain the {weave_type} weave structure in detail for textile design.

Include:
1. **Construction**: How the weave is formed (warp and weft interlacing pattern)
2. **Characteristics**: Visual appearance, texture, drape, durability
3. **Typical Uses**: Common applications in saree design (body, border, pallu)
4. **Manufacturing Considerations**:
   - Loom requirements
   - Thread count recommendations
   - Complexity and cost factors
5. **Design Advantages**: When to choose this weave over others
6. **Traditional Examples**: Famous saree styles using this weave

Be technical but accessible, suitable for both designers and manufacturers."""

    # Quality Assessment
    ASSESS_QUALITY = """Assess the quality and loom-readiness of this textile design:

Design Details: {design_details}

Evaluate:
1. **Float Length**: Check for excessive floats that could snag
2. **Color Count**: Verify color count is within loom capacity (typically ≤8 colors)
3. **Pattern Repeat**: Assess repeat size and alignment
4. **Weave Density**: Check if warp/weft density is manufacturable
5. **Edge Integrity**: Verify selvage and border stability
6. **Hook Calculation**: Estimate hooks required (for Jacquard)
7. **Manufacturing Feasibility**: Overall assessment for production

Provide:
- **Quality Score**: 1-10 rating
- **Issues Found**: List any problems
- **Recommendations**: How to fix issues
- **Loom Readiness**: Yes/No with explanation"""

    # Text-to-Design Generation
    GENERATE_DESIGN_PROMPT = """Create a detailed prompt for generating a textile design based on:

User Request: {user_request}
Style Preferences: {style_preferences}

Generate a comprehensive prompt that includes:
1. **Pattern Description**: Detailed visual description
2. **Color Scheme**: Specific colors and their arrangement
3. **Style Keywords**: Traditional motifs, weave type, texture
4. **Quality Modifiers**: "seamless", "high resolution", "intricate", etc.
5. **Negative Prompts**: What to avoid (blur, distortion, etc.)

Format the output as a ready-to-use prompt for image generation models."""

    # Conversational Templates
    CHAT_RESPONSE = """You are an expert textile designer assistant. Respond to this query:

User: {user_query}
Context: {context}

Provide a helpful, informative response that:
- Demonstrates expertise in textile design
- Uses appropriate technical terminology
- Offers practical, actionable advice
- Considers traditional Indian textile practices
- Is friendly and encouraging

Keep the response concise but comprehensive."""

    @staticmethod
    def format_design_analysis(design_description: str,
                               image_analysis: Optional[str] = None) -> str:
        """Format a design analysis prompt."""
        image_section = f"\nImage Analysis Data:\n{image_analysis}" if image_analysis else ""
        return PromptTemplates.ANALYZE_DESIGN.format(
            design_description=design_description,
            image_analysis=image_section
        )

    @staticmethod
    def format_color_recommendations(context: str) -> str:
        """Format a color recommendation prompt."""
        return PromptTemplates.RECOMMEND_COLORS.format(context=context)

    @staticmethod
    def format_pattern_suggestions(
            current_design: str, preferences: Optional[str] = None) -> str:
        """Format a pattern suggestion prompt."""
        pref_section = f"\nUser Preferences: {preferences}" if preferences else ""
        return PromptTemplates.SUGGEST_PATTERNS.format(
            current_design=current_design,
            preferences=pref_section
        )

    @staticmethod
    def format_weave_explanation(weave_type: str) -> str:
        """Format a weave explanation prompt."""
        return PromptTemplates.EXPLAIN_WEAVE.format(weave_type=weave_type)

    @staticmethod
    def format_quality_assessment(design_details: str) -> str:
        """Format a quality assessment prompt."""
        return PromptTemplates.ASSESS_QUALITY.format(
            design_details=design_details)

    @staticmethod
    def format_generation_prompt(
            user_request: str, style_preferences: Optional[str] = None) -> str:
        """Format a text-to-design generation prompt."""
        prefs = style_preferences or "Traditional Indian saree design"
        return PromptTemplates.GENERATE_DESIGN_PROMPT.format(
            user_request=user_request,
            style_preferences=prefs
        )

    @staticmethod
    def format_chat_response(user_query: str,
                             context: Optional[str] = None) -> str:
        """Format a conversational response prompt."""
        ctx = context or "General textile design assistance"
        return PromptTemplates.CHAT_RESPONSE.format(
            user_query=user_query,
            context=ctx
        )


# Textile-specific keywords and terminology
TEXTILE_KEYWORDS = {
    "patterns": [
        "butta", "motif", "paisley", "mango", "peacock", "floral",
        "geometric", "checks", "stripes", "border", "pallu", "body"
    ],
    "weaves": [
        "plain", "twill", "satin", "jacquard", "dobby", "brocade",
        "kanjivaram", "banarasi", "patola", "ikat"
    ],
    "colors": [
        "zari", "gold", "silver", "maroon", "emerald", "ruby",
        "sapphire", "peacock blue", "temple red", "turmeric yellow"
    ],
    "quality": [
        "float", "hooks", "acchu", "kali", "selvage", "warp", "weft",
        "thread count", "density", "repeat"
    ]
}


def get_textile_context_prompt() -> str:
    """Get a context-setting prompt for textile design AI."""
    return """You are an expert in traditional Indian textile design, particularly:
- Kanjivaram silk sarees
- Jacquard weaving techniques
- Traditional motifs and patterns
- Color theory for textiles
- Loom specifications and manufacturing

Always provide specific, technical, and culturally informed advice."""
