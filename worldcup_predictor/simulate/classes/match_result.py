from dataclasses import dataclass
from typing import Optional

@dataclass
class MatchResult:
    """Result of a single simulated match."""
    home_team:    str
    away_team:    str
    home_goals:   int
    away_goals:   int
    home_win_prob: float
    draw_prob:     float
    away_win_prob: float
    stage:         str
    city:          str = ""

    @property
    def winner(self) -> Optional[str]:
        if self.home_goals > self.away_goals:
            return self.home_team
        elif self.away_goals > self.home_goals:
            return self.away_team
        return None  # draw

    @property
    def result(self) -> str:
        if self.home_goals > self.away_goals:
            return 'home_win'
        elif self.away_goals > self.home_goals:
            return 'away_win'
        return 'draw'