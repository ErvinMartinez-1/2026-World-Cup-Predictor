# World Cup 2026 ML Predictor

A full-stack machine learning project that predicts the 2026 FIFA World Cup — every group-stage fixture, the full knockout bracket, and each nation's probability of lifting the trophy — served live at [d2ys6sqftyll1d.cloudfront.net](https://d2ys6sqftyll1d.cloudfront.net).

Built end-to-end in under three weeks (May 26 – June 10, 2026): data scraping → feature engineering → model training → tournament simulation → React UI → AWS deployment. This document tells that story.

---

## 1. Data Collection

Three independent data sources feed the model, each with its own loader class so a failure in one never blocks the others (`src/pipeline.py` → `DataPipeline` orchestrating `MatchLoader`, `EloLoader`, `Ranking`):

| Source | What | How it's collected |
|---|---|---|
| Match history | 49,288 international results, 1872 → present (`data/raw/results.csv`) | Curated CSV of every international match ever played |
| Elo ratings | ~244 nations, 31 columns of rating data (`data/raw/elo_ratings.tsv`) | Downloaded from eloratings.net's TSV endpoint, cached locally |
| FIFA rankings | ~212 ranking snapshots, 2021–2026 (`data/raw/fifa_rankings_scraped.csv`) | **Scraped with Playwright** — async browser automation that intercepts the API responses behind FIFA's ranking page DOM |

The scraper was the first real engineering challenge of the project: FIFA's rankings aren't published as a downloadable dataset, so the loader drives a headless browser and captures the JSON the page requests internally. Everything is cached after first fetch — re-scraping only happens with `force_reload=True`.

## 2. Cleaning & Preparation

Raw international football data is messy in specific ways, and the cleaning layer (`src/data_preprocessor.py`) addresses each:

- **Recency filter** — 150 years of matches is mostly noise for predicting 2026. Training data starts at **2021-01-01**, leaving **5,529 matches** (47.7% home wins, 22.9% draws, 29.4% away wins — the home-advantage skew the model must learn).
- **Country-name normalization** — "USA" vs "United States" vs "United States of America" across three sources mapped to one canonical name; all 48 qualified teams verified to join cleanly across all sources.
- **Missing-value strategy, by feature type**: Elo momentum gaps filled with 0 (no change), base ratings with training-set medians (stored so test data is imputed identically), head-to-head gaps with neutral priors (0.33 win rate, 2.5 avg goals), and rows lacking enough history for form features (< 3 prior matches) dropped outright.
- **Tournament weighting** — a World Cup match teaches the model more than a friendly. Sample weights range from 4.0 (World Cup) through 3.5 (Euros/Copa América) down to 0.5 (friendlies).
- **Scaling** — StandardScaler fit on training data only, persisted to `preprocessor.joblib` so the exact same transform applies at prediction time.

## 3. Feature Engineering

`src/feature_builder.py` turns each match into **61 numeric features** across five families:

1. **Strength ratings** — current Elo, peak Elo, Elo a year ago, and momentum over 30/90/365 days and 3 years, plus FIFA rank and points — for both teams.
2. **Form** — rolling 10-match window: points per game (tournament-weighted), win rate, goals scored/conceded, goal difference.
3. **Head-to-head** — last 10 meetings between the two specific teams: results split, win rate, average total goals.
4. **Comparative differentials** — `elo_diff`, `form_diff`, goals scored/conceded diffs, so the model sees relative strength directly rather than inferring it.
5. **Match context** — neutral-venue flag, with 2026-specific logic: host nations (USA, Mexico, Canada) playing on home soil get `neutral=0`; for everyone else at this World Cup the higher-Elo team is designated "home" with `neutral=1`.

**Output:** `training_features.parquet`, 5,221 rows × 72 columns (61 features + metadata/targets).

## 4. Model & Training

Three models, each with a distinct job (`src/models/match_predictor.py`):

- **XGBoost classifier** → P(home win / draw / away win). Deliberately conservative architecture for a noisy domain: 300 trees but only depth 3, learning rate 0.05, heavy regularization (L1 + L2 + gamma), subsampling of both rows (70%) and features (60%), balanced class weights, early stopping after 30 stale rounds. Outputs calibrated probabilities (`multi:softprob`), not just labels — the simulation layer depends on that.
- **Two Poisson Regressors** → expected home and away goals. Goals are count data; Poisson is the statistically honest choice.
- **Logistic Regression baseline** → the control. If XGBoost can't beat plain logistic regression, the features aren't earning their keep.

