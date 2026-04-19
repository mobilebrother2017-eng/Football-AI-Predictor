# config.py
BASE_URL = "https://www.football-data.co.uk/mmz4281/"

# Seasons: 2021 to 2025/2026 (5 historical + 1 current)
SEASONS = ["2021", "2122", "2223", "2324", "2425", "2526"]
LEAGUE = "E0.csv" # E0 is Premier League

# Columns we care about (Home Team, Away Team, Full Time Result, Odds - Bet365 Home/Draw/Away)
COLUMNS_NEEDED = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'B365H', 'B365D', 'B365A']