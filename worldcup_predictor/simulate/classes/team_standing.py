from dataclasses import dataclass

@dataclass
class TeamStanding:
    """A team's position in a group table."""
    team:       str
    played:     int = 0
    wins:       int = 0
    draws:      int = 0
    losses:     int = 0
    goals_for:  int = 0
    goals_against: int = 0

    @property
    def points(self) -> int:
        return self.wins * 3 + self.draws

    @property
    def goal_diff(self) -> int:
        return self.goals_for - self.goals_against

    def update(self, goals_scored: int, goals_conceded: int):
        self.played     += 1
        self.goals_for  += goals_scored
        self.goals_against += goals_conceded
        gd = goals_scored - goals_conceded
        if gd > 0:
            self.wins   += 1
        elif gd == 0:
            self.draws  += 1
        else:
            self.losses += 1