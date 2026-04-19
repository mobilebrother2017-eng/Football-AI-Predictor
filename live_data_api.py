import requests
import streamlit as st
from datetime import datetime

# Streamlit Secrets မှ API Key ကို လှမ်းယူခြင်း
try:
    API_KEY = st.secrets["FOOTBALL_DATA_API_KEY"]
except:
    API_KEY = "1fa5c122f54c43e98d08866baa536e44"

# Football-Data.org အတွက် Header သတ်မှတ်ချက်
HEADERS = { "X-Auth-Token": API_KEY }

# ဤ API အတွက် League Codes (API-Sports နှင့် မတူပါ)
LEAGUE_MAP = {
    "E0.csv": "PL",   # Premier League
    "SP1.csv": "PD",  # La Liga
    "I1.csv": "SA",   # Serie A
    "D1.csv": "BL1",  # Bundesliga
    "F1.csv": "FL1"   # Ligue 1
}

def get_todays_fixtures(league_code="E0.csv"):
    """ဒီနေ့ကန်မည့် ပွဲစဉ်များကို Football-Data.org မှ ဆွဲယူခြင်း"""
    api_league_code = LEAGUE_MAP.get(league_code, "PL")
    
    # ဒီနေ့ရက်စွဲကို ယူခြင်း
    today = datetime.now().strftime('%Y-%m-%d')
    
    # ကမ္ဘာ့အဆင့် ပွဲစဉ်များကို လှမ်းယူမည့် URL
    url = f"https://api.football-data.org/v4/competitions/{api_league_code}/matches"
    
    # ဤနေ့တွင် ကန်မည့်ပွဲများကိုသာ Filter လုပ်ခိုင်းခြင်း
    params = {
        "dateFrom": today,
        "dateTo": today
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        
        fixtures = []
        if 'matches' in data:
            for match in data['matches']:
                home_team = match['homeTeam']['shortName'] or match['homeTeam']['name']
                away_team = match['awayTeam']['shortName'] or match['awayTeam']['name']
                match_time = match['utcDate'][11:16] # အချိန်ယူခြင်း
                
                fixtures.append({
                    "Match": f"{home_team} vs {away_team}",
                    "Home": home_team,
                    "Away": away_team,
                    "Time": match_time,
                    "Status": match['status']
                })
        return fixtures
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

if __name__ == "__main__":
    print("🔄 Testing Football-Data.org API...")
    res = get_todays_fixtures("E0.csv")
    if res:
        for p in res: print(f"✅ {p['Time']} | {p['Match']}")
    else:
        print("ဒီနေ့အတွက် ပွဲစဉ်မရှိသေးပါ။ (သို့မဟုတ်) API Key ကန့်သတ်ချက် ရှိနေပါသည်။")
