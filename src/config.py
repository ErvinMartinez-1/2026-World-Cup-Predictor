from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"
TRAINING_START_DATE = "2021-01-01"

TOURNAMENT_WEIGHTS = {
    "FIFA World Cup": 4.0,
    "UEFA Euro": 3.5,
    "Copa América": 3.5,
    "CONCACAF Gold Cup": 3.0,
    "Africa Cup of Nations": 3.0,
    "AFC Asian Cup": 3.0,
    "FIFA World Cup qualification": 2.5,
    "UEFA Nations League": 2.0,
    "Friendly": 0.5,
}

TEAM_NAME_MAP = {
    "USA": "United States",
    "United States of America": "United States",
    "IR Iran": "Iran",
    "Korea Republic": "South Korea",
    "Türkiye": "Turkey",
    "Côte d'Ivoire":"Ivory Coast"
}

ELO_CODE_TO_NAME = {
    # Europe
    'ES': 'Spain',     'FR': 'France',      'EN': 'England',
    'PT': 'Portugal',  'NL': 'Netherlands', 'BE': 'Belgium',
    'DE': 'Germany',   'HR': 'Croatia',     'IT': 'Italy',
    'SE': 'Sweden',    'DK': 'Denmark',     'CH': 'Switzerland',
    'AT': 'Austria',   'PL': 'Poland',      'CZ': 'Czech Republic',
    'RS': 'Serbia',    'RO': 'Romania',     'HU': 'Hungary',
    'SK': 'Slovakia',  'UA': 'Ukraine',     'GR': 'Greece',
    'NO': 'Norway',    'FI': 'Finland',     'IE': 'Ireland',
    'SC': 'Scotland',  'WA': 'Wales',       'MK': 'North Macedonia',
    'AL': 'Albania',   'GE': 'Georgia',     'SL': 'Slovenia',
    'TR': 'Turkey',    'SQ': 'Albania',     'SI': 'Slovenia',
    'EI': 'Ireland',


    # South America
    'AR': 'Argentina', 'BR': 'Brazil',   'UY': 'Uruguay',
    'CO': 'Colombia',  'CL': 'Chile',    'PE': 'Peru',
    'PY': 'Paraguay',  'BO': 'Bolivia',  'VE': 'Venezuela',
    'EC': 'Ecuador',

    # North/Central America & Caribbean
    'US': 'United States',   'MX': 'Mexico',    'CA': 'Canada',
    'CR': 'Costa Rica',      'PA': 'Panama',    'JM': 'Jamaica',
    'HN': 'Honduras',        'GT': 'Guatemala', 'SV': 'El Salvador',
    'CU': 'Cuba',            'PR': 'Puerto Rico', 'CW': 'Curaçao',
    'CUW': 'Curaçao',

    # Africa
    'MA': 'Morocco',  'NG': 'Nigeria',      'CM': 'Cameroon',
    'GH': 'Ghana',    'CI': 'Ivory Coast',  'EG': 'Egypt',
    'TN': 'Tunisia',  'ZA': 'South Africa', 'SN': 'Senegal',
    'DZ': 'Algeria',  'ML': 'Mali',         'BF': 'Burkina Faso',
    'CD': 'DR Congo', 'CV': 'Cape Verde',   'CPV': 'Cape Verde',

    # Asia & Oceania & Middle East
    'IR': 'Iran',           'SA': 'Saudi Arabia',       'KR': 'South Korea',
    'JP': 'Japan',          'CN': 'China',              'QA': 'Qatar',
    'AU': 'Australia',      'NZ': 'New Zealand',        'RU': 'Russia',
    'UZ': 'Uzbekistan',     'KO': 'South Korea',        'JO': 'Jordan',
    'IL': 'Israel',         'IQ': 'Iraq',               'BA': 'Bosnia and Herzegovina',
    'NM': 'North Macedonia','AE': 'United Arab Emirates', 'HT': 'Haiti',
    'SY': 'Syria',
}

WC_2026_GROUPS = {
    'Group A': ['Mexico', 'South Korea', 'South Africa', 'Czech Republic'],
    'Group B': ['Canada', 'Switzerland', 'Qatar', 'Bosnia and Herzegovina'],
    'Group C': ['Spain', 'Japan', 'Panama', 'Algeria'],
    'Group D': ['United States', 'Paraguay', 'Australia', 'Turkey'],
    'Group E': ['Germany', 'Colombia', 'Egypt', 'Curaçao'],
    'Group F': ['Portugal', 'Uruguay', 'Ivory Coast', 'Uzbekistan'],
    'Group G': ['Belgium', 'Croatia', 'Morocco', 'Haiti'],
    'Group H': ['France', 'Canada', 'Austria', 'New Zealand'],
    'Group I': ['Argentina', 'Norway', 'Saudi Arabia', 'DR Congo'],
    'Group J': ['Brazil', 'England', 'Tunisia', 'Ghana'],
    'Group K': ['Netherlands', 'Senegal', 'Ecuador', 'Jordan'],
    'Group L': ['Iran', 'Scotland', 'Cape Verde', 'Sweden'],
}

WC_2026_TEAMS = {
    team for teams in WC_2026_GROUPS.values() for team in teams
}

ELO_COL_NAMES = [
    'rank',              
    'previous_rank',     
    'country_code',      
    'elo',               
    'confederation_rank',
    'elo_highest',       
    'rank_highest',      
    'elo_1yr_ago',       
    'rank_1yr_ago',      
    'elo_5yr_ago',       
    'rank_change_5yr',  
    'elo_change_last_match',  
    'rank_change_last_match', 
    'elo_change_30d',   
    'rank_change_30d',   
    'elo_change_90d',   
    'rank_change_90d',   
    'elo_change_365d', 
    'rank_change_365d',  
    'elo_change_3yr',    
    'rank_change_3yr',  
    'elo_change_5yr',    
    'matches_played',   
    'wins',              
    'draws',            
    'losses',            
    'goals_scored',      
    'goals_conceded_home',  
    'goals_conceded_away',  
    'total_goals_scored',   
    'total_goals_conceded'
]

ELO_MODEL_COLS = [
    'rank', 
    'previous_rank', 
    'country_code', 
    'elo',
    'elo_highest', 
    'elo_1yr_ago',
    'elo_change_last_match', 
    'elo_change_30d',
    'elo_change_90d', 
    'elo_change_365d', 
    'elo_change_3yr',
    'matches_played', 
    'wins', 
    'draws', 
    'losses',
    'goals_scored', 
    'total_goals_scored', 
    'total_goals_conceded'
]