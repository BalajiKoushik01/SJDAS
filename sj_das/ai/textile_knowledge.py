"""
Textile Knowledge Base - Domain expertise for silk sarees and textile design
Provides contextual information and traditional design rules
"""


# Pattern Knowledge
PATTERN_KNOWLEDGE = {
    "Border": {
        "description": "Decorative vertical edge design running along saree sides",
        "typical_width_cm": (5, 15),  # 2-6 inches
        "placement": ["Left edge", "Right edge", "Bottom edge"],
        "traditional_motifs": [
            "Peacock", "Elephant", "Mango (Paisley)", "Flower",
            "Geometric patterns", "Temple architecture", "Divine symbols"
        ],
        "cultural_significance": "Frames the saree, adds structural beauty",
        "tips": [
            "Border width should be 10-20% of saree width",
            "Contrast colors work best",
            "Gold/silver zari is traditional for festive wear",
            "Geometric borders suit daily wear, motifs for occasions"
        ]
    },
    "Pallu": {
        "description": "Ornate decorative end piece worn over shoulder",
        "typical_length_cm": (100, 150),  # 1-1.5 meters
        "placement": "End 1-1.5 meters of saree",
        "significance": "Most elaborate and visible part when worn",
        "traditional_styles": [
            "Brocade work", "Zari embroidery", "Peacock motifs",
            "Temple designs", "Floral patterns", "Royal insignia"
        ],
        "regional_variations": {
            "Kanchipuram": "Heavy silk with contrast pallu",
            "Banarasi": "Brocade with Mughal patterns",
            "Paithani": "Peacock and lotus motifs",
            "Chanderi": "Light, sheer pallu with zari border"
        },
        "tips": [
            "Pallu should be 20-30% of total saree length",
            "Maximum ornamentation goes here",
            "Consider draping style when designing",
            "Contrast pallu adds drama"
        ]
    },
    "Blouse": {
        "description": "Matching or contrasting blouse piece",
        "typical_length_cm": (80, 100),
        "design_considerations": [
            "Coordinates with saree colors",
            "Can match border or pallu",
            "Often includes same motifs in smaller scale"
        ],
        "tips": [
            "Provide 0.8-1 meter fabric",
            "Consider both matching and contrasting options",
            "Back designs are important for modern blouses"
        ]
    },
    "Broket": {
        "description": "Brocade work - rich fabric with raised patterns",
        "technique": "Extra weft weaving creates raised metallic patterns",
        "typical_patterns": [
            "Floral", "Leaf designs", "Geometric",
            "Animal motifs", "Religious symbols"
        ],
        "metal_threads": ["Gold zari", "Silver zari", "Copper"],
        "tips": [
            "Broket work is heavy - balance with lighter areas",
            "Traditional for bridal and festive sarees",
            "Requires higher hook count on loom (1000+)",
            "More expensive due to metallic thread"
        ]
    }
}

# Weave Knowledge
WEAVE_KNOWLEDGE = {
    "Jeri": {
        "full_name": "Jari/Zari work",
        "technique": "Extra weft insertion with metallic threads",
        "appearance": "Raised, shimmering metallic patterns",
        "typical_thread": "Gold, silver, or copper-wrapped threads",
        "usage": ["Bridal sarees", "Festive wear", "Temple sarees"],
        "famous_regions": [
            "Kanchipuram (Tamil Nadu)",
            "Banaras/Varanasi (Uttar Pradesh)",
            "Dharmavaram (Andhra Pradesh)"
        ],
        "loom_requirements": {
            "hooks": "800-2000+ (depending on complexity)",
            "skill_level": "Advanced",
            "production_time": "Slow (1-7 days per saree)"
        },
        "cost_factor": "High (3-10x basic weave)",
        "tips": [
            "Real zari uses gold/silver - test authenticity",
            "Density affects price and weight",
            "Modern alternatives: copper-zari, synthetic metallic"
        ]
    },
    "Ani": {
        "full_name": "Ananda/Plain weave with design",
        "technique": "Weft-faced compound weave",
        "appearance": "Smooth, interlocked patterns without raised surface",
        "characteristics": [
            "Lighter than jeri",
            "More durable for daily wear",
            "Comfortable draping"
        ],
        "usage": ["Everyday sarees", "Office wear", "Casual occasions"],
        "loom_requirements": {
            "hooks": "400-800",
            "skill_level": "Intermediate",
            "production_time": "Fast (1-3 days)"
        },
        "cost_factor": "Medium (1-3x basic weave)",
        "tips": [
            "Good for beginners to wear sarees",
            "Easy to maintain and wash",
            "Versatile for different occasions"
        ]
    },
    "Meena": {
        "full_name": "Meenakari work",
        "technique": "Intricate multi-colored enamel-like patterns",
        "appearance": "Colorful, jewel-like designs",
        "traditional_use": "Premium festive and bridal sarees",
        "loom_requirements": {
            "hooks": "1200+",
            "skill_level": "Expert",
            "production_time": "Very slow (7-30 days)"
        },
        "cost_factor": "Very High (10-50x basic)",
        "tips": [
            "Rajasthani specialty",
            "Extremely labor-intensive",
            "Often combined with jeri work"
        ]
    }
}

