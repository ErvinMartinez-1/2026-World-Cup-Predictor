import pandas as pd

df = pd.read_parquet("data/processed/training_features.parquet")
test_df = df[df['date'] >= '2026-01-01']

print("Completed matches result distribution:")
print(test_df[test_df['home_score'].notna()]['result'].value_counts())

print("\nFuture matches result distribution:")
print(test_df[test_df['home_score'].isna()]['result'].value_counts())

print("\nSample future matches:")
print(test_df[test_df['home_score'].isna()][
    ['date','home_team','away_team','result','home_score','away_score']
].head(10).to_string())