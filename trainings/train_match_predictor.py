import pandas as pd
import numpy as np
from pathlib import Path

from src.data_preprocessor import DataPreprocessor
from worldcup_predictor.src.models.match_predictor import MatchPredictor

FEATURES_PATH = Path("data/processed/training_features.parquet")
PREPROCESSOR_PATH = Path("data/processed/preprocessor.joblib")
MODELS_DIR = Path("data/processed/models")


VAL_START = "2025-01-01"
TEST_START = "2026-01-01"


def main():

    # Step 1: Load feature table
    print("Loading feature table...")
    df = pd.read_parquet(FEATURES_PATH)
    df['date'] = pd.to_datetime(df['date'])
    print(f"  Total rows: {len(df):,}")
    print(f"  Date range: {df['date'].min().date()} → {df['date'].max().date()}")

    # Step 2: Time-based split
    train_df = df[df['date'] <  VAL_START].copy()
    val_df = df[(df['date'] >= VAL_START) & (df['date'] <  TEST_START)].copy()
    test_df = df[df['date'] >= TEST_START].copy()

    completed_train_df = train_df[train_df['home_score'].notna()].copy()
    completed_val_df = val_df[val_df['home_score'].notna()].copy()
    completed_test_df = test_df[test_df['home_score'].notna()].copy()
    future_df  = test_df[test_df['home_score'].isna()].copy()

    print(f"\nTime-based split (completed matches only):")
    print(f"  Train: {len(completed_train_df):,} matches")
    print(f"  Val:   {len(completed_val_df):,} matches")
    print(f"  Test:  {len(completed_test_df):,} matches")
    print(f"  WC 2026 future fixtures: {len(future_df)}")

    # Step 3: Preprocess each split
    print("\nPreprocessing splits...")
    preprocessor = DataPreprocessor()

    X_train, y_train = preprocessor.fit_transform(
        completed_train_df,
        scale=True,
        save_path=PREPROCESSOR_PATH
    )
    X_val,  y_val = preprocessor.transform(completed_val_df,  scale=True)
    X_test, y_test = preprocessor.transform(completed_test_df, scale=True)

    print(f"\n  X_train: {X_train.shape}")
    print(f"  X_val:   {X_val.shape}")
    print(f"  X_test:  {X_test.shape}")

    # Check for any remaining nulls
    for name, X in [('train', X_train), ('val', X_val), ('test', X_test)]:
        nulls = X.isnull().sum().sum()
        if nulls > 0:
            print(f"  ⚠️  {name} has {nulls} null values remaining")
        else:
            print(f"  ✅ {name}: zero nulls")

    # Step 4: Train model
    predictor = MatchPredictor()
    predictor.train(X_train, y_train, X_val, y_val)

    # Step 5: Final evaluation on test set
    test_metrics = predictor.evaluate(X_test, y_test, label="Test")

    # Step 6: Compare XGBoost vs baseline
    print("\n── Model Comparison ──")
    print(f"  {'Metric':<20} {'Baseline':>10} {'XGBoost':>10} {'Δ':>8}")
    print(f"  {'─'*20} {'─'*10} {'─'*10} {'─'*8}")

    baseline_acc = predictor.val_metrics_['baseline_accuracy']
    xgb_acc = predictor.val_metrics_['xgb_accuracy']
    delta  = xgb_acc - baseline_acc

    print(f"  {'Val Accuracy':<20} {baseline_acc:>10.4f} {xgb_acc:>10.4f} "
          f"{'↑' if delta > 0 else '↓'}{abs(delta):>6.4f}")

    baseline_f1 = predictor.val_metrics_['baseline_f1']
    xgb_f1  = predictor.val_metrics_['xgb_f1']
    delta_f1  = xgb_f1 - baseline_f1

    print(f"  {'Val F1':<20} {baseline_f1:>10.4f} {xgb_f1:>10.4f} "
          f"{'↑' if delta_f1 > 0 else '↓'}{abs(delta_f1):>6.4f}")


    predictor.save(MODELS_DIR)

    print("  Training complete!")
    print(f"  Models saved → {MODELS_DIR}")
    print("═" * 55)

    return predictor, preprocessor


if __name__ == "__main__":
    predictor, preprocessor = main()