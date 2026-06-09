from src.pipeline import DataPipeline
from src.feature_builder import FeatureBuilder
from pathlib import Path

# ── Load pipeline ──
pipeline = DataPipeline().run()

# ── Initialise FeatureBuilder ──
fb = FeatureBuilder(
    matches=pipeline.matches,
    rankings=pipeline.rankings,
    elo=pipeline.elo,
)

# ── Build training set ──
train_df = fb.build_training_set(
    save_path=Path("data/processed/training_features.parquet")
)

# ── Inspect output ──
print("\n=== TRAINING SET OVERVIEW ===")
print(f"Shape:    {train_df.shape}")
print(f"Columns:  {list(train_df.columns)}")

print("\n=== NULL COUNTS (features only) ===")
feature_cols = [c for c in train_df.columns
                if c not in ['date','home_team','away_team',
                             'tournament','weight','neutral',
                             'home_score','away_score',
                             'goal_diff','result']]
null_pct = (train_df[feature_cols].isnull().sum() / len(train_df) * 100)
print(null_pct[null_pct > 0].sort_values(ascending=False).to_string())

print("\n=== TARGET DISTRIBUTION ===")
print(train_df['result'].value_counts())

print("\n=== SAMPLE ROW ===")
print(train_df.iloc[0].to_string())