import pandas as pd
import numpy as np
from pathlib import Path
from itertools import combinations
from typing import Optional

from src.config import DATA_PROCESSED, WC_2026_GROUPS, TOURNAMENT_WEIGHTS


class FeatureBuilder:
    FORM_WINDOW_MATCHES = 10
    MIN_MATCHES_FOR_FORM = 3

    def __init__(self, matches: pd.DataFrame, rankings: pd.DataFrame, elo: pd.DataFrame):
        self.matches  = matches.copy()
        self.rankings = rankings.copy()
        self.elo = elo.copy()

        self.matches['date'] = pd.to_datetime(self.matches['date'])
        self.rankings['rank_date'] = pd.to_datetime(self.rankings['rank_date'])

        self.has_ranking_history = self.rankings['rank_date'].nunique() > 1
        self.latest_ranking_date = self.rankings['rank_date'].max()

        if not self.has_ranking_history:
            print("[FeatureBuilder] ⚠️  Single ranking snapshot detected "
                f"({self.latest_ranking_date.date()})")
            print("  → FIFA ranking features excluded from training set")
            print("  → FIFA ranking features included for WC 2026 predictions")

        self.team_match_view = self.build_team_match_view()

        print(f"[FeatureBuilder] Initialised")
        print(f"  Matches:  {len(self.matches):,} fixtures")
        print(f"  Rankings: {self.rankings['rank_date'].nunique()} snapshot(s), "
            f"{self.rankings['team'].nunique()} teams")
        print(f"  ELO:      {len(self.elo)} teams")

    def build_training_set(self, save_path: Optional[Path] = None) -> pd.DataFrame:
        print("\n[FeatureBuilder] Building training set...")
        rows = []

        total = len(self.matches)
        skipped  = 0

        for i, match in self.matches.iterrows():
            match_date = match['date']
            home_team = match['home_team']
            away_team = match['away_team']

            home_feats = self.build_team_features(home_team, match_date)
            away_feats = self.build_team_features(away_team, match_date)

            if home_feats is None or away_feats is None:
                skipped += 1
                continue

            row = {
                # ── Match metadata ──
                'date': match_date,
                'home_team': home_team,
                'away_team': away_team,
                'tournament': match['tournament'],
                'weight': match['weight'],
                'neutral': match['neutral'],

                **{f'home_{k}': v for k, v in home_feats.items()},

                **{f'away_{k}': v for k, v in away_feats.items()},

                'elo_diff': home_feats.get('elo', np.nan) - away_feats.get('elo', np.nan),
                'rank_diff': home_feats.get('fifa_rank', np.nan) - away_feats.get('fifa_rank', np.nan),
                'points_diff': home_feats.get('fifa_points', np.nan) - away_feats.get('fifa_points', np.nan),
                'form_diff': home_feats.get('form_points_per_game', np.nan) - away_feats.get('form_points_per_game', np.nan),
                'goals_scored_diff': home_feats.get('avg_goals_scored', np.nan) - away_feats.get('avg_goals_scored', np.nan),
                'goals_conceded_diff': home_feats.get('avg_goals_conceded', np.nan) - away_feats.get('avg_goals_conceded', np.nan),

                **self.build_h2h_features(home_team, away_team, match_date),

                'home_score': match['home_score'],
                'away_score': match['away_score'],
                'goal_diff': match['goal_diff'],
                'result': match['result']
            }
            rows.append(row)

            if (i + 1) % 500 == 0:
                print(f"  Processed {i + 1:,} / {total:,} matches...")

        df = pd.DataFrame(rows).reset_index(drop=True)

        print(f"\n  ✅ Training set built:")
        print(f"     Rows:    {len(df):,}  (skipped {skipped} — insufficient history)")
        print(f"     Columns: {len(df.columns)}")
        print(f"     Date range: {df['date'].min().date()} → {df['date'].max().date()}")

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(save_path, index=False)
            print(f"Saved → {save_path}")

        return df

    def build_fixture_features(self, home_team: str, away_team: str, date: str = "2026-06-11") -> dict:
        match_date = pd.Timestamp(date)

        home_feats = self.build_team_features(home_team, match_date, force_ranking_inclusion=True)
        away_feats = self.build_team_features(away_team, match_date, force_ranking_inclusion=True)

        if home_feats is None:
            raise ValueError(f"No features found for '{home_team}' as of {date}")
        if away_feats is None:
            raise ValueError(f"No features found for '{away_team}' as of {date}")

        return {
            'date': match_date,
            'home_team':  home_team,
            'away_team':  away_team,
            **{f'home_{k}': v for k, v in home_feats.items()},
            **{f'away_{k}': v for k, v in away_feats.items()},
            'elo_diff': home_feats.get('elo', np.nan) - away_feats.get('elo', np.nan),
            'rank_diff': home_feats.get('fifa_rank', np.nan) - away_feats.get('fifa_rank', np.nan),
            'points_diff': home_feats.get('fifa_points', np.nan) - away_feats.get('fifa_points', np.nan),
            'form_diff': home_feats.get('form_points_per_game', np.nan)- away_feats.get('form_points_per_game', np.nan),
            'goals_scored_diff': home_feats.get('avg_goals_scored', np.nan) - away_feats.get('avg_goals_scored', np.nan),
            'goals_conceded_diff': home_feats.get('avg_goals_conceded', np.nan) - away_feats.get('avg_goals_conceded', np.nan),
            
            **self.build_h2h_features(home_team, away_team, match_date)
        }

    def build_wc2026_fixtures(self) -> pd.DataFrame:
        print("\n[FeatureBuilder] Building WC 2026 group stage fixtures...")
        rows = []

        for group, teams in WC_2026_GROUPS.items():
            for home_team, away_team in combinations(teams, 2):
                try:
                    feats = self.build_fixture_features(home_team, away_team, date="2026-06-11")
                    feats['group'] = group
                    rows.append(feats)
                except ValueError as e:
                    print(f"  ⚠️  Skipped {home_team} vs {away_team}: {e}")

        df = pd.DataFrame(rows)
        print(f"  ✅ {len(df)} fixtures built across {len(WC_2026_GROUPS)} groups")
        return df

    def build_team_features(self, team: str, as_of_date: pd.Timestamp, force_ranking_inclusion: bool = False) -> Optional[dict]:
        features = {}

        elo_feats = self.get_elo_features(team)
        if elo_feats:
            features.update(elo_feats)

        should_include = (force_ranking_inclusion or(self.has_ranking_history and as_of_date <= self.latest_ranking_date))

        if should_include:
            rank_feats = self.get_ranking_features(team, as_of_date)
            if rank_feats:
                features.update(rank_feats)

        form_feats = self.get_form_features(team, as_of_date)
        if form_feats:
            features.update(form_feats)

        return features if features else None



    def get_elo_features(self, team: str) -> dict:
        row = self.elo[self.elo['team'] == team]
        if row.empty:
            return {}

        r = row.iloc[0]
        return {
            'elo': r.get('elo'),
            'elo_highest': r.get('elo_highest'),
            'elo_1yr_ago': r.get('elo_1yr_ago'),
            'elo_change_30d': r.get('elo_change_30d'),
            'elo_change_90d': r.get('elo_change_90d'),
            'elo_change_365d': r.get('elo_change_365d'),
            'elo_change_3yr': r.get('elo_change_3yr'),
            'elo_rank': r.get('rank'),
            'matches_played': r.get('matches_played'),
            'win_rate': self.safe_divide(
                            r.get('wins'), r.get('matches_played')
                        ),
            'draw_rate': self.safe_divide(
                            r.get('draws'), r.get('matches_played')
                        ),
            'loss_rate': self.safe_divide(r.get('losses'), r.get('matches_played')
                            ),
            'goals_per_game': self.safe_divide(r. get('total_goals_scored'), r.get('matches_played')),
            'conceded_per_game':    self.safe_divide(r.get('total_goals_conceded'), r.get('matches_played'))
        }

    def get_ranking_features(self, team: str, as_of_date: pd.Timestamp) -> dict:
        team_rankings = self.rankings[(self.rankings['team'] == team) & (self.rankings['rank_date'] <= as_of_date)]

        if team_rankings.empty:
            # No snapshot on or before this date — return empty rather than leaking future ranking data into historical training rows
            return {}

        latest = team_rankings.sort_values('rank_date').iloc[-1]

        return {
            'fifa_rank': latest.get('rank'),
            'fifa_points': latest.get('total_points'),
            'fifa_points_change': (
                latest.get('total_points', 0) - latest.get('previous_points', 0)
                if pd.notna(latest.get('previous_points')) else np.nan
            )
        }

    def get_form_features(self, team: str, as_of_date: pd.Timestamp) -> dict:
        past_matches = self.team_match_view[
            (self.team_match_view['team'] == team) &
            (self.team_match_view['date'] < as_of_date)
        ].sort_values('date').tail(self.FORM_WINDOW_MATCHES)

        if len(past_matches) < self.MIN_MATCHES_FOR_FORM:
            return {}

        # Points per game (3=win, 1=draw, 0=loss) weighted by tournament
        past_matches = past_matches.copy()
        past_matches['points'] = past_matches['team_result'].map(
            {'win': 3, 'draw': 1, 'loss': 0}
        )
        past_matches['weighted_points'] = (
            past_matches['points'] * past_matches['weight']
        )

        total_weight = past_matches['weight'].sum()

        return {
            'form_points_per_game':self.safe_divide(past_matches['weighted_points'].sum(), total_weight),
            'form_wins': (past_matches['team_result'] == 'win').sum(),
            'form_draws': (past_matches['team_result'] == 'draw').sum(),
            'form_losses': (past_matches['team_result'] == 'loss').sum(),
            'form_win_rate': self.safe_divide((past_matches['team_result'] == 'win').sum(), len(past_matches)),

            'avg_goals_scored': past_matches['goals_scored'].mean(),
            'avg_goals_conceded': past_matches['goals_conceded'].mean(),
            'avg_goal_diff': past_matches['goal_diff'].mean(),

            'wavg_goals_scored': self.safe_divide((past_matches['goals_scored'] * past_matches['weight']).sum(), total_weight),
            'wavg_goals_conceded': self.safe_divide((past_matches['goals_conceded'] * past_matches['weight']).sum(),total_weight),

            'form_matches_available':  len(past_matches)
        }

    def build_h2h_features(self, team_a: str, team_b: str, as_of_date: pd.Timestamp, window: int = 10) -> dict:
        prefix = 'h2h_'

        h2h = self.matches[
            (
                ((self.matches['home_team'] == team_a) &
                 (self.matches['away_team'] == team_b)) |
                ((self.matches['home_team'] == team_b) &
                 (self.matches['away_team'] == team_a))
            ) &
            (self.matches['date'] < as_of_date)
        ].sort_values('date').tail(window)

        if h2h.empty:
            return {
                f'{prefix}matches': 0,
                f'{prefix}team_a_wins': np.nan,
                f'{prefix}team_b_wins': np.nan,
                f'{prefix}draws': np.nan,
                f'{prefix}team_a_winrate': np.nan,
                f'{prefix}avg_goals': np.nan,
            }

        team_a_wins = 0
        team_b_wins = 0
        draws = 0
        total_goals = []

        for _, m in h2h.iterrows():
            total_goals.append(m['home_score'] + m['away_score'])
            if m['result'] == 'draw':
                draws += 1
            elif (m['home_team'] == team_a and m['result'] == 'home_win') or \
                 (m['away_team'] == team_a and m['result'] == 'away_win'):
                team_a_wins += 1
            else:
                team_b_wins += 1

        n = len(h2h)
        return {
            f'{prefix}matches': n,
            f'{prefix}team_a_wins': team_a_wins,
            f'{prefix}team_b_wins': team_b_wins,
            f'{prefix}draws': draws,
            f'{prefix}team_a_winrate': self.safe_divide(team_a_wins, n),
            f'{prefix}avg_goals': np.mean(total_goals) if total_goals else np.nan
        }

    def build_team_match_view(self) -> pd.DataFrame:
        home = self.matches.rename(columns={
            'home_team': 'team',
            'away_team': 'opponent',
            'home_score': 'goals_scored',
            'away_score': 'goals_conceded',
        }).copy()
        home['team_result'] = home['result'].map({
            'home_win': 'win',
            'away_win': 'loss',
            'draw': 'draw'
        })
        home['goal_diff'] = home['goals_scored'] - home['goals_conceded']
        home['is_home'] = True

        away = self.matches.rename(columns={
            'away_team': 'team',
            'home_team': 'opponent',
            'away_score': 'goals_scored',
            'home_score': 'goals_conceded'
        }).copy()
        away['team_result'] = away['result'].map({
            'away_win': 'win',
            'home_win': 'loss',
            'draw': 'draw'
        })
        away['goal_diff'] = away['goals_scored'] - away['goals_conceded']
        away['is_home'] = False

        cols = ['date', 'team', 'opponent', 'team_result', 'goals_scored',
                'goals_conceded', 'goal_diff', 'weight', 'tournament', 'is_home']

        view = pd.concat([home[cols], away[cols]], ignore_index=True)
        return view.sort_values(['team', 'date']).reset_index(drop=True)

    @staticmethod
    def safe_divide(numerator, denominator) -> float:
        """Division that returns NaN instead of ZeroDivisionError."""
        try:
            if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
                return np.nan
            return float(numerator) / float(denominator)
        except Exception:
            return np.nan