"""
Run with:
    uvicorn api.main:app --reload --port 8000
"""

import json
import os
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Data lives at ../data/results when running from the repo, and at
# ./data/results when bundled for Lambda (/var/task). Repo layout is checked
# first so a leftover staged copy never shadows live data locally.
_HERE = Path(__file__).parent
_CANDIDATES = [_HERE.parent / "data" / "results", _HERE / "data" / "results"]
DATA_DIR = next((p for p in _CANDIDATES if p.exists()), _CANDIDATES[0])
RESULTS_PATH = DATA_DIR / "simulation_output.json"
FIXTURES_PATH = DATA_DIR / "fixture_predictions.json"

cache: dict = {
    "simulation": None,
    "fixtures": None,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
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

    yield

app = FastAPI(
    title="WC 2026 Predictor API",
    description="Tournament bracket predictions and Monte Carlo probabilities.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
def get_status():
    #Health check — shows whether results are loaded.
    sim = cache["simulation"]
    return {
        "simulation_loaded": sim is not None,
        "generated_at": sim.get("generated_at") if sim else None,
        "fixtures_loaded": cache["fixtures"] is not None,
        "n_fixtures": len(cache["fixtures"]) if cache["fixtures"] else 0,
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

from mangum import Mangum
handler = Mangum(app)