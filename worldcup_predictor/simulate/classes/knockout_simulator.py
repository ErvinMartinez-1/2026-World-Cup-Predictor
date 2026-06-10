import numpy as np
import pandas as pd

from worldcup_predictor.simulate.classes.knockout_resolver import KnockoutResolver, MatchStage
from worldcup_predictor.simulate.score_utils import get_most_likely_score
class KnockoutSimulator:
    """
    Simulates all knockout rounds from Round of 32 through the Final.

    Uses KnockoutResolver to handle draw redistribution and
    penalty shootout simulation.
    """

    # FIFA 2026 Round of 32 bracket structure
    # Format: (group_position, group) where position is
    # '1st_A' = group A winner, '2nd_B' = group B runner up
    # '3rd_best' = one of the 8 best third place teams
    ROUND_OF_32_BRACKET = [
        # Match 73-88 — confirmed FIFA bracket pairings
        ('1st_A', '2nd_B'),
        ('1st_C', '3rd_ABDE'),
        ('1st_B', '3rd_EFGIJ'),
        ('1st_D', '2nd_C'),
        ('1st_E', '2nd_F'),
        ('1st_G', '3rd_AEHIJ'),
        ('1st_F', '2nd_E'),
        ('1st_H', '2nd_J'),
        ('1st_I', '2nd_H'),
        ('1st_J', '2nd_I'),
        ('1st_K', '3rd_DEJIL'),
        ('2nd_K', '2nd_L'),
        ('1st_L', '3rd_EHIJK'),
        ('2nd_D', '2nd_G'),
        ('2nd_A', '3rd_BCFIJ'),
        ('1st_B', '3rd_best'),
    ]

    def __init__(self, predictor, feature_builder, preprocessor):
        self.predictor = predictor
        self.feature_builder = feature_builder
        self.preprocessor = preprocessor
        self.resolver = KnockoutResolver()

    def simulate_round(self, fixtures: list[tuple[str, str]], stage: MatchStage, probabilistic: bool = True) -> tuple[list[str], list[dict]]:
        winners = []
        results = []

        for home_team, away_team in fixtures:
            result = self.simulate_knockout_match(home_team, away_team, stage, probabilistic)
            winners.append(result['winner'])
            results.append(result)

        return winners, results

    def simulate_knockout_match(self, home_team: str, away_team:str, stage: MatchStage, probabilistic: bool) -> dict:
        """Simulate a single knockout match with draw resolution."""
        try:
            features = self.feature_builder.build_fixture_features(
                home_team=home_team,
                away_team=away_team,
                date="2026-07-01",
                neutral=True,
            )
            X = pd.DataFrame([features])
            X, _ = self.preprocessor.transform(X, scale=True)
            preds = self.predictor.predict(X).iloc[0]

            probs = {
                'home_win': float(preds['prob_home_win']),
                'draw': float(preds['prob_draw']),
                'away_win': float(preds['prob_away_win'])
            }

            exp_home_goals = float(preds['predicted_home_goals'])
            exp_away_goals = float(preds['predicted_away_goals'])

        except Exception as e:
            probs = {'home_win': 0.4, 'draw': 0.2, 'away_win': 0.4}
            exp_home_goals = exp_away_goals = 1.0

        # Resolve winner (no draws in knockout)
        resolution = self.resolver.resolve(
            home_team=home_team,
            away_team=away_team,
            probs=probs,
            stage=stage,
            simulate_penalties=probabilistic,
        )

        # Simulate scoreline
        if probabilistic:
            home_goals = np.random.poisson(max(exp_home_goals, 0.1))
            away_goals = np.random.poisson(max(exp_away_goals, 0.1))
        else:
            home_goals, away_goals = get_most_likely_score(exp_home_goals, exp_away_goals, probs['home_win'], probs['draw'], probs['away_win'])

        # Adjust score to match resolved winner
        winner = resolution['winner']
        if winner == home_team and home_goals <= away_goals:
            home_goals = away_goals + 1
        elif winner == away_team and away_goals <= home_goals:
            away_goals = home_goals + 1

        return {
            **resolution,
            'home_goals':     home_goals,
            'away_goals':     away_goals,
            'predicted_score': f"{home_goals}-{away_goals}"
        }