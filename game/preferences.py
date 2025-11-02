"""
Doda's preferences system - what Doda loves, likes, dislikes, and hates
"""

from typing import Dict, List, Optional
import json
from pathlib import Path


class PreferencesSystem:
    """Manages Doda's preferences and calculates affinity scores"""

    # Default preferences for Doda the Dodo bird
    DEFAULT_PREFERENCES = {
        "loves": [
            {"keyword": "dodo bird", "score": 10, "reason": "My own kind! Another dodo!"},
            {"keyword": "large beak", "score": 10, "reason": "What a magnificent beak!"},
            {"keyword": "colorful beak", "score": 9, "reason": "Such a beautiful colorful beak!"},
            {"keyword": "egg", "score": 9, "reason": "Precious egg! Must protect!"},
            {"keyword": "nest", "score": 8, "reason": "Perfect for resting!"}
        ],
        "likes": [
            {"keyword": "feather", "score": 7, "reason": "Soft and lovely"},
            {"keyword": "plant", "score": 6, "reason": "Nice greenery"},
            {"keyword": "food", "score": 6, "reason": "Something to eat!"},
            {"keyword": "toy", "score": 5, "reason": "Fun to play with"},
            {"keyword": "round", "score": 4, "reason": "Pleasing shape"}
        ],
        "dislikes": [
            {"keyword": "sharp", "score": -4, "reason": "Looks dangerous"},
            {"keyword": "loud", "score": -4, "reason": "Too noisy for me"},
            {"keyword": "metal", "score": -3, "reason": "Cold and hard"},
            {"keyword": "dirty", "score": -3, "reason": "Not clean"}
        ],
        "hates": [
            {"keyword": "predator", "score": -10, "reason": "Danger! Must flee!"},
            {"keyword": "snake", "score": -9, "reason": "Natural enemy!"},
            {"keyword": "fire", "score": -8, "reason": "Terrifying!"},
            {"keyword": "cage", "score": -8, "reason": "No freedom!"}
        ]
    }

    def __init__(self, preferences_path: str = "game/doda_preferences.json"):
        self.preferences_path = Path(preferences_path)
        self.preferences = self.DEFAULT_PREFERENCES.copy()

        # Load custom preferences if available
        self.load()

    def calculate_affinity(self, object_description: str, object_type: str = "physical_object",
                          special_features: Optional[dict] = None) -> tuple[int, str]:
        """
        Calculate affinity score for an object

        Args:
            object_description: Text description of the object
            object_type: Type of object (physical_object or dodo_bird)
            special_features: Dict with is_dodo_bird, beak_size, beak_color

        Returns:
            Tuple of (score, reason) where score is -10 to +10
        """
        # Special handling for dodo birds
        if object_type == "dodo_bird" or (special_features and special_features.get("is_dodo_bird")):
            return self._calculate_dodo_bird_affinity(special_features or {})

        # Check description against all preference keywords
        description_lower = object_description.lower()
        matches = []

        # Check all categories
        for category in ["loves", "likes", "dislikes", "hates"]:
            for pref in self.preferences[category]:
                keyword = pref["keyword"].lower()
                if keyword in description_lower:
                    matches.append(pref)

        # If no matches, neutral response
        if not matches:
            return (0, "Hmm, I'm not sure how I feel about this...")

        # Use the strongest match (highest absolute score)
        strongest_match = max(matches, key=lambda x: abs(x["score"]))
        return (strongest_match["score"], strongest_match["reason"])

    def _calculate_dodo_bird_affinity(self, special_features: dict) -> tuple[int, str]:
        """
        Calculate affinity for dodo bird gifts
        Beak size and color are important!

        Args:
            special_features: Dict with beak_size, beak_color

        Returns:
            Tuple of (score, reason)
        """
        beak_size = special_features.get("beak_size", "").lower()
        beak_color = special_features.get("beak_color", "").lower()

        base_score = 10  # Always loves dodo birds
        reason_parts = ["My own kind! Another dodo!"]

        # Beak size bonus
        if beak_size == "large":
            base_score += 2  # Can exceed 10 for exceptional gifts!
            reason_parts.append("And what a MAGNIFICENT beak!")
        elif beak_size == "medium":
            base_score += 1
            reason_parts.append("Nice beak size!")
        elif beak_size == "small":
            base_score += 0
            reason_parts.append("Cute little beak!")

        # Beak color bonus
        if any(color in beak_color for color in ["colorful", "bright", "vibrant", "rainbow"]):
            base_score += 2
            reason_parts.append("Such beautiful colors!")
        elif any(color in beak_color for color in ["orange", "yellow", "red"]):
            base_score += 1
            reason_parts.append("Pretty beak color!")

        # Cap at reasonable maximum
        final_score = min(base_score, 15)
        final_reason = " ".join(reason_parts)

        return (final_score, final_reason)

    def get_all_preferences(self) -> dict:
        """Get all preferences"""
        return self.preferences.copy()

    def get_category(self, category: str) -> List[dict]:
        """Get preferences for a specific category"""
        return self.preferences.get(category, [])

    def add_preference(self, category: str, keyword: str, score: int, reason: str):
        """Add a new preference"""
        if category not in self.preferences:
            raise ValueError(f"Invalid category: {category}")

        self.preferences[category].append({
            "keyword": keyword,
            "score": score,
            "reason": reason
        })

        self.save()

    def save(self):
        """Save preferences to JSON file"""
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.preferences_path, 'w') as f:
            json.dump(self.preferences, f, indent=2)

    def load(self):
        """Load preferences from JSON file"""
        if not self.preferences_path.exists():
            # Save defaults
            self.save()
            return

        try:
            with open(self.preferences_path, 'r') as f:
                loaded = json.load(f)

            # Merge with defaults (in case new categories added)
            for category in self.DEFAULT_PREFERENCES:
                if category in loaded:
                    self.preferences[category] = loaded[category]

        except Exception as e:
            print(f"Warning: Could not load preferences: {e}")
            print("Using default preferences")


if __name__ == "__main__":
    # Test preferences system
    prefs = PreferencesSystem()

    # Test regular object
    score, reason = prefs.calculate_affinity("A beautiful colorful feather", "physical_object")
    print(f"Feather: {score} - {reason}")

    # Test dodo bird with large colorful beak
    score, reason = prefs.calculate_affinity(
        "A majestic dodo bird",
        "dodo_bird",
        {"is_dodo_bird": True, "beak_size": "large", "beak_color": "bright orange and yellow"}
    )
    print(f"Dodo with large colorful beak: {score} - {reason}")

    # Test negative object
    score, reason = prefs.calculate_affinity("A dangerous sharp metal cage", "physical_object")
    print(f"Metal cage: {score} - {reason}")
