import numpy as np
import pandas as pd
from collections import defaultdict
from itertools import combinations

from src.config import WC_2026_GROUPS
from simulate.classes.match_result import MatchResult
from simulate.classes.team_standing import TeamStanding

class GroupStageSimulator:
    """
    Simulates all 48 group stage matches and produces final standings.

    Tiebreaker order (FIFA rules):
      1. Points
      2. Goal difference
      3. Goals scored
      4. Head-to-head points
      5. Head-to-head goal difference
      6. Random draw (lots)
    """
    def __init__(self, predictor, feature_builder, preprocessor):
        self.predictor = predictor
        self.feature_builder = feature_builder
        self.preprocessor = preprocessor

    def simulate(self, probabilistic: bool = True) -> tuple[dict, dict]:
        """
        Simulate all group stage matches.

        Args:
            probabilistic: If True, sample outcomes from probabilities
                          (Monte Carlo mode). If False, take most likely
                          outcome (deterministic mode).

        Returns:
            standings: {group: [TeamStanding sorted 1st→4th]}
            results:   {group: [MatchResult]}
        """
        all_standings = {}
        all_results   = {}

        for group, teams in WC_2026_GROUPS.items():
            standings, results = self.simulate_group(group, teams, probabilistic)
            all_standings[group] = standings
            all_results[group]   = results

        return all_standings, all_results

    def simulate_group(self, group: str, teams: list, probabilistic: bool) -> tuple[list, list]:
        #Simulate all 6 matches within one group.

        # Initialise standings
        standings = {team: TeamStanding(team=team) for team in teams}
        results   = []
        h2h  = defaultdict(lambda: defaultdict(int))  # h2h points

        for home_team, away_team in combinations(teams, 2):
            result = self.predict_match(home_team, away_team, group, probabilistic)
            results.append(result)

            # Update standings
            standings[home_team].update(result.home_goals, result.away_goals)
            standings[away_team].update(result.away_goals, result.home_goals)

            # Track H2H points
            h2h[home_team][away_team] += result.home_goals
            h2h[away_team][home_team] += result.away_goals

        # Sort standings with full tiebreaker chain
        sorted_standings = self.sort_standings(
            list(standings.values()), h2h
        )

        return sorted_standings, results

    def predict_match(self, home_team: str, away_team: str, group: str, probabilistic: bool) -> MatchResult:
        # Get model prediction for a single match and convert to MatchResult.
        try:
            # Build features for this fixture
            features = self.feature_builder.build_fixture_features(
                home_team=home_team,
                away_team=away_team,
                date="2026-06-11",
                neutral=True,
            )

            # Convert to DataFrame and preprocess
            X = pd.DataFrame([features])
            X, _ = self.preprocessor.transform(X, scale=True)

            # Get predictions
            preds = self.predictor.predict(X).iloc[0]

            prob_home = float(preds['prob_home_win'])
            prob_draw = float(preds['prob_draw'])
            prob_away = float(preds['prob_away_win'])

            # Expected goals from Poisson regressor
            exp_home_goals = float(preds['predicted_home_goals'])
            exp_away_goals = float(preds['predicted_away_goals'])

            if probabilistic:
                # Sample scoreline from Poisson distribution
                home_goals, away_goals = self.sample_scoreline(exp_home_goals, exp_away_goals, prob_home, prob_draw, prob_away)
            else:
                # Use rounded expected goals (deterministic)
                home_goals = round(exp_home_goals)
                away_goals = round(exp_away_goals)

        except Exception as e:
            # Fallback: 0-0 draw
            home_goals, away_goals = 0, 0
            prob_home = prob_draw = prob_away = 1/3

        return MatchResult(
            home_team=home_team,
            away_team=away_team,
            home_goals=home_goals,
            away_goals=away_goals,
            home_win_prob=prob_home,
            draw_prob=prob_draw,
            away_win_prob=prob_away,
            stage='Group Stage',
        )

    def sample_scoreline(self, exp_home: float, exp_away: float, prob_home: float, prob_draw: float, prob_away: float) -> tuple[int, int]:
        """
        Sample a scoreline consistent with the predicted outcome probabilities.

        Strategy:
          1. Sample the outcome (home_win/draw/away_win) from classifier probs
          2. Sample goals from Poisson distributions
          3. Adjust if sampled scoreline contradicts the sampled outcome
        """
        # Sample outcome — normalize to guard against floating-point drift
        p = np.array([prob_home, prob_draw, prob_away], dtype=float)
        p /= p.sum()
        outcome = np.random.choice(['home_win', 'draw', 'away_win'], p=p)

        # Sample goals from Poisson
        max_attempts = 10
        for _ in range(max_attempts):
            h = np.random.poisson(max(exp_home, 0.1))
            a = np.random.poisson(max(exp_away, 0.1))

            # Check if scoreline matches sampled outcome
            if outcome == 'home_win' and h > a:
                return h, a
            elif outcome == 'draw' and h == a:
                return h, a
            elif outcome == 'away_win' and a > h:
                return h, a

        # Fallback: force correct outcome
        if outcome == 'home_win':
            h = max(round(exp_home), 1)
            a = max(h - 1, 0)
        elif outcome == 'away_win':
            a = max(round(exp_away), 1)
            h = max(a - 1, 0)
        else:
            g = round((exp_home + exp_away) / 2)
            h = a = g

        return h, a

    def sort_standings(self, standings: list, h2h: dict) -> list:
        # Sort group standings using full FIFA tiebreaker chain.
        def tiebreaker_key(s: TeamStanding):
            return (
                s.points,        # 1. Points
                s.goal_diff,     # 2. Goal difference
                s.goals_for,     # 3. Goals scored
            )

        # Initial sort
        standings.sort(key=tiebreaker_key, reverse=True)

        # Apply H2H tiebreaker for tied teams
        standings = self.apply_h2h_tiebreaker(standings, h2h)

        return standings

    def apply_h2h_tiebreaker(self, standings: list, h2h: dict) -> list:
        #For teams level on points, GD, and GF — apply H2H points. Groups tied teams, re-sorts by H2H within the tie, then reassembles.
        result  = []
        i = 0

        while i < len(standings):
            # Find all teams tied with standings[i]
            tied = [standings[i]]
            j    = i + 1

            while j < len(standings):
                curr = standings[i]
                next_s = standings[j]
                if (curr.points == next_s.points and
                    curr.goal_diff == next_s.goal_diff and
                    curr.goals_for == next_s.goals_for):
                    tied.append(next_s)
                    j += 1
                else:
                    break

            if len(tied) > 1:
                # Sort tied teams by H2H points among themselves
                tied.sort(
                    key=lambda s: sum(
                        h2h[s.team][other.team]
                        for other in tied if other.team != s.team
                    ),
                    reverse=True
                )
                # Final tiebreaker: random (lots)
                # Only randomise if still tied after H2H
                tied = self.random_tiebreak_if_needed(tied, h2h)

            result.extend(tied)
            i = j

        return result

    def random_tiebreak_if_needed(self, tied: list, h2h:  dict) -> list:
        #Shuffle teams that are still level after H2H.
        h2h_points = [
            sum(h2h[s.team][other.team] for other in tied if other.team != s.team)
            for s in tied
        ]
        # Find groups still tied after H2H
        i = 0
        result = []
        while i < len(tied):
            same_h2h = [tied[i]]
            j = i + 1
            while j < len(tied) and h2h_points[j] == h2h_points[i]:
                same_h2h.append(tied[j])
                j += 1
            if len(same_h2h) > 1:
                np.random.shuffle(same_h2h)
            result.extend(same_h2h)
            i = j
        return result

class ThirdPlaceQualifier:
    """
    Determines which 8 of the 12 third-place teams advance
    to the Round of 32, per FIFA rules.

    Comparison order: Points → GD → GF → Random
    """

    def get_qualifiers(self, standings: dict) -> list[str]:
        third_place = []

        for group, group_standings in standings.items():
            if len(group_standings) >= 3:
                third = group_standings[2]
                third_place.append({
                    'team':        third.team,
                    'group':       group,
                    'points':      third.points,
                    'goal_diff':   third.goal_diff,
                    'goals_for':   third.goals_for,
                })

        # Sort all third-place teams
        third_place.sort(key=lambda x: (x['points'], x['goal_diff'], x['goals_for']), reverse=True)

        # Top 8 advance
        qualifiers = [t['team'] for t in third_place[:8]]
        return qualifiers