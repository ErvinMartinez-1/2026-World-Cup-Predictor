import joblib
import pandas as pd
from pathlib import Path

from src.pipeline import DataPipeline
from src.feature_builder import FeatureBuilder
from src.data_preprocessor import DataPreprocessor
from src.models.match_predictor import MatchPredictor
from worldcup_predictor.simulate.tournament import TournamentSimulator


def print_team_path(team: str, prediction: dict) -> None:
    """Print the predicted knockout route for a given team."""
    rounds = [
        ('Round of 32',   prediction['r32_results']),
        ('Round of 16',   prediction['r16_results']),
        ('Quarter Final', prediction['qf_results']),
        ('Semi Final',    prediction['sf_results']),
        ('Final',         [prediction['final_result']]),
    ]

    print(f"\n── {team}'s Predicted Path ──────────────────────────")
    found_in_any = False
    for stage_name, results in rounds:
        for r in results:
            if team not in (r['home_team'], r['away_team']):
                continue
            found_in_any = True
            opponent  = r['away_team'] if r['home_team'] == team else r['home_team']
            won       = r['winner'] == team
            my_prob   = r['home_win_prob'] if r['home_team'] == team else r['away_win_prob']
            outcome   = 'W' if won else 'L'
            print(f"  {stage_name:<15} vs {opponent:<22} {outcome}  "
                  f"({r['method']}, win prob: {my_prob*100:.1f}%)")
            break

    if not found_in_any:
        print(f"  {team} did not qualify for the knockout stage.")


def main():

    # ── Load pipeline ──────────────────────────────────────────────────
    print("Loading data pipeline...")
    pipeline = DataPipeline().run()

    # ── Load feature builder ───────────────────────────────────────────
    fb = FeatureBuilder(
        matches=pipeline.matches,
        rankings=pipeline.rankings,
        elo=pipeline.elo,
    )

    # ── Load trained model and preprocessor ───────────────────────────
    print("Loading trained model...")
    predictor    = MatchPredictor.load(Path("data/processed/models"))
    preprocessor = DataPreprocessor.load(Path("data/processed/preprocessor.joblib"))

    # ── Initialise simulator ───────────────────────────────────────────
    simulator = TournamentSimulator(
        predictor=predictor,
        feature_builder=fb,
        preprocessor=preprocessor,
    )

    # ── Run deterministic prediction ───────────────────────────────────
    print("\n" + "═" * 55)
    print("  DETERMINISTIC PREDICTION")
    print("═" * 55)

    prediction = simulator.predict()

    print(f"\n🏆 Predicted Winner: {prediction['winner']}")
    print(f"🥈 Runners Up:       {[t for t in prediction['finalists'] if t != prediction['winner']]}")
    print(f"\nSemi Finalists: {prediction['semi_finalists']}")
    print(f"Quarter Finalists: {prediction['quarter_finalists']}")

    print("\n── Group Standings ──────────────────────────────────")
    for group, standings in prediction['group_standings'].items():
        print(f"\n  {group}:")
        for i, s in enumerate(standings):
            marker = "✅" if i < 2 else ("🔵" if i == 2 else "❌")
            print(f"    {marker} {i+1}. {s.team:<25} "
                  f"Pts:{s.points}  GD:{s.goal_diff:+d}  "
                  f"GF:{s.goals_for}")

    print("\n── Group Results Sample ─────────────────────────────")
    for group, results in list(prediction['group_results'].items())[:2]:
        print(f"\n  {group}:")
        for r in results:
            print(f"    {r.home_team:<20} {r.home_goals} - "
                  f"{r.away_goals}  {r.away_team}")

    print("\n── Knockout Results ─────────────────────────────────")
    print(f"\n  Round of 32:")
    for r in prediction['r32_results']:
        print(f"    {r['home_team']:<20} vs {r['away_team']:<20} "
              f"→ {r['winner']} ({r['method']})")

    print(f"\n  Round of 16:")
    for r in prediction['r16_results']:
        print(f"    {r['home_team']:<20} vs {r['away_team']:<20} "
              f"→ {r['winner']} ({r['method']})")

    print(f"\n  Quarter Finals:")
    for r in prediction['qf_results']:
        print(f"    {r['home_team']:<20} vs {r['away_team']:<20} "
              f"→ {r['winner']} ({r['method']})")

    print(f"\n  Semi Finals:")
    for r in prediction['sf_results']:
        print(f"    {r['home_team']:<20} vs {r['away_team']:<20} "
              f"→ {r['winner']} ({r['method']})")

    print(f"\n  Final:")
    r = prediction['final_result']
    print(f"    {r['home_team']} vs {r['away_team']} "
          f"→ 🏆 {r['winner']} ({r['method']})")

    # ── Team path ─────────────────────────────────────────────────────
    print_team_path('Spain', prediction)

    # ── Run Monte Carlo (small run first to test) ──────────────────────
    print("\n" + "═" * 55)
    print("  MONTE CARLO (100 simulations — test run)")
    print("═" * 55)

    mc_results = simulator.monte_carlo(n_simulations=100)

    print(f"\n  Most likely winner: {mc_results['most_likely_winner']}")
    print(f"\n  Top 10 win probabilities:")
    top10 = mc_results['probabilities'].head(10)
    for _, row in top10.iterrows():
        bar = '█' * int(row['win_prob'] * 300)
        print(f"    {row['team']:<25} "
              f"Win:{row['win_prob']*100:5.1f}%  "
              f"Final:{row['final_prob']*100:4.1f}%  "
              f"SF:{row['semi_prob']*100:4.1f}%  "
              f"{bar}")

    print("\n✅ Simulator test complete")
    return simulator, prediction, mc_results


if __name__ == "__main__":
    simulator, prediction, mc_results = main()
