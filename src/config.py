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
    'Group A': ['Mexico', 'South Africa', 'South Korea', 'Czech Republic'],
    'Group B': ['Canada', 'Bosnia and Herzegovina', 'Qatar', 'Switzerland'],
    'Group C': ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    'Group D': ['United States', 'Paraguay', 'Australia', 'Turkey'],
    'Group E': ['Germany', 'Curaçao', 'Ivory Coast', 'Ecuador'],
    'Group F': ['Netherlands', 'Japan', 'Tunisia', 'Sweden'],
    'Group G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'Group H': ['Spain', 'Cape Verde', 'Saudi Arabia', 'Uruguay'],
    'Group I': ['France', 'Senegal', 'Norway', 'Iraq'],
    'Group J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'Group K': ['Portugal', 'Uzbekistan', 'Colombia', 'DR Congo'],
    'Group L': ['England', 'Croatia', 'Ghana', 'Panama']
}

WC_2026_HOST_NATIONS = {'United States', 'Mexico', 'Canada'}

WC_2026_HOST_CITIES = {
    # United States
    'New York': 'United States',   
    'Los Angeles': 'United States',   
    'Dallas': 'United States',  
    'San Francisco': 'United States',  
    'Seattle': 'United States',   
    'Boston': 'United States',   
    'Miami': 'United States',  
    'Atlanta': 'United States',   
    'Kansas City': 'United States', 
    'Houston': 'United States', 
    'Philadelphia': 'United States', 

    # Mexico
    'Mexico City': 'Mexico',          
    'Guadalajara': 'Mexico',         
    'Monterrey': 'Mexico',          

    # Canada
    'Toronto': 'Canada',          
    'Vancouver': 'Canada'     
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

FIXTURE_CITIES = {

    # Group A 
    ('Mexico', 'South Africa'): 'Mexico City',   
    ('South Korea', 'Czech Republic'): 'Guadalajara',   
    ('Mexico', 'South Korea'): 'Guadalajara',  
    ('South Africa', 'South Korea'):'Monterrey',  

    # Group B 
    ('Canada', 'Bosnia and Herzegovina'):'Toronto',       
    ('Qatar', 'Switzerland'): 'San Francisco', 
    ('Switzerland', 'Bosnia and Herzegovina'): 'Los Angeles',
    ('Canada', 'Qatar'): 'Vancouver', 
    ('Switzerland', 'Canada'): 'Vancouver',    
    ('Bosnia and Herzegovina', 'Qatar'): 'Seattle',

    # Group C 
    ('Brazil', 'Morocco'):'New York',     
    ('Haiti', 'Scotland'): 'Boston',         
    ('Scotland', 'Morocco'): 'Boston',     
    ('Brazil', 'Haiti'): 'Philadelphia',
    ('Scotland', 'Brazil'): 'Miami',
    ('Morocco', 'Haiti'): 'Atlanta',

    #  Group D 
    ('United States', 'Paraguay'): 'Los Angeles',    
    ('Australia', 'Turkey'): 'Vancouver',     
    ('Turkey', 'Paraguay'): 'San Francisco', 
    ('United States', 'Australia'): 'Seattle',      
    ('Turkey', 'United States'): 'Los Angeles',   
    ('Paraguay', 'Australia'): 'San Francisco', 

    # Group E 
    ('Germany', 'Curaçao'): 'Houston',     
    ('Ivory Coast', 'Ecuador'): 'Philadelphia',
    ('Germany', 'Ivory Coast'): 'Toronto',    
    ('Ecuador', 'Curaçao'): 'Kansas City',
    ('Ecuador', 'Germany'): 'New York',       
    ('Curaçao', 'Ivory Coast'): 'Philadelphia',

    # Group F
    ('Netherlands', 'Japan'): 'Dallas',        
    ('Sweden', 'Tunisia'): 'Monterrey',     
    ('Netherlands', 'Sweden'): 'Houston',         
    ('Tunisia', 'Japan'): 'Monterrey',     
    ('Tunisia', 'Netherlands'): 'Dallas',         
    ('Japan', 'Sweden'): 'Kansas City',

    # Group G 
    ('Belgium', 'Egypt'): 'Seattle',
    ('Iran', 'New Zealand'): 'Los Angeles',
    ('Belgium', 'Iran'): 'Atlanta',
    ('New Zealand', 'Egypt'): 'Kansas City',
    ('New Zealand', 'Belgium'): 'Miami',
    ('Egypt', 'Iran'): 'Dallas',

    # Group H 
    ('Spain', 'Cape Verde'): 'Atlanta',
    ('Saudi Arabia', 'Uruguay'): 'Miami',
    ('Spain', 'Saudi Arabia'): 'Atlanta',
    ('Uruguay', 'Cape Verde'): 'Houston',
    ('Uruguay', 'Spain'): 'Guadalajara',   
    ('Cape Verde', 'Saudi Arabia'): 'Dallas',

    # Group I 
    ('France', 'Senegal'): 'New York',      
    ('Iraq', 'Norway'): 'Boston',
    ('France', 'Iraq'): 'Philadelphia',
    ('Norway', 'Senegal'): 'Boston',
    ('Norway', 'France'): 'Boston',
    ('Senegal', 'Iraq'): 'Philadelphia',

    # Group J 
    ('Argentina', 'Algeria'): 'Kansas City',
    ('Austria', 'Jordan'): 'San Francisco',
    ('Argentina', 'Austria'): 'Dallas',
    ('Jordan', 'Algeria'): 'Dallas',
    ('Jordan', 'Argentina'): 'Dallas',
    ('Algeria', 'Austria'): 'Kansas City',

    # Group K 
    ('Portugal', 'DR Congo'): 'Houston',
    ('Uzbekistan', 'Colombia'): 'Dallas',
    ('Portugal', 'Uzbekistan'): 'Dallas',
    ('Colombia', 'DR Congo'): 'Houston',
    ('Colombia', 'Portugal'): 'Houston',
    ('DR Congo', 'Uzbekistan'): 'Atlanta',

    # Group L 
    ('England', 'Croatia'): 'Dallas',
    ('Ghana', 'Panama'): 'Atlanta',
    ('England', 'Ghana'): 'Boston',
    ('Panama', 'Croatia'): 'Miami',
    ('Panama', 'England'): 'New York',      
    ('Croatia', 'Ghana'):  'Miami'
}