import joblib

preprocessor = joblib.load("data/processed/preprocessor.joblib")
feature_names = joblib.load("data/processed/models/feature_names.joblib")

print("FIFA ranking features in model:")
ranking_feats = [f for f in feature_names if 'fifa' in f or 'rank_diff' in f]
print(ranking_feats if ranking_feats else "None — rankings not in trained model")

print(f"\nTotal features model expects: {len(feature_names)}")