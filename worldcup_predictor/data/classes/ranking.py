from pathlib import Path
import asyncio
import pandas as pd

from worldcup_predictor.data.classes.abstract_base_class import BaseDataLayer
from src.fifa_ranking import FIFARanking
from src.config import DATA_RAW, DATA_PROCESSED, TEAM_NAME_MAP


class Ranking(BaseDataLayer):
    def __init__(self, force_reload: bool = False, start_year: int = 2021, end_year: int = 2026):
        super().__init__(force_reload)
        self.start_year = start_year
        self.end_year   = end_year
        self._scraper   = FIFARanking()

    @property
    def processed_path(self) -> Path:
        return DATA_PROCESSED / "rankings_clean.parquet"

    def load_raw(self) -> pd.DataFrame:
        raw_csv = DATA_RAW / "fifa_rankings_scraped.csv"

        if raw_csv.exists() and not self.force_reload:
            print("[RankingLoader] Loading cached raw CSV...")
            return pd.read_csv(raw_csv)

        print("[RankingLoader] Scraping FIFA rankings via Playwright...")
        df = asyncio.run(
            self._scraper.scrape(
                start_year=self.start_year,
                end_year=self.end_year,
                save_path=raw_csv,
                headless=True,
            )
        )
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['rank_date'] = pd.to_datetime(df['rank_date'])

        # Normalize team names to match other data sources
        df['team'] = df['country_full'].replace(TEAM_NAME_MAP)

        cols = [
            'rank_date', 'team', 'country_code', 'rank',
            'total_points', 'previous_points',
            'previous_rank', 'rank_change', 'confederation'
        ]
        # Only keep columns that actually exist (DOM fallback omits some)
        cols = [c for c in cols if c in df.columns]

        return (
            df[cols]
            .sort_values(['team', 'rank_date'])
            .reset_index(drop=True)
        )

    def get_ranking_at_date(self, date: str) -> pd.DataFrame:
        target = pd.to_datetime(date)
        return (
            self.data[self.data['rank_date'] <= target]
            .sort_values('rank_date')
            .groupby('team')
            .last()
            .reset_index()
        )