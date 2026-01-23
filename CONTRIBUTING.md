# Contributing to SJ-DAS

Thank you for your interest in contributing to the Smart Jacquard Design Automation System!

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/sj-das-project.git
   cd sj-das-project
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## Code Standards

### Type Hints
All public APIs must include type hints:
```python
def process_image(image: QImage, max_colors: int = 16) -> np.ndarray:
    """Process image with type-safe parameters."""
    pass
```

### Docstrings
Use Google-style docstrings:
```python
def calculate_complexity(pattern: np.ndarray) -> float:
    """
    Calculate pattern complexity score.
    
    Args:
        pattern: Input pattern as numpy array
        
    Returns:
        Complexity score between 0.0 and 100.0
        
    Raises:
        ValidationError: If pattern dimensions are invalid
    """
    pass
```

### Testing
- Write tests for all new features
- Maintain >80% coverage on new code
- Use pytest fixtures for common setups

```python
def test_bresenham_horizontal():
    """Test horizontal line generation."""
    points = bresenham_line(0, 0, 5, 0)
    assert len(points) == 6
    assert points[0] == (0, 0)
```

## Pull Request Process

1. Create feature branch from `main`
2. Make changes with comprehensive tests
3. Run quality checks:
   ```bash
   pytest tests/ -v
   mypy sj_das/
   ruff check sj_das/
   ```
4. Update documentation if needed
5. Submit PR with clear description

## Questions?

Open an issue or contact the maintainers.
