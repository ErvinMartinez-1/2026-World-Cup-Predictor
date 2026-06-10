import pandas as pd
import requests, os
from pathlib import Path
from io import StringIO
from worldcup_predictor.data.classes.abstract_base_class import BaseDataLayer
from src.config import DATA_RAW, DATA_PROCESSED, ELO_CODE_TO_NAME, ELO_MODEL_COLS, ELO_COL_NAMES, WC_2026_TEAMS

class EloLoader(BaseDataLayer):
    ELO_URL = "https://eloratings.net/World.tsv"
    def __init__(self, force_reload: bool = False):
        super().__init__(force_reload)

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

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        change_cols = [c for c in df.columns if 'change' in c]
        for col in change_cols:
            df[col] = (
                df[col].astype(str)
                    .str.replace('â', '-', regex=False)
                    .str.replace('+', '', regex=False)
                    .str.strip()
            )

        df['team'] = df['country_code'].map(ELO_CODE_TO_NAME)
        numeric_cols = [c for c in ELO_COL_NAMES if c != 'country_code']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        keep = ['team'] + [c for c in ELO_MODEL_COLS if c in df.columns]
        df = df[keep]
        unmapped_codes = df[df['team'].isna()]
        total_unmapped = len(unmapped_codes)
        df = df.dropna(subset=['team'])

        loaded_teams  = set(df['team'].unique())
        missing_wc    = WC_2026_TEAMS - loaded_teams
        if missing_wc:
            print(f"[EloLoader] Warning:  WC teams missing from ELO data: {missing_wc}")

        else:
            print(f"[EloLoader] Success: All 48 WC teams found in ELO data")
            print(f"[EloLoader] Caution: {total_unmapped} non-WC minor nations dropped (expected)")

        return df.reset_index(drop=True)

    @property
    def processed_path(self) -> Path:
        return DATA_PROCESSED / "elo_ratings.parquet"

    def load_raw(self) -> pd.DataFrame:
        local = DATA_RAW / "elo_ratings.tsv"
        print(f"[EloLoader] Looking for TSV at: {local}")
        print(f"[EloLoader] File exists: {local.exists()}")
        print(f"[EloLoader] force_reload: {self.force_reload}")

        if local.exists() and not self.force_reload:
            print("[EloLoader] Loading from local TSV...")
            return pd.read_csv(local, sep='\t', names=ELO_COL_NAMES, header=None, encoding='utf-8')

        print("[EloLoader] Attempting download...")
        df = self.download()
        print(f"[EloLoader] Download result: {type(df)}")
        print(f"[EloLoader] Download head: {df.head() if df is not None else 'None'}")

        if df is not None:
            local.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(local, sep='\t', index=False, header=False)
            print(f"[EloLoader] Success: Saved to {local}")
            return df

        raise FileNotFoundError(
            f"ELO download failed. Manually download from:\n"
            f"{self.ELO_URL}\n"
            f"and save to:\n"
            f" {local}"
        )

    def lean(self, df: pd.DataFrame) -> pd.DataFrame:
        df['team'] = df['team'].str.strip()
        df['elo'] = pd.to_numeric(df['elo'], errors='coerce')
        return df.dropna(subset=['elo']).reset_index(drop=True)
    
    def download(self) -> pd.DataFrame | None:
        try:
            response = requests.get(
                self.ELO_URL,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15,
            )
            response.raise_for_status()

            if "<html" in response.text[:100].lower():
                print("[EloLoader] Warning:  Got HTML instead of TSV")
                return None

            df = pd.read_csv(
                StringIO(response.text),   # ← response text, not the URL
                sep='\t',
                names=ELO_COL_NAMES,           # ← all 31 columns
                header=None,
                encoding='utf-8',
            )
            print(f"[EloLoader] Success: Downloaded {len(df)} teams")
            return df

        except Exception as e:
            import traceback
            print(f"[EloLoader] Fail: Download failed: {type(e).__name__}: {e}")
            traceback.print_exc()
            