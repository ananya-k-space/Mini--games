# utils/scoreboard.py
"""Global scoreboard system - Python 3.14 compatible"""

from __future__ import annotations
import json
from pathlib import Path
from typing import TypedDict, Final
from datetime import datetime

class PlayerScore(TypedDict):
    name: str
    score: int
    level: int
    timestamp: str
    game: str

class ScoreboardManager:
    """Manages high scores across all games"""
    
    SCORES_FILE: Final[str] = "scores.json"
    
    def __init__(self) -> None:
        self.scores: dict[str, list[PlayerScore]] = {
            'Memory Match': [],
            'Number Rush': [],
            'Color Blast': []
        }
        self.load_scores()
    
    def load_scores(self) -> None:
        """Load scores from file"""
        try:
            score_path = Path(self.SCORES_FILE)
            if score_path.exists():
                with open(self.SCORES_FILE, 'r') as f:
                    self.scores = json.load(f)
        except Exception as e:
            print(f"Could not load scores: {e}")
    
    def save_scores(self) -> None:
        """Save scores to file"""
        try:
            with open(self.SCORES_FILE, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except Exception as e:
            print(f"Could not save scores: {e}")
    
    def add_score(self, game: str, player_name: str, score: int, level: int) -> bool:
        """Add a new score to the leaderboard"""
        if game not in self.scores:
            return False
        
        new_score: PlayerScore = {
            'name': player_name,
            'score': score,
            'level': level,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'game': game
        }
        
        self.scores[game].append(new_score)
        self.scores[game].sort(key=lambda x: (x['score'], x['level']), reverse=True)
        self.scores[game] = self.scores[game][:10]
        
        self.save_scores()
        return True
    
    def get_top_scores(self, game: str, limit: int = 10) -> list[PlayerScore]:
        """Get top scores for a game"""
        return self.scores.get(game, [])[:limit]
    
    def get_player_rank(self, game: str, player_name: str) -> int:
        """Get player's rank in a game"""
        scores = self.scores.get(game, [])
        for i, score in enumerate(scores, 1):
            if score['name'] == player_name:
                return i
        return -1
    
    def clear_scores(self, game: str | None = None) -> None:
        """Clear scores for a game or all games"""
        if game:
            self.scores[game] = []
        else:
            for key in self.scores:
                self.scores[key] = []
        self.save_scores()

scoreboard = ScoreboardManager()