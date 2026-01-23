"""
Example script demonstrating MiniMax M2.1 integration in SJ-DAS.

This script shows how to use the MiniMax AI for textile design analysis
and recommendations.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def example_agi_assistant():
    """Example: Using MiniMax through the AGI Assistant."""
    print("\n" + "=" * 60)
    print("Example 1: Using MiniMax through AGI Assistant")
    print("=" * 60 + "\n")

    from sj_das.ai.agi_assistant import get_agi

    agi = get_agi()

    # Example 1: Analyze a design
    print("Query: 'Analyze this peacock pattern design with gold zari work'")
    response = agi.process_command(
        "analyze this peacock pattern design with gold zari work")
    print(f"\nResponse Type: {response['type']}")
    print(f"Response: {response['response'][:200]}...")

    # Example 2: Get color recommendations
    print("\n" + "-" * 60 + "\n")
    print("Query: 'Suggest colors for a traditional wedding saree'")
    response = agi.process_command(
        "suggest colors for a traditional wedding saree")
    print(f"\nResponse Type: {response['type']}")
    print(f"Response: {response['response'][:200]}...")

    # Example 3: Pattern suggestions
    print("\n" + "-" * 60 + "\n")
    print("Query: 'Recommend pattern variations for border design'")
    response = agi.process_command(
        "recommend pattern variations for border design")
    print(f"\nResponse Type: {response['type']}")
    print(f"Response: {response['response'][:200]}...")


def example_direct_engine():
    """Example: Using MiniMax engine directly."""
    print("\n" + "=" * 60)
    print("Example 2: Using MiniMax Engine Directly")
    print("=" * 60 + "\n")

    from sj_das.core.engines.llm.minimax_engine import get_minimax_engine

    engine = get_minimax_engine()

    if not engine.is_configured():
        print("⚠️  MiniMax is not configured with an API key.")
        print("Run 'python configure_minimax.py' to set up your API key.")
        return

    # Example 1: Analyze a design
    print("Analyzing a design...")
    analysis = engine.analyze_design(
        design_description="Peacock motif with gold zari work on royal blue silk",
        image_analysis="Colors: Royal Blue, Gold, Emerald Green. Pattern: Floral with peacock"
    )

    if analysis:
        print(f"\nAnalysis:\n{analysis[:300]}...")
    else:
        print("Analysis not available (API key may not be configured)")

    # Example 2: Color recommendations
    print("\n" + "-" * 60 + "\n")
    print("Getting color recommendations...")
    colors = engine.get_color_recommendations(
        "Traditional Kanjivaram silk saree for wedding ceremony"
    )

    if colors:
        print(f"\nColor Recommendations:\n{colors[:300]}...")
    else:
        print("Recommendations not available (API key may not be configured)")

    # Example 3: Pattern suggestions
    print("\n" + "-" * 60 + "\n")
    print("Getting pattern suggestions...")
    patterns = engine.get_pattern_suggestions(
        current_design="Border with mango motifs",
        preferences="Traditional South Indian style"
    )

    if patterns:
        print(f"\nPattern Suggestions:\n{patterns[:300]}...")
    else:
        print("Suggestions not available (API key may not be configured)")


def example_model_manager():
    """Example: Using MiniMax through Model Manager."""
    print("\n" + "=" * 60)
    print("Example 3: Using MiniMax through Model Manager")
    print("=" * 60 + "\n")

    from sj_das.ai.model_manager import ModelManager

    manager = ModelManager()

    # Load MiniMax
    print("Loading MiniMax M2.1...")
    success = manager.load_minimax()

    if not success:
        print("⚠️  MiniMax could not be loaded (API key may not be configured)")
        print("Run 'python configure_minimax.py' to set up your API key.")
        return

    print("✓ MiniMax loaded successfully!\n")

    # Example 1: Design analysis
    print("Analyzing design with LLM...")
    analysis = manager.analyze_design_with_llm(
        design_description="Complex geometric pattern with 6 colors",
        image_analysis="High contrast, intricate details, traditional motifs"
    )

    if analysis:
        print(f"\nAnalysis:\n{analysis[:300]}...")
    else:
        print("Analysis not available")

    # Example 2: Get color suggestions
    print("\n" + "-" * 60 + "\n")
    print("Getting color suggestions...")
    suggestions = manager.get_design_suggestions(
        context="Need color palette for festive saree with traditional appeal",
        suggestion_type="color"
    )

    if suggestions:
        print(f"\nColor Suggestions:\n{suggestions[:300]}...")
    else:
        print("Suggestions not available")

    # Example 3: Get pattern suggestions
    print("\n" + "-" * 60 + "\n")
    print("Getting pattern suggestions...")
    suggestions = manager.get_design_suggestions(
        context="Border design for Kanjivaram silk saree",
        suggestion_type="pattern"
    )

    if suggestions:
        print(f"\nPattern Suggestions:\n{suggestions[:300]}...")
    else:
        print("Suggestions not available")


def example_configuration():
    """Example: Checking and managing configuration."""
    print("\n" + "=" * 60)
    print("Example 4: Configuration Management")
    print("=" * 60 + "\n")

    from sj_das.core.ai_config import get_ai_config

    config = get_ai_config()

    # Check if MiniMax is configured
    has_key = config.get_api_key('minimax') is not None
    print(f"MiniMax configured: {has_key}")

    # Get enabled providers
    providers = config.get_enabled_providers()
    print(f"Enabled AI providers: {providers}")

    # Get provider configuration
    minimax_config = config.get_provider_config('minimax')
    if minimax_config:
        print(f"\nMiniMax Configuration:")
        print(f"  Name: {minimax_config.name}")
        print(f"  Endpoint: {minimax_config.endpoint}")
        print(f"  Enabled: {minimax_config.enabled}")
        print(f"  Priority: {minimax_config.priority}")
        print(f"  Has API Key: {bool(minimax_config.api_key)}")

    print(f"\nConfiguration file: {config.config_file}")


def main():
    """Run all examples."""
    print("\n" + "#" * 60)
    print("# MiniMax M2.1 Integration Examples for SJ-DAS")
    print("#" * 60)

    try:
        # Example 1: AGI Assistant
        example_agi_assistant()

        # Example 2: Direct Engine
        example_direct_engine()

        # Example 3: Model Manager
        example_model_manager()

        # Example 4: Configuration
        example_configuration()

        print("\n" + "#" * 60)
        print("# Examples completed!")
        print("#" * 60 + "\n")

        print("💡 Tips:")
        print("  • Configure your API key: python configure_minimax.py")
        print("  • Read documentation: docs/MINIMAX_INTEGRATION.md")
        print("  • Run tests: pytest tests/test_minimax_engine.py -v")
        print()

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\nMake sure you have:")
        print("  1. Configured your MiniMax API key")
        print("  2. Installed all dependencies")
        print("  3. Run from the project root directory")


if __name__ == "__main__":
    main()
