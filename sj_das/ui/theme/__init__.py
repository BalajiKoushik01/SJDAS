from .futuristic_theme import FuturisticTheme
from .premium_theme import PremiumTheme, apply_premium_theme

# Alias for backward compatibility (using the new default)
ThemeManager = FuturisticTheme

__all__ = ['PremiumTheme', 'ThemeManager', 'apply_premium_theme']
