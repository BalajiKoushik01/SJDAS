# MiniMax M2.1 Integration for SJ-DAS

## Overview

MiniMax M2.1 is now integrated into SJ-DAS to provide intelligent design analysis, recommendations, and conversational assistance for textile design.

## Features

### 🎨 Intelligent Design Analysis
- Detailed analysis of textile patterns
- Color palette evaluation
- Weave structure recommendations
- Quality assessment and loom-readiness checks

### 💡 Context-Aware Recommendations
- Smart color palette suggestions based on design context
- Pattern variation recommendations
- Weave structure optimization
- Cultural and traditional design insights

### 💬 Conversational AI Assistant
- Multi-turn conversations about design decisions
- Natural language understanding for design queries
- Expert textile design knowledge
- Integration with existing AGI assistant

## Setup

### 1. Get Your API Key

1. Visit the MiniMax Open Platform: https://api.minimax.io
2. Register or log in to your account
3. Navigate to Settings
4. Create a new API key
5. Copy the API key (keep it secure!)

### 2. Configure the API Key

#### Option A: Using the Configuration Script (Recommended)

```bash
python configure_minimax.py
```

Follow the prompts to enter your API key.

#### Option B: Manual Configuration

```python
from sj_das.core.ai_config import get_ai_config

config = get_ai_config()
config.set_api_key('minimax', 'your-api-key-here')
```

#### Option C: Environment Variable

Set the `MINIMAX_API_KEY` environment variable:

```bash
# Windows
set MINIMAX_API_KEY=your-api-key-here

# Linux/Mac
export MINIMAX_API_KEY=your-api-key-here
```

### 3. Verify Installation

Run the test suite to verify everything is working:

```bash
pytest tests/test_minimax_engine.py -v
```

## Usage

### In the AGI Assistant

The MiniMax integration is automatically available through the AGI assistant. Try these commands:

```python
from sj_das.ai.agi_assistant import get_agi

agi = get_agi()

# Analyze a design
response = agi.process_command("analyze this peacock pattern design")

# Get color recommendations
response = agi.process_command("suggest colors for a traditional silk saree")

# Get pattern suggestions
response = agi.process_command("recommend pattern variations for border design")

# Ask for weave advice
response = agi.process_command("suggest weave structure for heavy silk")
```

### Direct API Usage

For more control, use the MiniMax engine directly:

```python
from sj_das.core.engines.llm.minimax_engine import get_minimax_engine

# Get the engine
engine = get_minimax_engine()

# Configure if needed (usually done automatically)
engine.configure('your-api-key')

# Analyze a design
analysis = engine.analyze_design(
    design_description="Peacock motif with gold zari work",
    image_analysis="Colors: Blue, Gold, Green. Pattern: Floral"
)

# Get color recommendations
colors = engine.get_color_recommendations(
    "Traditional Kanjivaram silk saree for wedding"
)

# Get pattern suggestions
patterns = engine.get_pattern_suggestions(
    current_design="Border with mango motifs",
    preferences="Traditional South Indian style"
)

# Explain a weave structure
explanation = engine.explain_weave_structure("Jacquard")

# Custom queries
response = engine.generate(
    "What are the best color combinations for a temple saree?"
)
```

### In the Model Manager

```python
from sj_das.ai.model_manager import ModelManager

manager = ModelManager()

# Load MiniMax (with optional API key)
manager.load_minimax(api_key='your-key')  # or uses stored key

# Analyze design
analysis = manager.analyze_design_with_llm(
    design_description="Complex geometric pattern",
    image_analysis="High contrast, 6 colors"
)

# Get suggestions
suggestions = manager.get_design_suggestions(
    context="Need color palette for festive saree",
    suggestion_type="color"  # or "pattern", "weave"
)
```

## API Key Management

### Viewing Configuration

```python
from sj_das.core.ai_config import get_ai_config

config = get_ai_config()

# Check if MiniMax is configured
has_key = config.get_api_key('minimax') is not None

# Get enabled providers
providers = config.get_enabled_providers()
print(f"Enabled AI providers: {providers}")
```

### Updating API Key

```python
from sj_das.core.ai_config import get_ai_config

config = get_ai_config()
config.set_api_key('minimax', 'new-api-key')
```

### Configuration File Location

API keys are stored securely in:
```
~/.sj_das/config/ai_providers.json
```

## Prompt Templates

The integration includes specialized prompt templates for textile design. You can use them directly:

```python
from sj_das.ai.prompt_templates import PromptTemplates

# Format a design analysis prompt
prompt = PromptTemplates.format_design_analysis(
    design_description="Peacock pattern with gold work",
    image_analysis="Colors: Blue, Gold. Style: Traditional"
)

# Format color recommendations
prompt = PromptTemplates.format_color_recommendations(
    context="Wedding saree, traditional style"
)

# Format pattern suggestions
prompt = PromptTemplates.format_pattern_suggestions(
    current_design="Border with floral motifs",
    preferences="South Indian traditional"
)
```

## Troubleshooting

### "MiniMax not configured" Warning

**Problem**: The engine is not configured with an API key.

**Solution**: Run `python configure_minimax.py` or set the API key manually.

### API Authentication Failed

**Problem**: Invalid or expired API key.

**Solution**: 
1. Check your API key is correct
2. Verify the key is active on the MiniMax platform
3. Update the key using `config.set_api_key('minimax', 'new-key')`

### Rate Limit Exceeded

**Problem**: Too many API requests in a short time.

**Solution**: 
- The engine will automatically handle rate limits
- Consider upgrading your MiniMax plan for higher limits
- Implement caching for repeated queries

### Network Errors

**Problem**: Cannot connect to MiniMax API.

**Solution**:
- Check your internet connection
- Verify firewall settings
- Check if the API endpoint is accessible

## Cost Optimization

- **Cache Common Queries**: The engine automatically maintains conversation context
- **Use Appropriate Token Limits**: Adjust `max_tokens` based on your needs
- **Batch Similar Requests**: Group related queries in a single conversation
- **Monitor Usage**: Check your MiniMax dashboard for usage statistics

## Advanced Configuration

### Custom Endpoints

For users in China or using custom endpoints:

```python
from sj_das.core.engines.llm.minimax_engine import MiniMaxEngine, MiniMaxConfig

config = MiniMaxConfig(
    api_key='your-key',
    endpoint='https://api.minimaxi.com/v1/text/chatcompletion_v2',  # China endpoint
    temperature=0.7,
    max_tokens=2048
)

engine = MiniMaxEngine(config)
```

### Custom Temperature and Tokens

```python
from sj_das.core.ai_config import get_ai_config

config = get_ai_config()
provider_config = config.get_provider_config('minimax')

# Modify settings (requires manual update to config file)
# Or pass directly to engine methods
```

## Integration with Existing Features

MiniMax M2.1 works seamlessly with:
- ✅ StyleGAN textile generation
- ✅ Google Gemini integration
- ✅ HuggingFace models
- ✅ Pollinations.ai fallback
- ✅ AGI Assistant
- ✅ Adaptive Memory system
- ✅ Proactive Assistant

## Support

For issues or questions:
1. Check the logs in `logs/sj_das.log`
2. Review the implementation plan: `implementation_plan.md`
3. Run tests: `pytest tests/test_minimax_engine.py -v`
4. Check MiniMax documentation: https://api.minimax.io/docs

## License

This integration is part of the SJ-DAS project and follows the same license terms.
