# SJ-DAS: Smart Jacquard Design Automation System

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt-6.10-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-orange.svg)](https://pytest.org/)

**Professional-grade desktop application for automating Jacquard loom design workflows with AI-powered pattern generation.**

## 🎯 Overview

SJ-DAS transforms traditional textile design workflows by combining computer vision, AI pattern generation, and loom-specific automation into a single, intuitive desktop application. Built with enterprise-level architecture patterns and comprehensive testing.

### Key Features

- **🎨 Advanced Pixel Editor**: Photoshop-quality editing with undo/redo, layers, and professional tools
- **🤖 AI Pattern Generation**: StyleGAN2-ADA powered design synthesis and variations
- **🧠 MiniMax M2.1 AI**: Intelligent design analysis, recommendations, and conversational assistance
- **🧵 Yarn & Weave Management**: Industry-standard color palettes and weave structure libraries
- **🏭 Loom Export**: Direct BMP export for Jacquard looms (Udayravi Creations compatible)
- **✂️ Auto-Segmentation**: Computer vision-based design region detection (body/border/pallu)
- **🔍 Smart Analysis**: Pattern complexity analysis and design validation
- **🎭 Real-time Preview**: Seamless texture preview and weave simulation

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Windows 10/11 (primary), macOS/Linux (experimental)
- 8GB RAM minimum, 16GB recommended
- NVIDIA GPU (optional, for AI features)

### Installation

```bash
# Clone repository
git clone https://github.com/BalajiKoushik01/SJDAS.git
cd SJDAS

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Install development tools (optional)
pip install -r requirements-dev.txt

# Launch application (CORRECT ENTRY POINT)
python launcher.py
```

> **Note**: Use `launcher.py` as the entry point, not `sj_das/main.py` (which is deprecated and archived).

## ✨ Recent Updates (2025-12-29)

### Bug Fixes & Improvements
- ✅ Fixed 9 critical bugs preventing application launch
- ✅ Added missing UI methods (rotate, flip, quantize, upscale)
- ✅ Fixed AI Pattern Generator widget initialization
- ✅ Removed duplicate code and improved organization
- ✅ Comprehensive integration testing (all tests passed)

See [`INTEGRATION_TEST_REPORT.md`](INTEGRATION_TEST_REPORT.md) for detailed verification results.

## 📁 Project Structure

```
sj_das_project/
├── sj_das/
│   ├── ai/                    # AI/ML modules (StyleGAN2, segmentation)
│   ├── core/                  # Core business logic
│   │   ├── exceptions.py      # Custom exception hierarchy
│   │   ├── loom_exporter.py   # BMP export engine
│   │   └── weave_manager.py   # Weave pattern management
│   ├── ui/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── menu_builder.py
│   │   │   ├── panel_factory.py
│   │   │   └── toolbar_factory.py
│   │   ├── features/          # Feature modules (AI, recolor, etc.)
│   │   ├── commands.py        # Command pattern (undo/redo)
│   │   ├── editor_widget.py   # Core pixel editor
│   │   └── infrastructure.py  # UI utilities (@safe_slot)
│   └── utils/
│       └── geometry_utils.py  # Math utilities (Bresenham, etc.)
├── tests/
│   ├── unit/                  # Unit tests (100% coverage on core)
│   └── integration/           # Integration tests
├── launcher.py                # Application entry point
├── pyproject.toml            # Tool configuration (pytest, ruff)
├── mypy.ini                  # Type checking configuration
└── requirements-dev.txt      # Development dependencies
```

## 🧪 Testing

```bash
# Run all tests with coverage
pytest tests/ -v --cov=sj_das --cov-report=html

# Run unit tests only
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_geometry_utils.py -v

# View coverage report
# Open htmlcov/index.html in browser
```

**Current Coverage**: 100% on `geometry_utils`, `commands`, and core utilities.

## 🛠️ Development

### Code Quality Tools

```bash
# Type checking
mypy sj_das/utils sj_das/core sj_das/ui/commands

# Linting
ruff check sj_das/

# Auto-fix linting issues
ruff check --fix sj_das/

# Format code
ruff format sj_das/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

Hooks automatically run:
- Trailing whitespace removal
- YAML/TOML validation
- Ruff linting and formatting
- mypy type checking
- pytest unit tests

## 📚 Architecture

### Design Patterns

- **Factory Pattern**: `PanelFactory`, `ToolbarFactory` for UI component creation
- **Command Pattern**: `MaskEditCommand` for undo/redo functionality
- **Decorator Pattern**: `@safe_slot` for crash-proof UI error handling
- **Observer Pattern**: PyQt signals/slots for event-driven architecture

### Exception Hierarchy

```python
SJDASException (base)
├── DesignImportError
├── AIProcessingError
├── LoomConfigError
├── ExportError
├── ValidationError
├── ResourceNotFoundError
└── WeaveGenerationError
```

All exceptions include contextual `details` dictionary for debugging.

## 🎨 UI Features

### Professional Tools
- Selection (Rectangle, Lasso, Magic Wand)
- Drawing (Brush, Eraser, Fill, Clone Stamp)
- Shapes (Rectangle, Ellipse, Line)
- Text overlay
- Color picker with yarn palette integration

### AI-Powered Features
- **Pattern Analysis**: Complexity scoring and structure detection
- **Auto-Segmentation**: CV-based region detection
- **Variation Generation**: StyleGAN2 synthesis
- **Smart Recolor**: Palette-based color transformation

## 🧠 MiniMax M2.1 AI Integration

SJ-DAS now includes **MiniMax M2.1**, an advanced large language model optimized for intelligent design assistance.

### AI Capabilities

#### 🎨 Intelligent Design Analysis
- Detailed pattern type identification (geometric, floral, traditional motifs)
- Color palette evaluation and harmony analysis
- Weave structure recommendations (Plain, Twill, Satin, Jacquard)
- Quality assessment and loom-readiness checks
- Cultural context identification

#### 💡 Context-Aware Recommendations
- Smart color palette suggestions based on design context
- Pattern variation recommendations with rationale
- Weave structure optimization for specific designs
- Traditional and cultural design insights
- Manufacturing feasibility analysis

#### 💬 Conversational AI Assistant
- Multi-turn conversations about design decisions
- Natural language understanding for design queries
- Expert textile design knowledge
- Integration with adaptive memory system

### Quick Start with MiniMax

```bash
# Configure your API key
python configure_minimax.py

# Run examples
python examples/minimax_examples.py
```

### Usage Examples

```python
from sj_das.ai.agi_assistant import get_agi

agi = get_agi()

# Analyze a design
response = agi.process_command("analyze this peacock pattern design")

# Get color recommendations
response = agi.process_command("suggest colors for a traditional wedding saree")

# Get pattern suggestions
response = agi.process_command("recommend pattern variations for border design")
```

For detailed documentation, see [MINIMAX_INTEGRATION.md](docs/MINIMAX_INTEGRATION.md).

## 🏭 Loom Integration

### Supported Formats
- **BMP Export**: Industry-standard Jacquard format
- **Hook Configuration**: 1000-4000 hooks supported
- **Color Depth**: 2-256 colors (loom-dependent)

### Weave Structures
- Plain weave
- Twill (2/2, 3/1, 3/3)
- Satin (4-harness, 8-harness)
- Custom patterns via weave library

## 📊 Performance

- **Startup Time**: < 3 seconds
- **Image Load**: < 1 second for 4K images
- **Undo/Redo**: O(1) with dirty-rect optimization
- **AI Inference**: ~2-5 seconds (GPU), ~10-20 seconds (CPU)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Install pre-commit hooks (`pre-commit install`)
4. Make changes with tests
5. Ensure all tests pass (`pytest tests/`)
6. Ensure type checking passes (`mypy sj_das/`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open Pull Request

### Code Standards
- **Type Hints**: Required for all public APIs
- **Docstrings**: Google-style for all classes/functions
- **Test Coverage**: Maintain >80% on new code
- **Line Length**: 120 characters (ruff enforced)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **QFluentWidgets**: Modern UI components
- **StyleGAN2-ADA**: AI pattern generation
- **PyQt6**: Application framework
- **OpenCV**: Computer vision operations

## 📧 Contact

- **Project Lead**: [Your Name]
- **Email**: [your.email@example.com]
- **Issues**: [GitHub Issues](https://github.com/yourusername/sj-das-project/issues)

---

**Built with ❤️ for the textile industry**
