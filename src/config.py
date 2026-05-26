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