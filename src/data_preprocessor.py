import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
from sklearn.preprocessing import StandardScaler
import joblib
    
from src.config import DATA_PROCESSED
 
class DataPreprocessor:
    DROP_COLS = [
        'rank_diff',
        'points_diff',
    ]
 
    META_COLS = [
        'date', 'home_team', 'away_team',
        'tournament', 'weight'
    ]
 
    TARGET_COLS = [
        'home_score', 'away_score', 'goal_diff', 'result',
    ]
 
    ELO_CHANGE_COLS = [
        'home_elo_change_30d',  'home_elo_change_90d',
        'home_elo_change_365d', 'home_elo_change_3yr',
        'away_elo_change_30d',  'away_elo_change_90d',
        'away_elo_change_365d', 'away_elo_change_3yr',
        'elo_diff',
    ]
 
    H2H_COLS = [
        'h2h_matches',
        'h2h_team_a_wins',
        'h2h_team_b_wins',
        'h2h_draws',
        'h2h_team_a_winrate',
        'h2h_avg_goals',
    ]
 
    H2H_NEUTRAL_VALUES = {
        'h2h_matches': 0,
        'h2h_team_a_wins': 0,
        'h2h_team_b_wins': 0,
        'h2h_draws': 0,
        'h2h_team_a_winrate': 0.33, 
        'h2h_avg_goals': 2.5,   
    }
 
    RESULT_ENCODING = {
        'home_win': 0,
        'draw':     1,
        'away_win': 2,
    }
 
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_cols = None   # set after fit
        self.median_values = {}     # stored medians for ELO imputation
        self.is_fitted = False

    def fit_transform(self, df: pd.DataFrame, scale: bool = True, save_path: Optional[Path] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Call this ONLY on training data — never on test/WC fixtures.
        Returns:
            X: Feature DataFrame (scaled if scale=True)
            y: Target DataFrame with columns [result, home_score, away_score, goal_diff]
        """
        print("[DataPreprocessor] Fitting and transforming training data...")
        df = df.copy()
 
        df = self.drop_cols(df)
 
        df, dropped = self.drop_insufficient_rows(df)
        print(f"  Dropped {dropped} rows with insufficient form data")
 
        df = self.fit_impute(df)
 
        y = self.extract_targets(df)
        X = df.drop(columns=self.TARGET_COLS, errors='ignore')
 
        X = self.select_feature_cols(X)
        self.feature_cols = list(X.columns)
 
        print(f"  Features: {len(self.feature_cols)} columns")
        print(f"  Samples:  {len(X):,} rows")
        print(f"  Nulls remaining: {X.isnull().sum().sum()}")
 
        if scale:
            X = self.fit_scale(X)
 
        self.is_fitted = True
 
        if save_path:
            self.save(save_path)
 
        return X, y
 
    def transform(self, df: pd.DataFrame, scale: bool = True) -> tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Transform new data using fitted preprocessor.
        Use for test sets and WC 2026 fixture predictions.
 
        Returns:
            X: Feature DataFrame
            y: Target DataFrame if targets present, else None
        """
        if not self.is_fitted:
            raise RuntimeError("Call fit_transform() before transform()")
 
        df = df.copy()
        df = self.drop_cols(df)
        df = self.impute(df)
 
        has_targets = all(c in df.columns for c in ['result', 'home_score'])
        y = self.extract_targets(df) if has_targets else None
 
        X = df.drop(columns=self.TARGET_COLS, errors='ignore')
        X = self.align_feature_cols(X)
 
        if scale and self.scaler is not None:
            X_scaled = self.scaler.transform(X)
            X = pd.DataFrame(X_scaled, columns=self.feature_cols, index=X.index)
 
        return X, y
 
    def save(self, path: Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        print(f"[DataPreprocessor] Saved → {path}")
 
    @classmethod
    def load(cls, path: Path) -> "DataPreprocessor":
        return joblib.load(path)
 
    def drop_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop confirmed useless columns."""
        return df.drop(
            columns=[c for c in self.DROP_COLS if c in df.columns],
            errors='ignore'
        )
 
    def drop_insufficient_rows(self, df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
        # Drop rows where ANY form feature is null or below 3 matches total
        form_cols = [c for c in df.columns if any(
            kw in c for kw in [
                'form_points_per_game', 'form_wins', 'form_draws',
                'form_losses', 'form_win_rate', 'avg_goals_scored',
                'avg_goals_conceded', 'avg_goal_diff',
                'wavg_goals_scored', 'wavg_goals_conceded',
                'form_matches_available', 'form_diff',
                'goals_scored_diff', 'goals_conceded_diff',
            ]
        )]

        if not form_cols:
            return df, 0

        mask = df[form_cols].isnull().any(axis=1)
        dropped = mask.sum()
        return df[~mask].reset_index(drop=True), dropped
 
    def fit_impute(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.ELO_CHANGE_COLS:
            if col in df.columns:
                df[col] = df[col].fillna(0)

        elo_base_cols = [
            c for c in df.columns
            if 'elo' in c and c not in self.ELO_CHANGE_COLS
            and 'change' not in c
        ]
        for col in elo_base_cols:
            median = df[col].median()
            self.median_values[col] = median
            df[col] = df[col].fillna(median)
 
        rate_cols = [c for c in df.columns if '_rate' in c]
        for col in rate_cols:
            median = df[col].median()
            self.median_values[col] = median
            df[col] = df[col].fillna(median)
 
        goals_cols = [
            c for c in df.columns
            if 'goals_per_game' in c or 'conceded_per_game' in c
            or 'matches_played' in c
        ]
        for col in goals_cols:
            median = df[col].median()
            self.median_values[col] = median
            df[col] = df[col].fillna(median)
 
        for col, val in self.H2H_NEUTRAL_VALUES.items():
            if col in df.columns:
                df[col] = df[col].fillna(val)
            # Encode neutral as integer (True=1, False=0)
        if 'neutral' in df.columns:
            df['neutral'] = df['neutral'].astype(int)
 
        return df
 
    def impute(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.ELO_CHANGE_COLS:
            if col in df.columns:
                df[col] = df[col].fillna(0)
 
        for col, median in self.median_values.items():
            if col in df.columns:
                df[col] = df[col].fillna(median)
 
        for col, val in self.H2H_NEUTRAL_VALUES.items():
            if col in df.columns:
                df[col] = df[col].fillna(val)
                
        if 'neutral' in df.columns:
            df['neutral'] = df['neutral'].astype(int)
 
        return df
 
    def extract_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        y = df[
            [c for c in self.TARGET_COLS if c in df.columns]
        ].copy()
 
        if 'result' in y.columns:
            y['result_encoded'] = y['result'].map(self.RESULT_ENCODING)
 
        return y
 
    def select_feature_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        exclude = set(self.META_COLS + self.TARGET_COLS + self.DROP_COLS)
        cols    = [
            c for c in df.columns
            if c not in exclude
            and pd.api.types.is_numeric_dtype(df[c])
        ]
        return df[cols]
 
    def align_feature_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.feature_cols:
            if col not in df.columns:
                df[col] = 0
                print(f"  ⚠️  Missing feature '{col}' filled with 0")
 
        return df[self.feature_cols]
 
    def fit_scale(self, X: pd.DataFrame) -> pd.DataFrame:
        scaled = self.scaler.fit_transform(X)
        return pd.DataFrame(scaled, columns=X.columns, index=X.index)
 
 
    def summary(self) -> dict:
        if not self.is_fitted:
            return {"status": "not fitted"}
        return {
            "features":         len(self.feature_cols),
            "feature_names":    self.feature_cols,
            "imputed_medians":  len(self.median_values),
            "result_encoding":  self.RESULT_ENCODING,
        }
