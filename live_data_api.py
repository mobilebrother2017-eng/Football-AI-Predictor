import requests
import streamlit as st
from datetime import datetime

# Streamlit Secrets မှ API Key ကို လှမ်းယူခြင်း (မရပါက ယာယီ API ကို သုံးမည်)
try:
    API_KEY = st.secrets["API_SPORTS_KEY"]
except:
    # ယာယီစမ်းသပ်ရန်
    API_KEY = "f7dad2631e489455df6b63f5bc148dec"

HEADERS = {
    "x-apisports-key": API_KEY
}

# ဥရောပ ထိပ်သီးလိဂ် ၅ ခု၏ API IDs
API_LEAGUE_IDS = {
    "E0.csv": 39,    # Premier League (England)
    "SP1.csv": 140,  # La Liga (Spain)
    "I1.csv": 135,   # Serie A (Italy)
    "D1.csv": 78,    # Bundesliga (Germany)
    "F1.csv": 61     # Ligue 1 (France)
}

def get_current_season():
    """လက်ရှိ ဘောလုံးရာသီကို အလိုအလျောက် တွက်ချက်ခြင်း (ဥပမာ- 25/26 ရာသီအတွက် 2025 ကိုယူမည်)"""
    now = datetime.now()
    if now.month < 8: # ဩဂုတ်လမတိုင်ခင်ဆိုလျှင် ယခင်နှစ်ရာသီကို ယူမည်
        return str(now.year - 1)
    return str(now.year)

def get_todays_fixtures(league_code="E0.csv"):
    """ရွေးချယ်ထားသော လိဂ်အတွက် ဒီနေ့ကန်မည့် ပွဲစဉ်များကို ဆွဲယူခြင်း"""
    league_id = API_LEAGUE_IDS.get(league_code, 39)
    today_date = datetime.today().strftime('%Y-%m-%d')
    season = get_current_season()
    
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {"league": str(league_id), "season": season, "date": today_date} 
    
    try:
        response = requests.get(url, headers=HEADERS, params=querystring)
        data = response.json()
        
        fixtures = []
        if data.get('response'):
            for match in data['response']:
                fixture_id = match['fixture']['id']
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                match_status = match['fixture']['status']['short']
                # အချိန်ကို နာရီနှင့် မိနစ်သာ ယူရန် (ဥပမာ - 19:30)
                match_time = match['fixture']['date'][11:16] 
                
                fixtures.append({
                    "Fixture_ID": fixture_id,
                    "Match": f"{home_team} vs {away_team}",
                    "Home": home_team,
                    "Away": away_team,
                    "Time": match_time,
                    "Status": match_status
                })
        return fixtures
    except Exception as e:
        print(f"API Error: {e}")
        return []

# Terminal မှတဆင့် တိုက်ရိုက် စမ်းသပ်ရန်
if __name__ == "__main__":
    print("🔄 Testing API-Sports Connection...")
    
    # Premier League အတွက် စမ်းသပ်ခြင်း
    matches = get_todays_fixtures("E0.csv") 
    
    if matches:
        print(f"✅ ဒီနေ့ပွဲစဉ် စုစုပေါင်း ({len(matches)}) ပွဲ တွေ့ရှိပါသည်:\n")
        for m in matches:
            print(f"⏰ {m['Time']} | {m['Match']} ({m['Status']})")
    else:
        print("❌ ဒီနေ့အတွက် ကန်မည့်ပွဲ မရှိပါ (သို့) API ချိတ်ဆက်မှု အဆင်မပြေသေးပါ။ (ဥရောပစံတော်ချိန်အရ ပွဲမရှိသေးခြင်း ဖြစ်နိုင်ပါသည်)")
