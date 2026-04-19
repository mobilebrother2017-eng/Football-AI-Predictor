import pandas as pd

BASE_URL = "https://www.football-data.co.uk/mmz4281/"
SEASONS = ["2122", "2223", "2324", "2425", "2526"]
# HST (Home Shots on Target), AST (Away Shots on Target) များကို xG တွက်ရန် ထည့်ထားသည်
COLUMNS_NEEDED = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'B365H', 'B365D', 'B365A', 'HST', 'AST']

def fetch_and_clean_data(league_code="E0.csv"):
    """ရွေးချယ်ထားသော League အလိုက် Data များ ဆွဲယူခြင်း"""
    all_data = []
    for season in SEASONS:
        url = f"{BASE_URL}{season}/{league_code}"
        try:
            df = pd.read_csv(url, encoding='unicode_escape')
            
            # API တွင် Column အချို့ မပါဝင်ပါက Error မတက်စေရန် စစ်ဆေးခြင်း
            cols_to_use = [col for col in COLUMNS_NEEDED if col in df.columns]
            df = df[cols_to_use]
            
            df['Season'] = season
            all_data.append(df)
        except Exception as e:
            # Data မရှိသေးသော ရာသီများအတွက် ကျော်သွားရန်
            pass
            
    if not all_data:
        return pd.DataFrame()
        
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.dropna(subset=['FTR', 'B365H', 'B365D', 'B365A'], inplace=True)
    return combined_df