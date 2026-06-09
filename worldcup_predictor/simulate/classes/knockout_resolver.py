"""
knockout_resolver.py

Resolves match predictions for knockout rounds where a draw
is not a valid final outcome.

Two components:
  MatchStage      — enum defining tournament stages
  KnockoutResolver — handles draw redistribution and penalty simulation
"""

import numpy as np
from enum import Enum
from typing import Optional

class MatchStage(Enum):
    GROUP = "group"
    ROUND_OF_32 = "round_of_32"
    ROUND_OF_16 = "round_of_16"
    QUARTER_FINAL = "quarter_final"
    SEMI_FINAL = "semi_final"
    FINAL = "final"
    @property
    def is_knockout(self) -> bool:
        """Returns True for any stage where a draw is invalid."""
        return self != MatchStage.GROUP

    @property
    def display_name(self) -> str:
        """Human-readable stage name for GUI display."""
        names = {
            'group':'Group Stage',
            'round_of_32': 'Round of 32',
            'round_of_16': 'Round of 16',
            'quarter_final': 'Quarter Final',
            'semi_final': 'Semi Final',
            'final': 'Final',
        }
        return names.get(self.value, self.value)

class KnockoutResolver:
    PENALTY_THRESHOLD = 0.05

    def resolve(
        self,
        home_team:           str,
        away_team:           str,
        probs:               dict,
        stage:               MatchStage,
        simulate_penalties:  bool = True,
    ) -> dict:
        """
        Resolve a match prediction for the given stage.

        Args:
            home_team:          Home team name
            away_team:          Away team name
            probs:              Dict with keys home_win, draw, away_win
            stage:              MatchStage — determines if draw is valid
            simulate_penalties: If True, simulate shootout when very close

        Returns:
            Dict containing:
              winner, method, stage, home_win_prob,
              away_win_prob, draw_prob (group only), went_to_pens
        """
        if not stage.is_knockout:
            return self.resolve_group(home_team, away_team, probs, stage)

        return self.resolve_knockout(
            home_team, away_team, probs, stage, simulate_penalties
        )

    def resolve_group(self, home_team: str, away_team: str, probs: dict, stage: MatchStage) -> dict:
        """Return group stage result — draw is a valid outcome."""
        outcome_map = {
            'home_win': home_team,
            'draw':     'draw',
            'away_win': away_team,
        }
        predicted = max(probs, key=probs.get)

        return {
            'home_team':      home_team,
            'away_team':      away_team,
            'winner':         outcome_map[predicted],
            'method':         '90_minutes',
            'stage':          stage.value,
            'display_stage':  stage.display_name,
            'home_win_prob':  round(probs.get('home_win', 0), 4),
            'draw_prob':      round(probs.get('draw', 0), 4),
            'away_win_prob':  round(probs.get('away_win', 0), 4),
            'went_to_pens':   False,
        }

    def resolve_knockout(self, home_team: str, away_team: str, probs: dict, stage: MatchStage, simulate_penalties: bool) -> dict:
        """
        Resolve a knockout match:
          1. Redistribute draw probability proportionally
          2. Check if close enough for penalties
          3. Determine winner
        """
        # Step 1 — redistribute draw
        adj = self.redistribute_draw(probs)
        home_prob = adj['home_win']
        away_prob = adj['away_win']
        diff      = abs(home_prob - away_prob)

        # Step 2 — check for penalty shootout
        if simulate_penalties and diff < self.PENALTY_THRESHOLD:
            return self.simulate_penalties(
                home_team, away_team, probs, adj, stage
            )

        # Step 3 — winner: sample probabilistically in Monte Carlo, deterministic otherwise
        if simulate_penalties:
            p = np.array([home_prob, away_prob])
            p /= p.sum()
            winner = np.random.choice([home_team, away_team], p=p)
        else:
            winner = home_team if home_prob > away_prob else away_team

        # Determine method — extra time if draw was likely
        method = 'extra_time' if probs.get('draw', 0) > 0.25 else '90_minutes'

        return {
            'home_team':       home_team,
            'away_team':       away_team,
            'winner':          winner,
            'method':          method,
            'stage':           stage.value,
            'display_stage':   stage.display_name,
            'home_win_prob':   round(home_prob, 4),
            'away_win_prob':   round(away_prob, 4),
            'draw_prob_orig':  round(probs.get('draw', 0), 4),
            'went_to_pens':    False,
        }

    # ── Draw redistribution ───────────────────────────────────────────────

    def redistribute_draw(self, probs: dict) -> dict:
        """
        Proportionally redistribute draw probability to home/away.

        Example:
          home=0.35, draw=0.40, away=0.25
          total_win = 0.35 + 0.25 = 0.60
          home_share = 0.35/0.60 = 0.583
          away_share = 0.25/0.60 = 0.417
          home_adj = 0.35 + 0.40*0.583 = 0.583
          away_adj = 0.25 + 0.40*0.417 = 0.417
        """
        home_p = probs.get('home_win', 0)
        away_p = probs.get('away_win', 0)
        draw_p = probs.get('draw', 0)

        total_win = home_p + away_p

        # Edge case: both zero
        if total_win == 0:
            return {'home_win': 0.5, 'away_win': 0.5, 'draw': 0.0}

        home_share = home_p / total_win
        away_share = away_p / total_win

        return {
            'home_win': round(home_p + draw_p * home_share, 6),
            'away_win': round(away_p + draw_p * away_share, 6),
            'draw':     0.0,
        }

    def simulate_penalties(
        self,
        home_team: str,
        away_team: str,
        orig_probs: dict,
        adj_probs:  dict,
        stage:      MatchStage,
    ) -> dict:
        """
        Simulate a penalty shootout.

        Penalties are largely a lottery but we weight slightly
        by the stronger team's adjusted probability:
          pen_prob = 0.5 * 0.7 + adj_prob * 0.3
          (70% random + 30% strength-weighted)
        """
        home_p = adj_probs['home_win']
        away_p = adj_probs['away_win']

        # Blend 50/50 with strength weighting
        pen_home = 0.5 * 0.7 + home_p * 0.3
        pen_away = 0.5 * 0.7 + away_p * 0.3

        # Normalise to sum to 1
        total    = pen_home + pen_away
        pen_home = pen_home / total
        pen_away = pen_away / total

        # Simulate the shootout
        winner = home_team if np.random.random() < pen_home else away_team

        return {
            'home_team':       home_team,
            'away_team':       away_team,
            'winner':          winner,
            'method':          'penalties',
            'stage':           stage.value,
            'display_stage':   stage.display_name,
            'home_win_prob':   round(pen_home, 4),
            'away_win_prob':   round(pen_away, 4),
            'draw_prob_orig':  round(orig_probs.get('draw', 0), 4),
            'went_to_pens':    True,
        }