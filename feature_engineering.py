# feature_engineering.py တွင် ထပ်မံဖြည့်စွက်ရန်
import pandas as pd
import numpy as np

def calculate_recent_form(df, match_window=5):
    """
    အသင်းတစ်သင်း၏ နောက်ဆုံး (၅) ပွဲ ရမှတ်များကို တွက်ချက်ခြင်း (Recent Form)
    """
    # Date ကို အစဉ်လိုက်ဖြစ်အောင် အရင်စီပါမယ်
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.sort_values(by='Date').reset_index(drop=True)
    
    # ရမှတ်များ သတ်မှတ်ခြင်း
    df['Home_Pts'] = df['FTR'].map({'H': 3, 'D': 1, 'A': 0})
    df['Away_Pts'] = df['FTR'].map({'H': 0, 'D': 1, 'A': 3})
    
    # Dictionary များဖြင့် အသင်းများ၏ ရမှတ်များကို မှတ်သားထားရန်
    team_form = {}
    home_form_list = []
    away_form_list = []
    
    for index, row in df.iterrows():
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        
        # အိမ်ကွင်းအသင်း၏ လက်ရှိ Form ကို ယူမည်
        if home_team not in team_form:
            team_form[home_team] = []
        home_form_list.append(sum(team_form[home_team][-match_window:])) # နောက်ဆုံး ၅ ပွဲပေါင်း ရမှတ်
        
        # အဝေးကွင်းအသင်း၏ လက်ရှိ Form ကို ယူမည်
        if away_team not in team_form:
            team_form[away_team] = []
        away_form_list.append(sum(team_form[away_team][-match_window:]))
        
        # ပွဲပြီးရလဒ်များကို ပြန်ထည့်မည်
        team_form[home_team].append(row['Home_Pts'])
        team_form[away_team].append(row['Away_Pts'])
        
    df['Home_Team_Form'] = home_form_list
    df['Away_Team_Form'] = away_form_list
    
    return df

def calculate_h2h(df):
    """
    ဒီနှစ်သင်း ထိပ်တိုက်တွေ့ဆုံခဲ့ဖူးသော နောက်ဆုံးပွဲများရှိ အိမ်ကွင်းအသင်း၏ နိုင်ခြေ (H2H)
    """
    h2h_win_rate = []
    
    for index, row in df.iterrows():
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        current_date = row['Date']
        
        # လက်ရှိပွဲမတိုင်ခင် အတိတ်က ဒီနှစ်သင်း တွေ့ခဲ့ဖူးတဲ့ ပွဲစဉ်များကို ရှာခြင်း
        past_matches = df[(df['Date'] < current_date) & 
                          (((df['HomeTeam'] == home_team) & (df['AwayTeam'] == away_team)) | 
                           ((df['HomeTeam'] == away_team) & (df['AwayTeam'] == home_team)))]
        
        if len(past_matches) > 0:
            # အိမ်ကွင်းအသင်း (Home Team) က နိုင်ခဲ့တဲ့ အကြိမ်အရေအတွက်ကို တွက်မည်
            home_wins = len(past_matches[(past_matches['HomeTeam'] == home_team) & (past_matches['FTR'] == 'H')]) + \
                        len(past_matches[(past_matches['AwayTeam'] == home_team) & (past_matches['FTR'] == 'A')])
            win_rate = home_wins / len(past_matches)
        else:
            win_rate = 0.5 # အရင်က မတွေ့ဖူးရင် 50% လို့ သတ်မှတ်မည်
            
        h2h_win_rate.append(win_rate)
        
    df['H2H_Home_Win_Rate'] = h2h_win_rate
    return df

def preprocess_data(df):
    """ Main processing function """
    # ယခင် Implied Probabilities များ တွက်ခြင်း
    df['Implied_Prob_H'] = 1 / df['B365H']
    df['Implied_Prob_D'] = 1 / df['B365D']
    df['Implied_Prob_A'] = 1 / df['B365A']
    df['Target'] = df['FTR'].map({'H': 0, 'D': 1, 'A': 2}) 
    
    # အသစ်ထည့်ထားသော Function များ
    df = calculate_recent_form(df)
    df = calculate_h2h(df)
    
    # တွက်ချက်မှု မရှိသေးသည့် အစောပိုင်း ပွဲစဉ်များ (NaN) ကို ရှင်းလင်းခြင်း
    df.fillna(0, inplace=True)
    return df