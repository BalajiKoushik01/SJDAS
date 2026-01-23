"""
Adaptive Memory Module ("The Brain")
Tracks user preferences and learns from design patterns over time.
"""

import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("SJ_DAS.AdaptiveMemory")


class AdaptiveMemory:
    """
    Persistent memory that learns from user behavior.
    """

    def __init__(self, user_id="default"):
        self.user_id = user_id
        self.brain_path = Path(f"user_data/brain_{user_id}.json")
        self.brain_path.parent.mkdir(exist_ok=True, parents=True)

        self.memory = {
            "stats": {
                "designs_created": 0,
                "ai_generations": 0,
                "last_active": None
            },
            "preferences": {
                "fav_colors": {},      # "Red": 5
                "fav_weaves": {},      # "Kanchipuram": 3
                "fav_patterns": {}     # "Paisley": 8
            },
            "recent_actions": []       # Last 50 actions for context
        }

        self.load_memory()

    def load_memory(self):
        if self.brain_path.exists():
            try:
                with open(self.brain_path, 'r') as f:
                    self.memory = json.load(f)
                logger.info("Brain loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load brain: {e}")

    def save_memory(self):
        try:
            self.memory["stats"]["last_active"] = datetime.now().isoformat()
            with open(self.brain_path, 'w') as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save brain: {e}")

    def learn_from_design(self, pattern_type: str,
                          weave_type: str, primary_colors: list):
        """
        Ingest a completed design to update weights.
        """
        # Update Stats
        self.memory["stats"]["designs_created"] += 1

        # Update Weights
        prefs = self.memory["preferences"]

        # Weave Weight
        current_w = prefs["fav_weaves"].get(weave_type, 0)
        prefs["fav_weaves"][weave_type] = current_w + 1

        # Pattern Weight
        current_p = prefs["fav_patterns"].get(pattern_type, 0)
        prefs["fav_patterns"][pattern_type] = current_p + 1

        # Color Weights
        for color in primary_colors:
            current_c = prefs["fav_colors"].get(color, 0)
            prefs["fav_colors"][color] = current_c + 1

        self.save_memory()
        logger.info(f"Learned from design: {weave_type} / {pattern_type}")

    def log_action(self, action_name: str, details: str = ""):
        """Log a user action for short-term context."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_name,
            "details": details
        }

        self.memory["recent_actions"].append(entry)
        # Keep last 50
        if len(self.memory["recent_actions"]) > 50:
            self.memory["recent_actions"].pop(0)

        if action_name == "ai_generation":
            self.memory["stats"]["ai_generations"] += 1

        self.save_memory()

    def get_top_preference(self, category: str) -> str:
        """Get the highest weighted item in a category."""
        target = self.memory["preferences"].get(f"fav_{category}", {})
        if not target:
            return None
        return max(target, key=target.get)

    def get_context_summary(self) -> str:
        """Get a text summary of what the AI knows about the user."""
        fav_weave = self.get_top_preference("weaves") or "Unknown"
        fav_color = self.get_top_preference("colors") or "Unknown"
        count = self.memory["stats"]["designs_created"]

        return f"User has created {count} designs. Prefers {fav_weave} weave and {fav_color} tones."


# Global instance
_brain_instance = None


def get_adaptive_memory():
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = AdaptiveMemory()
    return _brain_instance
