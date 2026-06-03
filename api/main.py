"""
Run with:
    uvicorn api.main:app --reload --port 8000
"""

import json
import pandas as pd
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT  = Path(__file__).parent.parent
RESULTS_PATH = ROOT / "data" / "results" / "simulation_output.json"
FIXTURES_PATH = ROOT / "data" / "results" / "fixture_predictions.json"
MODEL_DIR = ROOT / "data" / "processed" / "models"
PREPROCESSOR_PATH = ROOT / "data" / "processed" / "preprocessor.joblib"

app = FastAPI(
    title="WC 2026 Predictor API",
    description="Tournament bracket predictions and Monte Carlo probabilities.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cache: dict = {
    "simulation": None,  # full export_results() output dict
    "fixtures": None,  # list from generate_fixture_predictions()
    "simulator": None,  # TournamentSimulator — loaded lazily, reused across requests
}

@asynccontextmanager
async def startup() -> None:
    if RESULTS_PATH.exists():
        with open(RESULTS_PATH, encoding="utf-8") as f:
            cache["simulation"] = json.load(f)
        print(f"[API] Loaded simulation results from {RESULTS_PATH}")
    else:
        print("[API] No cached simulation found — run export_results() to generate.")

    if FIXTURES_PATH.exists():
        with open(FIXTURES_PATH, encoding="utf-8") as f:
            cache["fixtures"] = json.load(f)
        print(f"[API] Loaded {len(cache['fixtures'])} fixture predictions from {FIXTURES_PATH}")
    else:
        print("[API] No cached fixtures found — run generate_fixture_predictions() to generate.")

@app.get("/api/status")
def get_status():
    #Health check — shows whether results are loaded.
    sim = cache["simulation"]
    return {
        "simulation_loaded": sim is not None,
        "generated_at": sim.get("generated_at") if sim else None,
        "fixtures_loaded": cache["fixtures"] is not None,
        "n_fixtures": len(cache["fixtures"]) if cache["fixtures"] else 0,
        "simulator_loaded": cache["simulator"] is not None,
    }

@app.get("/api/bracket")
def get_bracket():
    require_simulation()
    return cache["simulation"]["deterministic"]

@app.get("/api/monte-carlo")
def get_monte_carlo():
    require_simulation()
    return cache["simulation"]["monte_carlo"]

@app.get("/api/fixtures")
def get_fixtures(group: Optional[str] = None):
    """
    All 72 WC 2026 group stage fixture predictions.

    Optional query param ?group=Group+A filters to a single group.
    actual_* fields are null until real results are recorded.
    """
    require_fixtures()
    fixtures = cache["fixtures"]
    if group:
        fixtures = [f for f in fixtures if f["group"] == group]
    return {"fixtures": fixtures}

@app.get("/api/fixtures/{fixture_id}")
def get_fixture(fixture_id: str):
    """Return the prediction for a single fixture by its ID."""
    require_fixtures()
    match = next((f for f in cache["fixtures"] if f["id"] == fixture_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Fixture '{fixture_id}' not found.")
    return match

@app.post("/api/fixtures/{fixture_id}/predict")
def repredict_fixture(fixture_id: str):

    require_fixtures()

    idx = next(
        (i for i, f in enumerate(cache["fixtures"]) if f["id"] == fixture_id),
        None,
    )
    if idx is None:
        raise HTTPException(status_code=404, detail=f"Fixture '{fixture_id}' not found.")

    fixture = cache["fixtures"][idx]
    simulator = get_simulator()

    try:
        updated_preds = predict_one(simulator, fixture)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    # Merge new prediction fields into the existing fixture, preserving actual_* fields
    fixture.update(updated_preds)
    cache["fixtures"][idx] = fixture

    # Persist updated list to disk
    with open(FIXTURES_PATH, "w", encoding="utf-8") as f:
        json.dump(cache["fixtures"], f, indent=2)

    return fixture

def get_simulator():

    if cache["simulator"] is not None:
        return cache["simulator"]

    import sys
    sys.path.insert(0, str(ROOT))

    from src.pipeline import DataPipeline
    from src.feature_builder import FeatureBuilder
    from src.data_preprocessor import DataPreprocessor
    from src.models.match_predictor import MatchPredictor
    from simulate.tournament import TournamentSimulator

    print("[API] Loading pipeline and model (first use)...")
    pipeline = DataPipeline().run()
    fb = FeatureBuilder(matches=pipeline.matches, rankings=pipeline.rankings, elo=pipeline.elo)
    predictor = MatchPredictor.load(MODEL_DIR)
    preprocessor = DataPreprocessor.load(PREPROCESSOR_PATH)

    simulator = TournamentSimulator(
        predictor=predictor,
        feature_builder=fb,
        preprocessor=preprocessor,
    )
    cache["simulator"] = simulator
    print("[API] Simulator ready.")
    return simulator

def require_simulation():
    if cache["simulation"] is None:
        raise HTTPException(
            status_code=503,
            detail="No simulation data available. Generate it by running export_results().",
        )

def require_fixtures():
    if cache["fixtures"] is None:
        raise HTTPException(
            status_code=503,
            detail="No fixture data available. Generate it by running generate_fixture_predictions().",
        )

def predict_one(simulator, fixture: dict) -> dict:
    """Re-run the model for a single fixture dict and return updated prediction fields."""
    features = simulator.feature_builder.build_fixture_features(
        home_team=fixture["home_team"],
        away_team=fixture["away_team"],
        date=fixture["date"],
        neutral=True,
        city=fixture.get("city"),
    )
    X = pd.DataFrame([features])
    X, _ = simulator.preprocessor.transform(X, scale=True)
    preds = simulator.predictor.predict(X).iloc[0]

    return {
        "home_win_prob": round(float(preds["prob_home_win"]), 4),
        "draw_prob": round(float(preds["prob_draw"]), 4),
        "away_win_prob": round(float(preds["prob_away_win"]), 4),
        "predicted_outcome": str(preds["predicted_result"]),
        "predicted_home_goals": round(float(preds["predicted_home_goals"]), 2),
        "predicted_away_goals": round(float(preds["predicted_away_goals"]), 2),
        "predicted_score": str(preds["predicted_score"]),
    }