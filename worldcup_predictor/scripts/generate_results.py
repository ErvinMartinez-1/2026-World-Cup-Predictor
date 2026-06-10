"""
Runs the full WC 2026 prediction pipeline and writes two files:
  data/results/simulation_output.json — deterministic bracket + 1000-run MC
  data/results/fixture_predictions.json — all 72 group stage predictions

Run from the worldcup_predictor directory:
    python -X utf8 scripts/generate_results.py
"""

import json
from pathlib import Path

from src.pipeline import DataPipeline
from src.feature_builder import FeatureBuilder
from src.data_preprocessor import DataPreprocessor
from src.models.match_predictor import MatchPredictor
from worldcup_predictor.simulate.tournament import TournamentSimulator

N_SIMULATIONS = 1000

# Load data and model 
print("Loading pipeline...")
pipeline = DataPipeline().run()

fb = FeatureBuilder(
    matches=pipeline.matches,
    rankings=pipeline.rankings,
    elo=pipeline.elo,
)

print("Loading model...")
predictor = MatchPredictor.load(Path("data/processed/models"))
preprocessor = DataPreprocessor.load(Path("data/processed/preprocessor.joblib"))

simulator = TournamentSimulator(
    predictor=predictor,
    feature_builder=fb,
    preprocessor=preprocessor,
)

# Deterministic prediction
print("\nRunning deterministic prediction...")
prediction = simulator.predict()

# Monte Carlo 
print(f"\nRunning Monte Carlo ({N_SIMULATIONS:,} simulations)...")
mc_results = simulator.monte_carlo(n_simulations=N_SIMULATIONS)

# Export bracket + MC to JSON 
simulator.export_results(prediction, mc_results)

# Generate fixture predictions 
print("\nGenerating group stage fixture predictions...")
fixtures = simulator.generate_fixture_predictions()

out_path = Path("data/results/fixture_predictions.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(fixtures, f, indent=2)

print(f"\n  Fixture predictions saved ({len(fixtures)} fixtures) → {out_path}")
print("\nDone. Both JSON files are ready in data/results/")