**The split is temporal, not random** — the most important methodological decision in the project. Training on matches before 2025, validating on 2025, testing on 2026. A random split would leak future information (a team's late-2025 form would inform predictions about early-2025 matches) and produce flattering but fake metrics.

## 5. Testing & Evaluation

Held-out validation results (`data/processed/models/metrics.joblib`):

| Metric | Baseline | XGBoost |
|---|---|---|
| Accuracy | 56.0% | **59.2%** |
| Log loss | — | 0.896 |
| Ranked Probability Score | — | **0.176** |
| Goals MAE | — | 0.92–1.09 |

Three-way football outcomes are genuinely hard — bookmakers operate around 60% — so 59.2% with a +3.2-point edge over the baseline confirmed the feature set carries real signal. RPS (the football-forecasting standard, which rewards *well-calibrated probabilities* rather than lucky picks) at 0.176 was the number that mattered most, since the Monte Carlo simulation consumes probabilities, not classifications.

One bug from this phase made it into the git history (June 4): naively rounding Poisson goal expectations collapsed most group games into identical 1-1 draws. The fix was a most-likely-score function that respects the predicted outcome — if the classifier says home win, the scoreline sampling can't contradict it.

A data-validation notebook (`notebooks/load_match_data_check.ipynb`) sanity-checks the pipeline against known ground truth — including spot-checking the 2022 final (Argentina 3-3 France).

## 6. Simulating the Tournament

`simulate/tournament.py` runs the full 48-team, 12-group 2026 format — 72 group fixtures, then Round of 32 through the final — in two modes:

- **Deterministic**: one most-likely bracket. Every match takes its argmax outcome and most-likely score. Group standings resolve with the real FIFA 2026 tiebreaker cascade (points → goal difference → goals scored → head-to-head → drawing of lots).
- **Monte Carlo**: 1,000 complete tournament simulations. Each match outcome is *sampled* from the classifier's probability distribution, goals from Poisson; drawn knockout games resolve through simulated extra time and a shot-by-shot penalty shootout. Aggregating 1,000 parallel universes yields each team's probability of winning the cup, reaching the final, the semis, and so on.

`scripts/generate_results.py` exports both into two JSON files — `simulation_output.json` (the bracket + probabilities) and `fixture_predictions.json` (all 72 group fixtures with odds and predicted scores, plus `actual_*` fields for recording real results as the tournament unfolds). These two files are the contract between the ML world and everything downstream.

## 7. The Application

- **API** (`worldcup_predictor/api/main.py`): FastAPI serving five endpoints — `/api/status`, `/api/bracket`, `/api/monte-carlo`, `/api/fixtures` (with group filtering), `/api/fixtures/{id}` — all reading from the pre-computed JSONs, cached in memory at startup.
- **UI** (`frontend/`): React 19 + Vite, with React Router, Tailwind, Framer Motion, and a Spline 3D hero. The predictions page renders the full bracket, per-group fixtures with probability bars, Monte Carlo standings, and supports manually entering actual results as games are played.

## 8. Deployment

**Goal**: Real cloud deployment at effectively zero cost, sized honestly for a low-traffic personal project while gaining familiarity with AWS services.


**Architecture** — defined entirely as code in one SAM template (`template.yaml`):

```
React SPA ── S3 bucket (fully private)
                │  Origin Access Control
                ▼
          CloudFront CDN ──► users (HTTPS, edge-cached)

React fetch ──► API Gateway (HTTP API) ──► Lambda (FastAPI via Mangum)
                                              └─ bundled JSONs, cached in memory
```

**Details:**

- **SPA routing on a CDN**: deep links like `/predictions` don't exist as S3 objects. CloudFront maps 403/404 errors to `/index.html` (200), letting React Router take over. (403, not just 404 — a locked-down bucket without `ListBucket` returns 403 for missing keys.)
- **Cache strategy**: Vite's content-hashed assets are cached for a year as immutable; `index.html` is never cached and gets a CloudFront invalidation on every deploy. New releases are instant, repeat visits are fast.
- **CORS hardening**: after launch, the API's allowed origin was tightened from `*` to the CloudFront domain via a stack parameter — config, not code.
- **Repeatable releases**: Frontend deployment scripts (stages JSONs → builds → deploys the stack) and Backend logic deployment scripts (builds → syncs S3 → invalidates CDN). Updating predictions during the tournament is: regenerate JSONs locally, run one script.

**Cost**: Lambda and API Gateway free tiers cover this traffic indefinitely; CloudFront's always-free tier (1TB/month) covers serving; S3 storage for a 5MB site rounds to $0.

---

## Running It

```powershell
# API (from worldcup_predictor/)
uvicorn api.main:app --reload --port 8000

# UI (from frontend/) — dev server proxies /api to :8000
npm run dev

# Regenerate predictions
python -X utf8 scripts/generate_results.py

```

## Project Structure

```
world_cup_ML/
├── frontend/      # React 19 + Vite SPA
├── worldcup_predictor/
│   ├── api/       # FastAPI app (the Lambda)
│   ├── src/       # Pipeline, features, preprocessing, models
│   ├── simulate/  # Group stage + knockout simulators
│   ├── trainings/ # Model training scripts
│   ├── scripts/   # Result generation
│   ├── data/      # raw / processed / results
│   ├── notebooks/ # Data validation
│   └── tests/
├── template.yaml  # SAM stack: Lambda, API Gateway, S3, 
                                CloudFront

```
