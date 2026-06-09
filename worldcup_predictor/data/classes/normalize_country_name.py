from src.config import TEAM_NAME_MAP

class TeamNameNormalizer:
    def normalize(self, name: str) -> str:
        return TEAM_NAME_MAP.get(name, name)

    def normalize_series(self, series):
        return series.replace(TEAM_NAME_MAP)

    def audit(self, *dataframes, col='team') -> set:
        """
        Pass in multiple DataFrames and get back the set of
        team names that don't appear in all sources — your mismatch report.
        """
        sets = [set(df[col].unique()) for df in dataframes]
        base = sets[0]
        for s in sets[1:]:
            base = base.symmetric_difference(s)
        return base