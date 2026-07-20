# World Cup 2026 ML Predictor

A full-stack machine learning project that predicts the 2026 FIFA World Cup: every group-stage fixture, the full knockout bracket, and each nation's probability of lifting the trophy.

Built end-to-end (May 26 – June 10, 2026) as a linear pipeline:

**Data Collection → Cleaning → Feature Engineering → Model Training → Evaluation → Tournament Simulation → React UI → AWS Deployment**

---

## 1. Data Collection

Three data sources feed the model, each behind its own loader so one failing source never blocks the others (`src/pipeline.py` → `DataPipeline`, loaders in `data/classes/`).

| Source | Contents | Method |
|---|---|---|
| Match history | 49,288 international results, 1872–present (`data/raw/results.csv`) | Curated CSV of every international match played |
| Elo ratings | ~244 nations, 31 rating columns (`data/raw/elo_ratings.tsv`) | Downloaded from eloratings.net's TSV endpoint, cached locally |
| FIFA rankings | ~212 snapshots, 2021–2026 (`data/raw/fifa_rankings_scraped.csv`) | Scraped with Playwright — a headless browser intercepts the JSON the ranking page fetches internally |

FIFA publishes no downloadable ranking dataset, so the scraper drives a headless browser and captures the internal API responses. All sources are cached after first fetch; re-fetching requires `force_reload=True`.

## 2. Cleaning & Preparation

`src/data_preprocessor.py` handles the ways international football data is messy:

- **Recency filter** — Training starts at **2021-01-01**, keeping **5,529 matches** (47.7% home wins, 22.9% draws, 29.4% away wins). Older data adds noise, not signal.
- **Name normalization** — Variants like "USA" / "United States" / "United States of America" collapse to one canonical name. All 48 qualified teams join cleanly across all three sources.
- **Missing values (per feature type)** — Elo momentum gaps → 0; base ratings → training-set medians (stored for identical test imputation); head-to-head gaps → neutral priors (0.33 win rate, 2.5 avg goals); rows with fewer than 3 prior matches → dropped.
- **Sample weighting** — Matches are weighted by importance, from 4.0 (World Cup) to 0.5 (friendlies), so competitive results influence the model more.
- **Scaling** — StandardScaler fit on training data only, saved to `preprocessor.joblib` for reuse at prediction time.

## 3. Feature Engineering

`src/feature_builder.py` converts each match into **61 numeric features** in five families:

1. **Strength** — Current/peak Elo, Elo a year ago, Elo momentum (30/90/365 days, 3 years), FIFA rank and points, for both teams.
2. **Form** — Rolling 10-match window: weighted points per game, win rate, goals for/against, goal difference.
3. **Head-to-head** — Last 10 meetings between the two teams: result split, win rate, average total goals.
4. **Differentials** — `elo_diff`, `form_diff`, goals-for/against diffs, so the model sees relative strength directly.
5. **Context** — Neutral-venue flag. Host nations (USA, Mexico, Canada) get `neutral=0` on home soil; otherwise the higher-Elo team is labeled "home" with `neutral=1`.

**Output:** `training_features.parquet` — 5,221 rows × 72 columns (61 features + metadata/targets).

## 4. Model Training

Three models (`src/models/match_predictor.py`), each with a distinct job:

- **XGBoost classifier** → P(home win / draw / away win). Tuned conservatively for a noisy domain: 300 trees at depth 3, learning rate 0.05, L1 + L2 + gamma regularization, row/feature subsampling (70% / 60%), balanced class weights, early stopping after 30 stale rounds. Outputs calibrated probabilities (`multi:softprob`), which the simulation depends on.
- **Two Poisson regressors** → expected home and away goals. Poisson fits count data like goals.
- **Logistic regression baseline** → the control. If XGBoost can't beat it, the features aren't adding value.

**Temporal split, not random:** train on matches before 2025, validate on 2025, test on 2026. A random split would leak future form into past predictions and inflate the metrics.

## 5. Evaluation

Held-out validation results (`data/processed/models/metrics.joblib`):