# Color Knowledge
COLOR_KNOWLEDGE = {
    "traditional_combinations": {
        "Bridal": {
            "popular": [
                ("Red", "Gold"), ("Maroon", "Green"), ("Pink", "Orange"),
                ("Purple", "Gold"), ("Green", "Red")
            ],
            "significance": "Auspicious colors for marriage"
        },
        "Festive": {
            "popular": [
                ("Royal Blue", "Gold"), ("Purple", "Silver"),
                ("Orange", "Pink"), ("Green", "Gold")
            ],
            "occasions": ["Diwali", "Temple visits", "Celebrations"]
        },
        "Casual": {
            "popular": [
                ("Pastels", "White"), ("Earth tones", "Brown"),
                ("Light blue", "White"), ("Peach", "Cream")
            ],
            "occasions": ["Daily wear", "Work", "Informal gatherings"]
        }
    },
    "cultural_significance": {
        "Red": "Prosperity, marriage, strength",
        "Green": "Fertility, new beginnings, nature",
        "Yellow": "Sanctity, knowledge, happiness",
        "White": "Peace, purity (mourning in some regions)",
        "Blue": "Calmness, vastness, Lord Krishna",
        "Orange": "Spirituality, sacrifice, courage",
        "Purple": "Royalty, luxury, dignity",
        "Black": "Power, elegance (modern; traditionally avoided)"
    },
    "contrast_rules": {
        "high_contrast": [
            "Red-Green", "Blue-Orange", "Yellow-Purple",
            "Black-White", "Gold-Dark colors"
        ],
        "medium_contrast": [
            "Red-Pink", "Blue-Green", "Purple-Pink"
        ],
        "low_contrast": [
            "Pastels together", "Analogous colors"
        ],
        "tips": [
            "Bridal: High contrast with gold",
            "Festive: High to medium contrast",
            "Casual: Medium to low contrast",
            "Modern: Low contrast monochrome is trending"
        ]
    }
}

# Loom Specifications
LOOM_SPECIFICATIONS = {
    "Jacquard": {
        "hook_ranges": {
            "basic": (400, 800, "Simple patterns, everyday sarees"),
            "standard": (800, 1200, "Most traditional designs"),
            "advanced": (1200, 2000, "Complex patterns, heavy work"),
            "premium": (2000, 5000, "Elaborate bridal, museum quality")
        },
        "dimensions": {
            "length_meters": (5.5, 6.5),
            "width_cm": (110, 122),  # 44-48 inches
            "notes": "Standard saree dimensions"
        },
        "thread_count": {
            "warp_typical": (80, 120, "threads per inch"),
            "weft_typical": (60, 100, "picks per inch"),
            "fine_quality": (120, 150, "threads per inch")
        }
    },
    "production_estimates": {
        "simple_saree": "1-2 days",
        "medium_complexity": "3-5 days",
        "heavy_work": "7-15 days",
        "bridal_premium": "15-45 days"
    }
}

# Design Guidelines
DESIGN_GUIDELINES = {
    "proportions": {
        "border_width": {
            "minimum": "2.5 cm (1 inch)",
            "typical": "5-10 cm (2-4 inches)",
            "heavy": "10-15 cm (4-6 inches)",
            "rule": "10-20% of total width"
        },
        "pallu_length": {
            "minimum": "80 cm",
            "typical": "100-120 cm",
            "elaborate": "120-150 cm",
            "rule": "20-30% of total length"
        },
        "body_design": {
            "sparse": "Small motifs spaced 10-20cm apart",
            "medium": "Regular patterns every 5-10cm",
            "dense": "All-over patterns",
            "rule": "Balance with border and pallu density"
        }
    },
    "quality_checks": {
        "contrast": "Border should contrast with body by 30%+ brightness",
        "symmetry": "Left and right borders must match exactly",
        "continuity": "Patterns should align when worn",
        "pallu_prominence": "Pallu should be 2-3x denser than body",
        "color_limit": "Traditional: 3-5 colors, Modern: unlimited but balanced"
    },
    "common_mistakes": [
        "Border too narrow (less than 5cm)",
        "Pallu too short (less than 1 meter)",
        "Insufficient contrast between sections",
        "Patterns too complex for loom capacity",
        "Color combinations culturally inappropriate"
    ]
}


def get_pattern_knowledge(pattern_type: str) -> dict:
    """Get knowledge about a pattern type."""
    return PATTERN_KNOWLEDGE.get(pattern_type, {})


def get_weave_knowledge(weave_type: str) -> dict:
    """Get knowledge about a weave type."""
    return WEAVE_KNOWLEDGE.get(weave_type, {})


def suggest_colors(occasion: str) -> list[tuple]:
    """Suggest color combinations for an occasion."""
    category = occasion.lower()
    if "bridal" in category or "wedding" in category:
        return COLOR_KNOWLEDGE["traditional_combinations"]["Bridal"]["popular"]
    elif "festival" in category or "celebration" in category:
        return COLOR_KNOWLEDGE["traditional_combinations"]["Festive"]["popular"]
    else:
        return COLOR_KNOWLEDGE["traditional_combinations"]["Casual"]["popular"]


def estimate_loom_requirements(complexity: str, has_zari: bool) -> dict:
    """Estimate loom requirements for a design."""
    hooks_needed = 400  # Base

    if complexity == "simple":
        hooks_needed = 600
    elif complexity == "medium":
        hooks_needed = 1000
    elif complexity == "complex":
        hooks_needed = 1500
    elif complexity == "elaborate":
        hooks_needed = 2500

    if has_zari:
        hooks_needed = int(hooks_needed * 1.3)  # Zari adds complexity

    return {
        "hooks_needed": hooks_needed,
        "skill_level": "Intermediate" if hooks_needed < 1000 else "Advanced",
        "estimated_time": LOOM_SPECIFICATIONS["production_estimates"].get(
            "medium_complexity" if hooks_needed < 1200 else "heavy_work"
        )
    }
