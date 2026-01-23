# MiniMax M2.1 Quick Reference

## Setup (One-Time)

```bash
python configure_minimax.py
```

Enter your API key from https://api.minimax.io

---

## Basic Usage

### Through AGI Assistant (Recommended)

```python
from sj_das.ai.agi_assistant import get_agi

agi = get_agi()

# Analyze design
agi.process_command("analyze this peacock pattern design")

# Color suggestions
agi.process_command("suggest colors for wedding saree")

# Pattern recommendations
agi.process_command("recommend pattern variations")

# Weave advice
agi.process_command("suggest weave structure for heavy silk")
```

### Direct Engine Access

```python
from sj_das.core.engines.llm.minimax_engine import get_minimax_engine

engine = get_minimax_engine()

# Design analysis
analysis = engine.analyze_design(
    "Peacock motif with gold zari",
    "Colors: Blue, Gold, Green"
)

# Color recommendations
colors = engine.get_color_recommendations(
    "Traditional Kanjivaram silk saree"
)

# Pattern suggestions
patterns = engine.get_pattern_suggestions(
    "Border with mango motifs",
    "South Indian traditional style"
)

# Weave explanation
info = engine.explain_weave_structure("Jacquard")
```

### Through Model Manager

```python
from sj_das.ai.model_manager import ModelManager

manager = ModelManager()
manager.load_minimax()

# Analyze with LLM
analysis = manager.analyze_design_with_llm(
    "Complex geometric pattern",
    "6 colors, high contrast"
)

# Get suggestions
suggestions = manager.get_design_suggestions(
    "Festive saree color palette",
    "color"  # or "pattern", "weave"
)
```

---

## Configuration Management

```python
from sj_das.core.ai_config import get_ai_config

config = get_ai_config()

# Set API key
config.set_api_key('minimax', 'your-key')

# Get API key
key = config.get_api_key('minimax')

# Check enabled providers
providers = config.get_enabled_providers()

# Enable/disable
config.enable_provider('minimax', True)
```

---

## Natural Language Commands

| Command | What It Does |
|---------|-------------|
| `"analyze this design"` | Detailed design analysis |
| `"suggest colors for..."` | Color palette recommendations |
| `"recommend patterns for..."` | Pattern variation suggestions |
| `"explain [weave type]"` | Weave structure explanation |
| `"suggest weave for..."` | Weave structure recommendations |

---

## Prompt Templates

```python
from sj_das.ai.prompt_templates import PromptTemplates

# Design analysis
prompt = PromptTemplates.format_design_analysis(
    "Peacock pattern",
    "Blue, Gold colors"
)

# Color recommendations
prompt = PromptTemplates.format_color_recommendations(
    "Wedding saree, traditional"
)

# Pattern suggestions
prompt = PromptTemplates.format_pattern_suggestions(
    "Border design",
    "South Indian style"
)
```

---

## Troubleshooting

### Not Configured
```python
# Check configuration
from sj_das.core.ai_config import get_ai_config
config = get_ai_config()
has_key = config.get_api_key('minimax') is not None
print(f"Configured: {has_key}")
```

### API Errors
- Check API key is valid
- Verify internet connection
- Check rate limits on MiniMax dashboard

### Import Errors
```bash
# Ensure all dependencies installed
pip install -r requirements.txt
```

---

## Files & Locations

| File | Purpose |
|------|---------|
| `configure_minimax.py` | Setup script |
| `examples/minimax_examples.py` | Usage examples |
| `docs/MINIMAX_INTEGRATION.md` | Full documentation |
| `tests/test_minimax_engine.py` | Unit tests |
| `~/.sj_das/config/ai_providers.json` | Config storage |

---

## Testing

```bash
# Run tests
pytest tests/test_minimax_engine.py -v

# Run examples
python examples/minimax_examples.py
```

---

## API Endpoints

- **International**: `https://api.minimax.io/v1/text/chatcompletion_v2`
- **China**: `https://api.minimaxi.com/v1/text/chatcompletion_v2`

---

## Cost Optimization

- Cache common queries
- Use appropriate `max_tokens`
- Batch similar requests
- Monitor usage on MiniMax dashboard

---

## Support

- Documentation: `docs/MINIMAX_INTEGRATION.md`
- Examples: `examples/minimax_examples.py`
- Tests: `tests/test_minimax_engine.py`
- Logs: `logs/sj_das.log`
