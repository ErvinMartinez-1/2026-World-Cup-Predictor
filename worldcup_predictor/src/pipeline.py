import pandas as pd
from dataclasses import dataclass, field
from typing import Optional

from worldcup_predictor.data.classes.load_match import MatchLoader
from worldcup_predictor.data.classes.ranking import Ranking
from worldcup_predictor.data.classes.elo import EloLoader
from worldcup_predictor.data.classes.normalize_country_name import TeamNameNormalizer

@dataclass
class PipelineStatus:
    matches: bool = False
    rankings: bool = False
    elo: bool = False
    errors: list = field(default_factory=list)

    def report(self):
        pass


class DataPipeline:

    def __init__(
        self,
        force_reload: bool = False,
        force_reload_matches: bool = False,
        force_reload_rankings: bool = False,
        force_reload_elo: bool = False,
        ranking_start_year: int = 2021,
        ranking_end_year: int = 2026,
    ):
        # Global force_reload overrides individual flags
        self._loaders = {
            "matches": MatchLoader(
                force_reload=force_reload or force_reload_matches
            ),
            "rankings": Ranking(
                force_reload=force_reload or force_reload_rankings,
                start_year=ranking_start_year,
                end_year=ranking_end_year,
            ),
            "elo": EloLoader(
                force_reload=force_reload or force_reload_elo
            ),
        }

        self._normalizer = TeamNameNormalizer()
        self.status = PipelineStatus()

        # Public data attributes populated by run()
        self.matches: Optional[pd.DataFrame] = None
        self.rankings: Optional[pd.DataFrame] = None
        self.elo: Optional[pd.DataFrame] = None

    def run(self) -> "DataPipeline":
        """
        Load all layers. Failures are isolated — one layer failing
        does not prevent the others from loading.
        """

        self.matches = self.load_layer("matches")
        self.rankings = self.load_layer("rankings")
        self.elo = self.load_layer("elo")

        self.validate_names()
        self.status.report()

        return self

    def rankings_at(self, date: str) -> pd.DataFrame:
        self.require("rankings")
        return self._loaders["rankings"].get_ranking_at_date(date)

    def team_matches(self, team: str) -> pd.DataFrame:
        self.require("matches")
        m = self.matches
        return m[
            (m['home_team'] == team) | (m['away_team'] == team)
        ].copy()

    def team_elo(self, team: str) -> Optional[float]:
        self.require("elo")
        row = self.elo[self.elo['team'] == team]
        return float(row['elo'].iloc[0]) if not row.empty else None

    def team_ranking(self, team: str) -> Optional[dict]:
        self.require("rankings")
        row = (
            self.rankings[self.rankings['team'] == team]
            .sort_values('rank_date')
            .tail(1)
        )
        return row.to_dict(orient='records')[0] if not row.empty else None

    def summary(self) -> dict:
        return {
            "matches": {
                "rows":       len(self.matches) if self.matches is not None else 0,
                "date_range": (
                    f"{self.matches['date'].min().date()} → "
                    f"{self.matches['date'].max().date()}"
                ) if self.matches is not None else "N/A",
                "teams": self.matches['home_team'].nunique() if self.matches is not None else 0,
            },
            "rankings": {
                "rows": len(self.rankings) if self.rankings is not None else 0,
                "snapshots": self.rankings['rank_date'].nunique() if self.rankings is not None else 0,
                "teams": self.rankings['team'].nunique() if self.rankings is not None else 0,
            },
            "elo": {
                "rows":  len(self.elo) if self.elo is not None else 0,
                "teams": self.elo['team'].nunique() if self.elo is not None else 0,
            },
        }

    def load_layer(self, name: str) -> Optional[pd.DataFrame]:
        """Load a single layer, isolating any exception."""
        try:
            df = self._loaders[name].load()
            setattr(self.status, name, True)
            return df
        except Exception as e:
            msg = f"{name}: {type(e).__name__}: {e}"
            self.status.errors.append(msg)
            return None

    def validate_names(self):
        loaded = {
            name: df.rename(columns={
                'home_team': 'team',
                'away_team': 'team',
            })
            for name, df in [
                ("matches",  self.matches),
                ("rankings", self.rankings),
                ("elo",      self.elo),
            ]
            if df is not None and 'team' in df.columns
        }

        if len(loaded) < 2:
            return

        mismatches = self._normalizer.audit(
            *loaded.values(), col='team'
        )
        if mismatches:
            pass

    def require(self, layer: str):
        if getattr(self, layer) is None:
            raise RuntimeError(
                f"Layer '{layer}' is not loaded. "
                f"Check pipeline.status for errors."
            )