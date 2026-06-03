import json
import os
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations

from simulate.classes.knockout_resolver import MatchStage
from src.config import WC_2026_GROUPS, FIXTURE_CITIES
from simulate.classes.groupstage_simulator import GroupStageSimulator
from simulate.classes.third_place import ThirdPlaceQualifier
from simulate.classes.knockout_simulator import KnockoutSimulator


class TournamentSimulator:
    """
    Orchestrates the full WC 2026 tournament simulation.

    Two modes:
      predict()      → single deterministic prediction
      monte_carlo()  → N simulations → probability distributions
    """

    def __init__(self, predictor, feature_builder, preprocessor):
        self.predictor = predictor
        self.feature_builder = feature_builder
        self.preprocessor = preprocessor
        self.group_sim = GroupStageSimulator(predictor, feature_builder, preprocessor)
        self.knockout_sim = KnockoutSimulator(predictor, feature_builder, preprocessor)
        self.third_place  = ThirdPlaceQualifier()

    def predict(self) -> dict:
        print("\n" + "═" * 55)
        print("  WC 2026 Tournament Prediction")
        print("═" * 55)

        return self.run_tournament(probabilistic=False)

    def monte_carlo(self, n_simulations: int = 10000) -> dict:
        """
        Run N probabilistic tournament simulations and aggregate results into
        per-team stage-reach probabilities.
        """
        print(f"\n{'═' * 55}")
        print(f"  Monte Carlo Simulation ({n_simulations:,} runs)")
        print(f"{'═' * 55}")

        win_counts = defaultdict(int)
        final_counts = defaultdict(int)
        semi_counts = defaultdict(int)
        quarter_counts = defaultdict(int)
        r16_counts = defaultdict(int)
        r32_counts = defaultdict(int)

        successful = 0
        failed = 0
        log_every = max(1, n_simulations // 10)

        for i in range(n_simulations):
            if (i + 1) % log_every == 0:
                print(f"  Simulation {i+1:,} / {n_simulations:,}...")

            try:
                result = self.run_tournament(probabilistic=True)

                win_counts[result['winner']] += 1
                for team in result.get('finalists', []):
                    final_counts[team] += 1
                for team in result.get('semi_finalists', []):
                    semi_counts[team] += 1
                for team in result.get('quarter_finalists', []):
                    quarter_counts[team] += 1
                for team in result.get('r16_teams', []):
                    r16_counts[team] += 1
                for team in result.get('r32_teams', []):
                    r32_counts[team] += 1

                successful += 1

            except Exception:
                failed += 1
                continue

        if successful == 0:
            raise RuntimeError("All simulations failed — cannot build probability table.")

        if failed > 0:
            print(f"  ⚠️  {failed} simulation(s) failed and were skipped.")

        probs = self.build_probability_table(successful, win_counts, final_counts, semi_counts, quarter_counts, r16_counts, r32_counts)

        print(f"\n  ✅ Monte Carlo complete ({successful:,} successful runs)")
        print(f"\n  Top 10 tournament winners:")
        for _, row in probs.head(10).iterrows():
            bar = '█' * int(row['win_prob'] * 200)
            print(f"    {row['team']:<25} {row['win_prob']*100:5.1f}%  {bar}")

        return {
            'n_simulations': successful,
            'probabilities': probs,
            'most_likely_winner': probs.iloc[0]['team'],
        }

    def run_tournament(self, probabilistic: bool) -> dict:

        # Group Stage
        standings, group_results = self.group_sim.simulate(probabilistic)

        # Determine qualified teams
        qualified  = self.get_qualified_teams(standings)
        r32_teams  = list(qualified['first'] + qualified['second'] + qualified['third'])

        # Round of 32
        r32_fixtures = self.build_r32_fixtures(qualified)
        r16_teams, r32_results = self.knockout_sim.simulate_round(
            r32_fixtures, MatchStage.ROUND_OF_32, probabilistic
        )

        # Round of 16
        r16_fixtures = self.pair_teams(r16_teams)
        qf_teams, r16_results = self.knockout_sim.simulate_round(
            r16_fixtures, MatchStage.ROUND_OF_16, probabilistic
        )

        # Quarter Finals
        qf_fixtures = self.pair_teams(qf_teams)
        sf_teams, qf_results = self.knockout_sim.simulate_round(
            qf_fixtures, MatchStage.QUARTER_FINAL, probabilistic
        )

        # Semi Finals 
        sf_fixtures = self.pair_teams(sf_teams)
        finalists, sf_results = self.knockout_sim.simulate_round(
            sf_fixtures, MatchStage.SEMI_FINAL, probabilistic
        )

        # Final
        final_fixture = [(finalists[0], finalists[1])]
        champion, final_result = self.knockout_sim.simulate_round(
            final_fixture, MatchStage.FINAL, probabilistic
        )

        return {
            'winner': champion[0],
            'finalists': finalists,
            'semi_finalists': sf_teams,
            'quarter_finalists': qf_teams,
            'r16_teams': r16_teams,
            'r32_teams': r32_teams,
            'group_standings': standings,
            'group_results': group_results,
            'r32_results': r32_results,
            'r16_results': r16_results,
            'qf_results': qf_results,
            'sf_results': sf_results,
            'final_result': final_result[0],
        }

    def get_qualified_teams(self, standings: dict) -> dict:
        first  = []
        second = []
        third  = []

        for group, group_standings in standings.items():
            if len(group_standings) >= 1:
                first.append(group_standings[0].team)
            if len(group_standings) >= 2:
                second.append(group_standings[1].team)
            if len(group_standings) >= 3:
                third.append(group_standings[2].team)

        # Get best 8 third place teams
        third_qualifiers = self.third_place.get_qualifiers(standings)

        return {
            'first': first,
            'second': second,
            'third': third_qualifiers,
        }

    def build_r32_fixtures(self, qualified: dict) -> list[tuple[str, str]]:
        fixtures = []
        firsts   = qualified['first']    # 12 group winners
        seconds  = qualified['second']   # 12 group runners-up
        thirds   = qualified['third']    # 8 best third-place

        # Pair group winners vs runners-up from different groups
        # Simplified: pair by bracket position
        all_32 = firsts[:12] + seconds[:12] + thirds[:8]

        # Pair sequentially: [0vs16, 1vs17, 2vs18, ...]
        # In a real implementation this follows FIFA's confirmed bracket
        half = len(all_32) // 2
        for i in range(half):
            if i < len(all_32) and (i + half) < len(all_32):
                fixtures.append((all_32[i], all_32[i + half]))

        return fixtures

    def pair_teams(self, teams: list) -> list[tuple[str, str]]:
        fixtures = []
        for i in range(0, len(teams) - 1, 2):
            fixtures.append((teams[i], teams[i + 1]))
        return fixtures

    # Monte Carlo aggregation

    def build_probability_table(self, n: int, win_counts: dict, final_counts: dict, semi_counts: dict, quarter_counts: dict, r16_counts: dict, r32_counts: dict) -> pd.DataFrame:
        all_teams = (
            set(win_counts) | set(final_counts) | set(semi_counts) |
            set(quarter_counts) | set(r16_counts) | set(r32_counts)
        )

        rows = [{
            'team': team,
            'win_prob': win_counts[team]     / n,
            'final_prob': final_counts[team]   / n,
            'semi_prob': semi_counts[team]    / n,
            'quarter_prob': quarter_counts[team] / n,
            'r16_prob': r16_counts[team]     / n,
            'r32_prob': r32_counts[team]     / n,
        } for team in all_teams]

        return (pd.DataFrame(rows).sort_values('win_prob', ascending=False).reset_index(drop=True))


    def export_results(
        self,
        prediction: dict,
        mc_results: dict,
        path: str = 'data/results/simulation_output.json',
    ) -> dict:
        """
        Serialize deterministic + Monte Carlo results to JSON.
        Returns the dict so the API can serve it directly.
        """
        def _standing(s) -> dict:
            return {
                'team': s.team,
                'played': s.played,
                'wins': s.wins,
                'draws': s.draws,
                'losses': s.losses,
                'goals_for': s.goals_for,
                'goals_against': s.goals_against,
                'goal_diff': s.goal_diff,
                'points': s.points,
            }

        def _group_match(r) -> dict:
            return {
                'home_team': r.home_team,
                'away_team': r.away_team,
                'home_goals': r.home_goals,
                'away_goals': r.away_goals,
                'result': r.result,
                'winner': r.winner,
                'home_win_prob': round(r.home_win_prob, 4),
                'draw_prob': round(r.draw_prob, 4),
                'away_win_prob': round(r.away_win_prob, 4),
                'stage': r.stage,
                'city': r.city,
            }

        def _default(obj):
            if hasattr(obj, 'item'):        # numpy scalar
                return obj.item()
            if hasattr(obj, 'isoformat'):   # datetime / Timestamp
                return obj.isoformat()
            raise TypeError(f"Not serializable: {type(obj)}")

        output = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'deterministic': {
                'winner': prediction['winner'],
                'finalists': prediction['finalists'],
                'semi_finalists': prediction['semi_finalists'],
                'quarter_finalists': prediction['quarter_finalists'],
                'r16_teams': prediction['r16_teams'],
                'r32_teams': prediction['r32_teams'],
                'group_stage': {
                    'standings': {
                        group: [_standing(s) for s in standings]
                        for group, standings in prediction['group_standings'].items()
                    },
                    'matches': {
                        group: [_group_match(r) for r in matches]
                        for group, matches in prediction['group_results'].items()
                    },
                },
                'knockout': {
                    'round_of_32': prediction['r32_results'],
                    'round_of_16': prediction['r16_results'],
                    'quarter_finals': prediction['qf_results'],
                    'semi_finals': prediction['sf_results'],
                    'final': prediction['final_result'],
                },
            },
            'monte_carlo': {
                'n_simulations': mc_results['n_simulations'],
                'most_likely_winner': mc_results['most_likely_winner'],
                'teams': mc_results['probabilities'].to_dict(orient='records'),
            },
        }

        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, default=_default)

        print(f"\n  Results saved to {path}")
        return output

    def generate_fixture_predictions(self) -> list[dict]:
        """
        Predict all 72 WC 2026 group stage fixtures individually.
        Returns a list of dicts ready for the /api/fixtures endpoint.
        Actual result fields are null — populated later as results come in.
        """
        results = []

        for group, teams in WC_2026_GROUPS.items():
            for team_a, team_b in combinations(teams, 2):
                city = (FIXTURE_CITIES.get((team_a, team_b)) or
                        FIXTURE_CITIES.get((team_b, team_a)))

                # Mirror build_wc2026_fixtures: stronger ELO team is home
                elo_df = self.feature_builder.elo
                elo_a = elo_df[elo_df['team'] == team_a]['elo'].values
                elo_b = elo_df[elo_df['team'] == team_b]['elo'].values
                elo_a = float(elo_a[0]) if len(elo_a) > 0 else 0.0
                elo_b = float(elo_b[0]) if len(elo_b) > 0 else 0.0
                home_team = team_a if elo_a >= elo_b else team_b
                away_team = team_b if elo_a >= elo_b else team_a

                try:
                    features = self.feature_builder.build_fixture_features(
                        home_team, away_team, date='2026-06-11', neutral=True, city=city,
                    )
                    X = pd.DataFrame([features])
                    X, _ = self.preprocessor.transform(X, scale=True)
                    preds = self.predictor.predict(X).iloc[0]

                    fixture_id = (
                        f"{group.replace(' ', '_').lower()}"
                        f"_{home_team.replace(' ', '_').lower()}"
                        f"_vs_{away_team.replace(' ', '_').lower()}"
                    )

                    results.append({
                        'id': fixture_id,
                        'group': group,
                        'stage': 'Group Stage',
                        'home_team': home_team,
                        'away_team': away_team,
                        'city': city or 'TBD',
                        'date': '2026-06-11',
                        'home_win_prob': round(float(preds['prob_home_win']), 4),
                        'draw_prob': round(float(preds['prob_draw']), 4),
                        'away_win_prob': round(float(preds['prob_away_win']), 4),
                        'predicted_outcome': str(preds['predicted_result']),
                        'predicted_home_goals': round(float(preds['predicted_home_goals']), 2),
                        'predicted_away_goals': round(float(preds['predicted_away_goals']), 2),
                        'predicted_score': str(preds['predicted_score']),
                        'actual_home_goals': None,
                        'actual_away_goals': None,
                        'actual_outcome': None,
                        'prediction_correct': None,
                    })
                except Exception as e:
                    print(f"  Fixture prediction failed {home_team} vs {away_team}: {e}")

        return results