| Metric | Baseline | XGBoost |
|---|---|---|
| Accuracy | 56.0% | **59.2%** |
| Log loss | — | 0.896 |
| Ranked Probability Score | — | **0.176** |
| Goals MAE | — | 0.92–1.09 |

Three-way football outcomes are hard — bookmakers sit around 60% — so 59.2% with a +3.2-point edge over the baseline confirms the features carry signal. RPS matters most here, since the simulation consumes probabilities rather than picks, and 0.176 indicates well-calibrated ones. A validation notebook (`notebooks/load_match_data_check.ipynb`) spot-checks the pipeline against known results, including the 2022 final (Argentina 3–3 France).

## 6. Tournament Simulation

`simulate/tournament.py` runs the full 48-team, 12-group 2026 format — 72 group fixtures, then Round of 32 through the final — in two modes:

- **Deterministic** — One most-likely bracket. Each match takes its argmax outcome and score; group standings resolve via the official FIFA 2026 tiebreaker cascade (points → goal difference → goals scored → head-to-head → drawing of lots).
- **Monte Carlo** — 1,000 full tournament simulations. Each outcome is *sampled* from the classifier's distribution and goals from Poisson; drawn knockout games go to simulated extra time and penalties. Aggregating the runs yields each team's probability of winning the cup, reaching the final, the semis, and so on.

`scripts/generate_results.py` exports two JSON files that form the contract with the frontend:
- `simulation_output.json` — the bracket plus Monte Carlo probabilities
- `fixture_predictions.json` — all 72 group fixtures with odds and predicted scores, plus `actual_*` fields for recording real results as they happen

## 7. Application

- **API** (`worldcup_predictor/api/main.py`) — FastAPI with five endpoints (`/api/status`, `/api/bracket`, `/api/monte-carlo`, `/api/fixtures` with group filtering, `/api/fixtures/{id}`), all served from the pre-computed JSONs cached in memory at startup.
- **UI** (`frontend/`) — React 19 + Vite with React Router, Tailwind, Framer Motion, and a Spline 3D hero. Renders the full bracket, per-group fixtures with probability bars, and Monte Carlo standings, and lets you enter actual results as games are played.

## 8. Deployment

Deployed to AWS at near-zero cost, sized for a low-traffic personal project. The whole stack is defined as code in one SAM template (`template.yaml`).

```
React SPA ── S3 bucket (private)
                │  Origin Access Control
                ▼
          CloudFront CDN ──► users (HTTPS, edge-cached)

React fetch ──► API Gateway (HTTP API) ──► Lambda (FastAPI via Mangum)
                                              └─ bundled JSONs, cached in memory
```

- **SPA routing** — Deep links like `/predictions` aren't S3 objects, so CloudFront rewrites 403/404 to `/index.html` (200) and lets React Router take over. (403 because a locked-down bucket returns 403, not 404, for missing keys.)
- **Caching** — Content-hashed assets are cached a year as immutable; `index.html` is never cached and gets a CloudFront invalidation on every deploy, so releases are instant and repeat visits fast.
- **CORS** — The API's allowed origin is set to the CloudFront domain via a stack parameter, not hardcoded.
- **Releases** — Deploy scripts stage the JSONs, build, and push the stack / sync S3 / invalidate the CDN. Updating predictions mid-tournament is: regenerate JSONs, run one script.

**Cost:** Lambda, API Gateway, and CloudFront free tiers cover this traffic; S3 for a ~5MB site rounds to $0.

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
├── frontend/            # React 19 + Vite SPA
├── worldcup_predictor/
│   ├── api/             # FastAPI app (the Lambda)
│   ├── src/             # Pipeline, preprocessing, features, models
│   ├── data/            # raw / processed / results + loader classes
│   ├── simulate/        # Group stage + knockout simulators
│   ├── trainings/       # Model training scripts
│   ├── scripts/         # Result generation
│   ├── notebooks/       # Data validation
│   └── tests/
└── template.yaml        # SAM stack: Lambda, API Gateway, S3, CloudFront
```
