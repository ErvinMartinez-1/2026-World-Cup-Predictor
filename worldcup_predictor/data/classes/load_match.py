# src/data/match_loader.py
import pandas as pd
from pathlib import Path
from worldcup_predictor.data.classes.abstract_base_class import BaseDataLayer
from src.config import DATA_RAW, DATA_PROCESSED, TRAINING_START_DATE, TOURNAMENT_WEIGHTS

class MatchLoader(BaseDataLayer):
    def __init__(self, force_reload: bool = False):
        super().__init__(force_reload)
        
    @property
    def processed_path(self) -> Path:
        return DATA_PROCESSED / "matches_clean.parquet"

    def load_raw(self) -> pd.DataFrame:
        return pd.read_csv(DATA_RAW / "results.csv")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'] >= TRAINING_START_DATE].copy()
        df['weight'] = df['tournament'].map(TOURNAMENT_WEIGHTS).fillna(1.0)
        df['goal_diff'] = df['home_score'] - df['away_score']
        df['result'] = df['goal_diff'].apply(
            lambda x: 'home_win' if x > 0 else ('away_win' if x < 0 else 'draw')
        )
        return df.reset_index(drop=True)