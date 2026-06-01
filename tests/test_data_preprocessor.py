# test_preprocessor.py
from pathlib import Path
import pandas as pd
from src.data_preprocessor import DataPreprocessor

train_df = pd.read_parquet("data/processed/training_features.parquet")

# ── Fit and transform ──
preprocessor = DataPreprocessor()
X, y = preprocessor.fit_transform(
    train_df,
    scale=True,
    save_path=Path("data/processed/preprocessor.joblib")
)

print("\n=== PREPROCESSOR OUTPUT ===")
print(f"X shape:       {X.shape}")
print(f"y shape:       {y.shape}")
print(f"Nulls in X:    {X.isnull().sum().sum()}")
print(f"\nFeatures ({len(preprocessor.feature_cols)}):")
print(preprocessor.feature_cols)
print(f"\nTarget distribution:")
print(y['result'].value_counts())
print(f"\nEncoded target distribution:")
print(y['result_encoded'].value_counts().sort_index())