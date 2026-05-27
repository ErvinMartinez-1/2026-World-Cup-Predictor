# src/data/elo_loader.py
import pandas as pd
import requests, os
from pathlib import Path
from data.classes.abstract_base_class import BaseDataLayer
from src.config import DATA_RAW, DATA_PROCESSED

class EloLoader(BaseDataLayer):
    @property
    def processed_path(self) -> Path:
        return DATA_PROCESSED / "elo_ratings.parquet"

    def load_raw(self) -> pd.DataFrame:
        local = DATA_RAW / "elo_ratings.tsv"
        if local.exists():
            return pd.read_csv(local, sep='\t',
                               names=['rank','team','elo','games_played'])
        url = os.getenv("ELO_URL")
        df = pd.read_csv(url, sep='\t',
                         names=['rank','team','elo','games_played'])
        df.to_csv(local, sep='\t', index=False)
        return df

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df['team'] = df['team'].str.strip()
        df['elo'] = pd.to_numeric(df['elo'], errors='coerce')
        return df.dropna(subset=['elo']).reset_index(drop=True)

    @property
    def processed_path(self) -> Path:
        return DATA_PROCESSED / "elo_ratings.parquet"

    def load_raw(self) -> pd.DataFrame:
        local = DATA_RAW / "elo_ratings.tsv"
        if local.exists():
            return pd.read_csv(local, sep='\t',
                               names=['rank','team','elo','games_played'])
        url = os.getenv("ELO_URL")
        df = pd.read_csv(url, sep='\t',
                         names=['rank','team','elo','games_played'])
        df.to_csv(local, sep='\t', index=False)
        return df

    def _lean(self, df: pd.DataFrame) -> pd.DataFrame:
        df['team'] = df['team'].str.strip()
        df['elo'] = pd.to_numeric(df['elo'], errors='coerce')
        return df.dropna(subset=['elo']).reset_index(drop=True)