"""
Game state management for Doda Terminal - Phase 2
Tracks gratification, gift history, and win/lose conditions
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path


@dataclass
class GiftRecord:
    """Record of a single gift evaluation"""
    timestamp: str
    object_type: str
    description: str
    affinity_score: int
    gratification_change: int
    total_gratification: int
    is_dodo_bird: bool = False
    beak_size: Optional[str] = None
    beak_color: Optional[str] = None


class GameState:
    """Manages Doda's gratification level and game state"""

    WIN_THRESHOLD = 30
    LOSE_THRESHOLD = -30

    def __init__(self, save_path: str = "game/save_state.json"):
        self.gratification = 0
        self.gift_history: List[GiftRecord] = []
        self.save_path = Path(save_path)
        self.game_over = False
        self.won = False

        # Load existing state if available
        self.load()

    def add_gift(self, gift_analysis: dict, affinity_score: int) -> GiftRecord:
        """
        Add a gift to history and update gratification

        Args:
            gift_analysis: Vision analysis dict with object_type, description, special_features
            affinity_score: Score from preferences (-10 to +10)

        Returns:
            GiftRecord with updated state
        """
        # Extract special features
        special = gift_analysis.get("special_features", {})
        is_dodo = special.get("is_dodo_bird", False)
        beak_size = special.get("beak_size", "N/A") if is_dodo else None
        beak_color = special.get("beak_color", "N/A") if is_dodo else None

        # Update gratification
        old_gratification = self.gratification
        self.gratification += affinity_score

        # Create record
        record = GiftRecord(
            timestamp=datetime.now().isoformat(),
            object_type=gift_analysis["object_type"],
            description=gift_analysis["description"],
            affinity_score=affinity_score,
            gratification_change=affinity_score,
            total_gratification=self.gratification,
            is_dodo_bird=is_dodo,
            beak_size=beak_size,
            beak_color=beak_color
        )

        self.gift_history.append(record)

        # Check win/lose conditions
        self._check_game_over()

        # Auto-save
        self.save()

        return record

    def _check_game_over(self):
        """Check if game has reached win or lose condition"""
        if self.gratification >= self.WIN_THRESHOLD:
            self.game_over = True
            self.won = True
        elif self.gratification <= self.LOSE_THRESHOLD:
            self.game_over = True
            self.won = False

    def get_status(self) -> dict:
        """Get current game status"""
        return {
            "gratification": self.gratification,
            "game_over": self.game_over,
            "won": self.won,
            "gift_count": len(self.gift_history),
            "win_threshold": self.WIN_THRESHOLD,
            "lose_threshold": self.LOSE_THRESHOLD
        }

    def reset(self):
        """Reset game state"""
        self.gratification = 0
        self.gift_history = []
        self.game_over = False
        self.won = False
        self.save()

    def save(self):
        """Save state to JSON file"""
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "gratification": self.gratification,
            "game_over": self.game_over,
            "won": self.won,
            "gift_history": [
                {
                    "timestamp": g.timestamp,
                    "object_type": g.object_type,
                    "description": g.description,
                    "affinity_score": g.affinity_score,
                    "gratification_change": g.gratification_change,
                    "total_gratification": g.total_gratification,
                    "is_dodo_bird": g.is_dodo_bird,
                    "beak_size": g.beak_size,
                    "beak_color": g.beak_color
                }
                for g in self.gift_history
            ]
        }

        with open(self.save_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self):
        """Load state from JSON file"""
        if not self.save_path.exists():
            return

        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)

            self.gratification = data.get("gratification", 0)
            self.game_over = data.get("game_over", False)
            self.won = data.get("won", False)

            # Reconstruct gift history
            self.gift_history = [
                GiftRecord(**gift) for gift in data.get("gift_history", [])
            ]
        except Exception as e:
            print(f"Warning: Could not load game state: {e}")
