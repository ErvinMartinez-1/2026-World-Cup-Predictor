import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
from sklearn.preprocessing import StandardScaler
import joblib
 
from config import DATA_PROCESSED
 
 
class DataPreprocessor:
    """
    Phase 2b: Prepares the raw feature table for model training.
 
    Handles:
      - Dropping leaky / useless columns
      - Imputing nulls with appropriate strategies per feature group
      - Dropping rows with insufficient data
      - Scaling numerical features
      - Encoding target variable
 
    Usage:
        preprocessor = DataPreprocessor()
        X_train, y_train = preprocessor.fit_transform(train_df)
        X_wc,    _       = preprocessor.transform(wc_fixtures_df)
    """
 
    # ── Columns to drop entirely ──────────────────────────────────────────
 
    # Confirmed 100% null — no ranking history
    DROP_COLS = [
        'rank_diff',
        'points_diff',
    ]
 
    # Metadata — not features
    META_COLS = [
        'date', 'home_team', 'away_team',
        'tournament', 'weight', 'neutral',
    ]
 
    # Target columns — separated out before training
    TARGET_COLS = [
        'home_score', 'away_score', 'goal_diff', 'result',
    ]
 
    # ── Imputation strategies per feature group ───────────────────────────
 
    # ELO change columns — NaN means no change recorded → impute with 0
    ELO_CHANGE_COLS = [
        'home_elo_change_30d',  'home_elo_change_90d',
        'home_elo_change_365d', 'home_elo_change_3yr',
        'away_elo_change_30d',  'away_elo_change_90d',
        'away_elo_change_365d', 'away_elo_change_3yr',
        'elo_diff',
    ]
 
    # H2H columns — NaN means no prior meeting → impute with neutral values
    H2H_COLS = [
        'h2h_matches',
        'h2h_team_a_wins',
        'h2h_team_b_wins',
        'h2h_draws',
        'h2h_team_a_winrate',
        'h2h_avg_goals',
    ]
 
    H2H_NEUTRAL_VALUES = {
        'h2h_matches':        0,
        'h2h_team_a_wins':    0,
        'h2h_team_b_wins':    0,
        'h2h_draws':          0,
        'h2h_team_a_winrate': 0.33,  # neutral — no advantage
        'h2h_avg_goals':      2.5,   # global average goals per match
    }
 
    # Result encoding for classification model
    RESULT_ENCODING = {
        'home_win': 0,
        'draw':     1,
        'away_win': 2,
    }
 
    def __init__(self):
        self.scaler          = StandardScaler()
        self.feature_cols_   = None   # set after fit
        self.median_values_  = {}     # stored medians for ELO imputation
        self.is_fitted_      = False
 
    # ═══════════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════════════════
 
    def fit_transform(
        self,
        df:         pd.DataFrame,
        scale:      bool = True,
        save_path:  Optional[Path] = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fit the preprocessor on training data and transform it.
        Call this ONLY on training data — never on test/WC fixtures.
 
        Returns:
            X: Feature DataFrame (scaled if scale=True)
            y: Target DataFrame with columns [result, home_score,
                                              away_score, goal_diff]
        """
        print("[DataPreprocessor] Fitting and transforming training data...")
        df = df.copy()
 
        # ── Step 1: Drop useless columns ──
        df = self._drop_cols(df)
 
        # ── Step 2: Drop rows with missing form data ──
        df, dropped = self._drop_insufficient_rows(df)
        print(f"  Dropped {dropped} rows with insufficient form data")
 
        # ── Step 3: Impute nulls ──
        df = self._fit_impute(df)
 
        # ── Step 4: Separate targets ──
        y = self._extract_targets(df)
        X = df.drop(columns=self.TARGET_COLS, errors='ignore')
 
        # ── Step 5: Keep only numeric feature columns ──
        X = self._select_feature_cols(X)
        self.feature_cols_ = list(X.columns)
 
        print(f"  Features: {len(self.feature_cols_)} columns")
        print(f"  Samples:  {len(X):,} rows")
        print(f"  Nulls remaining: {X.isnull().sum().sum()}")
 
        # ── Step 6: Scale ──
        if scale:
            X = self._fit_scale(X)
 
        self.is_fitted_ = True
 
        if save_path:
            self.save(save_path)
 
        return X, y
 
    def transform(
        self,
        df:    pd.DataFrame,
        scale: bool = True,
    ) -> tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Transform new data using fitted preprocessor.
        Use for test sets and WC 2026 fixture predictions.
 
        Returns:
            X: Feature DataFrame
            y: Target DataFrame if targets present, else None
        """
        if not self.is_fitted_:
            raise RuntimeError("Call fit_transform() before transform()")
 
        df = df.copy()
        df = self._drop_cols(df)
        df = self._impute(df)
 
        # Extract targets if present
        has_targets = all(c in df.columns for c in ['result', 'home_score'])
        y = self._extract_targets(df) if has_targets else None
 
        X = df.drop(columns=self.TARGET_COLS, errors='ignore')
        X = self._align_feature_cols(X)
 
        if scale and self.scaler is not None:
            X_scaled = self.scaler.transform(X)
            X = pd.DataFrame(X_scaled, columns=self.feature_cols_, index=X.index)
 
        return X, y
 
    def save(self, path: Path):
        """Save fitted preprocessor to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        print(f"[DataPreprocessor] Saved → {path}")
 
    @classmethod
    def load(cls, path: Path) -> "DataPreprocessor":
        """Load a fitted preprocessor from disk."""
        return joblib.load(path)
 
    # ═══════════════════════════════════════════════════════════════════════
    # INTERNAL STEPS
    # ═══════════════════════════════════════════════════════════════════════
 
    def _drop_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop confirmed useless columns."""
        return df.drop(
            columns=[c for c in self.DROP_COLS if c in df.columns],
            errors='ignore'
        )
 
    def _drop_insufficient_rows(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, int]:
        """
        Drop rows where form features are all null.
        These are early matches with < MIN_MATCHES_FOR_FORM history.
        ~1.4% of rows based on null analysis.
        """
        form_cols = [c for c in df.columns if 'form_points_per_game' in c]
        if not form_cols:
            return df, 0
 
        # Drop only if ALL form columns are null (completely missing)
        mask    = df[form_cols].isnull().all(axis=1)
        dropped = mask.sum()
        return df[~mask].reset_index(drop=True), dropped
 
    def _fit_impute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit imputation values on training data then apply them.
        Stores medians so transform() uses the same values.
        """
        # ELO change cols → impute with 0 (no change)
        for col in self.ELO_CHANGE_COLS:
            if col in df.columns:
                df[col] = df[col].fillna(0)
 
        # ELO base cols → impute with median (fitted on train)
        elo_base_cols = [
            c for c in df.columns
            if 'elo' in c and c not in self.ELO_CHANGE_COLS
            and 'change' not in c
        ]
        for col in elo_base_cols:
            median = df[col].median()
            self.median_values_[col] = median
            df[col] = df[col].fillna(median)
 
        # Win/draw/loss rates → impute with median
        rate_cols = [c for c in df.columns if '_rate' in c]
        for col in rate_cols:
            median = df[col].median()
            self.median_values_[col] = median
            df[col] = df[col].fillna(median)
 
        # Goals per game → impute with median
        goals_cols = [
            c for c in df.columns
            if 'goals_per_game' in c or 'conceded_per_game' in c
            or 'matches_played' in c
        ]
        for col in goals_cols:
            median = df[col].median()
            self.median_values_[col] = median
            df[col] = df[col].fillna(median)
 
        # H2H → impute with neutral values
        for col, val in self.H2H_NEUTRAL_VALUES.items():
            if col in df.columns:
                df[col] = df[col].fillna(val)
 
        return df
 
    def _impute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply stored imputation values to new data.
        Uses values fitted on training set — no leakage.
        """
        # ELO change → 0
        for col in self.ELO_CHANGE_COLS:
            if col in df.columns:
                df[col] = df[col].fillna(0)
 
        # Medians from training set
        for col, median in self.median_values_.items():
            if col in df.columns:
                df[col] = df[col].fillna(median)
 
        # H2H neutral values
        for col, val in self.H2H_NEUTRAL_VALUES.items():
            if col in df.columns:
                df[col] = df[col].fillna(val)
 
        return df
 
    def _extract_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract and encode target columns."""
        y = df[
            [c for c in self.TARGET_COLS if c in df.columns]
        ].copy()
 
        # Encode result as integer for classification
        if 'result' in y.columns:
            y['result_encoded'] = y['result'].map(self.RESULT_ENCODING)
 
        return y
 
    def _select_feature_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        """Keep only numeric non-meta columns."""
        exclude = set(self.META_COLS + self.TARGET_COLS + self.DROP_COLS)
        cols    = [
            c for c in df.columns
            if c not in exclude
            and pd.api.types.is_numeric_dtype(df[c])
        ]
        return df[cols]
 
    def _align_feature_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Align test/prediction data to training feature columns.
        Adds missing cols as 0, drops extra cols.
        """
        for col in self.feature_cols_:
            if col not in df.columns:
                df[col] = 0
                print(f"  ⚠️  Missing feature '{col}' filled with 0")
 
        return df[self.feature_cols_]
 
    def _fit_scale(self, X: pd.DataFrame) -> pd.DataFrame:
        scaled = self.scaler.fit_transform(X)
        return pd.DataFrame(scaled, columns=X.columns, index=X.index)
 
    # ── Summary ───────────────────────────────────────────────────────────
 
    def summary(self) -> dict:
        if not self.is_fitted_:
            return {"status": "not fitted"}
        return {
            "features":         len(self.feature_cols_),
            "feature_names":    self.feature_cols_,
            "imputed_medians":  len(self.median_values_),
            "result_encoding":  self.RESULT_ENCODING,
        }