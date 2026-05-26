import pandas as pd

class WorldCupDataPipeline:
    def __init__(self, start_date='2021-01-01'):
        self.start_date = start_date
        self.results = None
        self.elo_ratings = None
        self.fifa_rankings = None
    
    def load_all(self):
        self.results = self._load_match_results()
        self.elo_ratings = self._load_elo_ratings()
        self.fifa_rankings = self._load_fifa_rankings()
        return self
    
    def load_match_results(self):
        df = pd.read_csv('data/results.csv', parse_dates=['date'])
        return df[df['date'] >= self.start_date].copy()
    
    def load_elo_ratings(self):
        return get_elo_ratings()  # from Layer 3 above
    
    def load_fifa_rankings(self):
        return pd.read_csv('data/fifa_rankings.csv')  # Kaggle dataset
    
    def get_team_features(self, team: str) -> dict:
        """Pull all features for a single team"""
        team_matches = self.results[
            (self.results['home_team'] == team) | 
            (self.results['away_team'] == team)
        ].tail(20)
        
        return {
            'team': team,
            'elo': self._get_current_elo(team),
            'fifa_rank': self._get_fifa_rank(team),
            'recent_form': self._calc_form(team, team_matches),
            'avg_goals_scored': self._calc_avg_goals(team, team_matches),
            'avg_goals_conceded': self._calc_avg_conceded(team, team_matches),
        }