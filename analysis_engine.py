import pandas as pd
import math

def get_current_teams(df):
    latest_season = df['Season'].max()
    teams = sorted(df[df['Season'] == latest_season]['HomeTeam'].unique())
    return teams

def calculate_form_and_trend(team_name, df, num_matches=5):
    team_matches = df[(df['HomeTeam'] == team_name) | (df['AwayTeam'] == team_name)].sort_values(by='Date').tail(num_matches)
    points = 0
    form_string = []
    
    for _, row in team_matches.iterrows():
        if row['HomeTeam'] == team_name and row['FTR'] == 'H':
            points += 3
            form_string.append('W')
        elif row['AwayTeam'] == team_name and row['FTR'] == 'A':
            points += 3
            form_string.append('W')
        elif row['FTR'] == 'D':
            points += 1
            form_string.append('D')
        else:
            form_string.append('L')
            
    trend = " -> ".join(form_string) 
    return points, trend

def calculate_h2h_stats(home_team, away_team, df):
    matches = df[((df['HomeTeam'] == home_team) & (df['AwayTeam'] == away_team)) | 
                 ((df['HomeTeam'] == away_team) & (df['AwayTeam'] == home_team))]
    
    if len(matches) == 0:
        return 0.5, 0, 0, 0
    
    home_wins = len(matches[(matches['HomeTeam'] == home_team) & (matches['FTR'] == 'H')]) + \
                len(matches[(matches['AwayTeam'] == home_team) & (matches['FTR'] == 'A')])
    win_rate = home_wins / len(matches)
    
    avg_h_odd = matches['B365H'].mean() if not matches['B365H'].isnull().all() else 0
    avg_d_odd = matches['B365D'].mean() if not matches['B365D'].isnull().all() else 0
    avg_a_odd = matches['B365A'].mean() if not matches['B365A'].isnull().all() else 0
    
    return win_rate, avg_h_odd, avg_d_odd, avg_a_odd

def generate_league_table(df):
    latest_season = df['Season'].max()
    current_df = df[df['Season'] == latest_season]
    
    table = {}
    for _, row in current_df.iterrows():
        home = row['HomeTeam']; away = row['AwayTeam']
        if home not in table: table[home] = {'P':0, 'W':0, 'D':0, 'L':0, 'GF':0, 'GA':0, 'Pts':0}
        if away not in table: table[away] = {'P':0, 'W':0, 'D':0, 'L':0, 'GF':0, 'GA':0, 'Pts':0}
        
        table[home]['P'] += 1; table[away]['P'] += 1
        table[home]['GF'] += row['FTHG']; table[home]['GA'] += row['FTAG']
        table[away]['GF'] += row['FTAG']; table[away]['GA'] += row['FTHG']
        
        if row['FTR'] == 'H':
            table[home]['W'] += 1; table[home]['Pts'] += 3; table[away]['L'] += 1
        elif row['FTR'] == 'A':
            table[away]['W'] += 1; table[away]['Pts'] += 3; table[home]['L'] += 1
        else:
            table[home]['D'] += 1; table[away]['D'] += 1; table[home]['Pts'] += 1; table[away]['Pts'] += 1

    table_df = pd.DataFrame.from_dict(table, orient='index').reset_index()
    table_df.rename(columns={'index': 'Team'}, inplace=True)
    table_df['GD'] = table_df['GF'] - table_df['GA']
    table_df = table_df.sort_values(by=['Pts', 'GD', 'GF'], ascending=[False, False, False]).reset_index(drop=True)
    table_df.index += 1 
    return table_df

def calculate_xg_proxy(team_name, df, num_matches=5):
    team_matches = df[(df['HomeTeam'] == team_name) | (df['AwayTeam'] == team_name)].sort_values(by='Date').tail(num_matches)
    
    total_xg_created = 0.0
    total_xg_conceded = 0.0
    
    for _, row in team_matches.iterrows():
        if 'HST' in row and 'AST' in row and not pd.isna(row['HST']):
            if row['HomeTeam'] == team_name:
                total_xg_created += (row['HST'] * 0.11) + (row['FTHG'] * 0.5) 
                total_xg_conceded += (row['AST'] * 0.11) + (row['FTAG'] * 0.5)
            else:
                total_xg_created += (row['AST'] * 0.11) + (row['FTAG'] * 0.5)
                total_xg_conceded += (row['HST'] * 0.11) + (row['FTHG'] * 0.5)
        else:
            if row['HomeTeam'] == team_name:
                total_xg_created += row['FTHG']; total_xg_conceded += row['FTAG']
            else:
                total_xg_created += row['FTAG']; total_xg_conceded += row['FTHG']

    avg_xg_created = total_xg_created / num_matches if num_matches > 0 else 0
    avg_xg_conceded = total_xg_conceded / num_matches if num_matches > 0 else 0
    
    return round(avg_xg_created, 2), round(avg_xg_conceded, 2)

def get_motivation_status(team_name, league_table_df):
    team_row = league_table_df[league_table_df['Team'] == team_name]
    
    if team_row.empty:
        return "Normal"
        
    games_played = team_row['P'].values[0]
    rank = team_row.index[0] 
    points = team_row['Pts'].values[0]
    
    if games_played >= 28:
        if rank <= 5:
            return "🔥 High Motivation (Title / Europe Race - ဖလား/ဥရောပဝင်ခွင့် လုနေသည်)"
        elif rank >= 16:
            return "🔥 High Motivation (Relegation Survival - တန်းမဆင်းရရေး ရုန်းကန်နေသည်)"
        else:
            return "🧊 Low Motivation (Mid-table Safe - အေးဆေးဖြစ်နေသော အလယ်အလတ်အဆင့်)"
    
    return "⚡ Normal (Season in Progress - ပုံမှန်အခြေအနေ)"

def analyze_historical_context(team_name, current_odds, is_home, df):
    min_odds = current_odds - 0.3
    max_odds = current_odds + 0.3
    
    if is_home:
        past_matches = df[(df['HomeTeam'] == team_name) & (df['B365H'] >= min_odds) & (df['B365H'] <= max_odds)]
        wins = len(past_matches[past_matches['FTR'] == 'H'])
    else:
        past_matches = df[(df['AwayTeam'] == team_name) & (df['B365A'] >= min_odds) & (df['B365A'] <= max_odds)]
        wins = len(past_matches[past_matches['FTR'] == 'A'])
        
    total_matches = len(past_matches)
    
    if total_matches == 0:
        return "ဤအသင်းအတွက် အလားတူ ပေါက်ကြေးမျိုးဖြင့် အတိတ်တွင် ကစားခဲ့သော မှတ်တမ်း မရှိသေးပါ။"
        
    actual_win_rate = (wins / total_matches) * 100
    implied_prob = (1 / current_odds) * 100
    
    if actual_win_rate >= implied_prob:
        insight = f"✅ **အတိတ်မှတ်တမ်းကောင်းမွန်သည်:** လွန်ခဲ့သော (၅) နှစ်အတွင်း ဤအသင်းသည် အလားတူ ပေါက်ကြေးမျိုးဖြင့် ({total_matches}) ပွဲ ကစားခဲ့ရာ ({wins}) ပွဲ အနိုင်ရခဲ့ပါသည်။ (တကယ့် နိုင်ခြေ: {actual_win_rate:.1f}% | Bookmaker မျှော်မှန်းချက်: {implied_prob:.1f}%)။ အတိတ်က ပေါက်ကြေးကို ကောင်းစွာ အသုံးချနိုင်ခဲ့သည်ကို တွေ့ရသည်။"
    else:
        insight = f"⚠️ **အတိတ်တွင် မှားယွင်းမှုရှိခဲ့သည်:** လွန်ခဲ့သော (၅) နှစ်အတွင်း ဤအသင်းသည် အလားတူ ပေါက်ကြေးမျိုးဖြင့် ({total_matches}) ပွဲ ကစားခဲ့ရာ ({wins}) ပွဲသာ အနိုင်ရခဲ့ပါသည်။ (တကယ့် နိုင်ခြေ: {actual_win_rate:.1f}% သာရှိပြီး Bookmaker မျှော်မှန်းချက် {implied_prob:.1f}% အောက် ရောက်နေပါသည်)။ Bookmaker ၏ ကြေးပေးမှုသည် အတိတ်ကတည်းက ဤအသင်းအတွက် မှားယွင်းတတ်သဖြင့် သတိထားပါ။"
        
    return insight

def predict_goals_poisson(home_xg_for, home_xga, away_xg_for, away_xga):
    lambda_home = (home_xg_for + away_xga) / 2.0
    lambda_away = (away_xg_for + home_xga) / 2.0

    lambda_home = max(0.1, lambda_home)
    lambda_away = max(0.1, lambda_away)

    score_probs = {}
    over_2_5_prob = 0.0
    under_2_5_prob = 0.0

    for h in range(6):
        for a in range(6):
            prob_h = ((lambda_home**h) * math.exp(-lambda_home)) / math.factorial(h)
            prob_a = ((lambda_away**a) * math.exp(-lambda_away)) / math.factorial(a)
            prob = prob_h * prob_a
            
            score_probs[f"{h} - {a}"] = prob
            
            if h + a > 2.5:
                over_2_5_prob += prob
            else:
                under_2_5_prob += prob

    sorted_scores = sorted(score_probs.items(), key=lambda item: item[1], reverse=True)
    top_3_scores = sorted_scores[:3]

    total_ou = over_2_5_prob + under_2_5_prob
    if total_ou > 0:
        over_2_5_pct = (over_2_5_prob / total_ou) * 100
        under_2_5_pct = (under_2_5_prob / total_ou) * 100
    else:
        over_2_5_pct, under_2_5_pct = 50.0, 50.0

    return top_3_scores, over_2_5_pct, under_2_5_pct

# 🌟 ကျန်ခဲ့သော Missing Function (H2H Pattern သုံးသပ်ချက်)
def analyze_specific_fixture_history(home_team, away_team, df):
    h2h_matches = df[((df['HomeTeam'] == home_team) & (df['AwayTeam'] == away_team)) |
                     ((df['HomeTeam'] == away_team) & (df['AwayTeam'] == home_team))].sort_values(by='Date')

    if len(h2h_matches) == 0:
        return "အတိတ်တွင် ဤနှစ်သင်း ထိပ်တိုက်တွေ့ဆုံခဲ့သော မှတ်တမ်းမရှိပါ။"

    total_matches = len(h2h_matches)
    
    home_wins = len(h2h_matches[(h2h_matches['HomeTeam'] == home_team) & (h2h_matches['FTR'] == 'H')]) + \
                len(h2h_matches[(h2h_matches['AwayTeam'] == home_team) & (h2h_matches['FTR'] == 'A')])
    away_wins = len(h2h_matches[(h2h_matches['HomeTeam'] == away_team) & (h2h_matches['FTR'] == 'H')]) + \
                len(h2h_matches[(h2h_matches['AwayTeam'] == away_team) & (h2h_matches['FTR'] == 'A')])
    draws = total_matches - home_wins - away_wins

    recent_h2h = h2h_matches.tail(3)
    recent_trend = []
    for _, row in recent_h2h.iterrows():
        if (row['HomeTeam'] == home_team and row['FTR'] == 'H') or (row['AwayTeam'] == home_team and row['FTR'] == 'A'):
            recent_trend.append(f"{home_team} နိုင်")
        elif row['FTR'] == 'D':
            recent_trend.append("သရေ")
        else:
            recent_trend.append(f"{away_team} နိုင်")

    trend_str = " -> ".join(recent_trend)

    insight = f"စုစုပေါင်း တွေ့ဆုံမှု ({total_matches}) ပွဲတွင် **{home_team} က ({home_wins}) ပွဲနိုင်**၊ **{away_team} က ({away_wins}) ပွဲနိုင်**ပြီး၊ သရေပွဲ ({draws}) ပွဲ ရှိခဲ့ပါသည်။\n\n"

    if home_wins > away_wins * 1.5:
        insight += f"📈 **သုံးသပ်ချက်:** ဤပွဲစဉ်မျိုးတွင် **{home_team} သည် ခြေတက်လေ့ရှိပြီး** {away_team} ကို အသာစီးရထားသည်ကို တွေ့ရသည်။\n"
    elif away_wins > home_wins * 1.5:
        insight += f"📉 **သုံးသပ်ချက်:** {home_team} သည် ဤပွဲစဉ်မျိုးတွင် **ခြေကျတတ်ပြီး (Bogey Team သဖွယ်)** {away_team} ကို အသေအလဲ ရုန်းကန်ရလေ့ရှိသည်။\n"
    elif draws >= home_wins and draws >= away_wins:
        insight += f"🤝 **သုံးသပ်ချက်:** ဤနှစ်သင်းတွေ့ဆုံလျှင် အကြိတ်အနယ်ရှိပြီး **သရေကျလေ့ရှိသော Pattern** ကို တွေ့ရသည်။\n"
    else:
        insight += f"⚖️ **သုံးသပ်ချက်:** နှစ်သင်းစလုံး ခြေရည်တူဖြစ်ပြီး ကြိုတင်ခန့်မှန်းရ ခက်ခဲသော ပွဲစဉ်မျိုးဖြစ်သည်။\n"

    insight += f"\n🔄 **နောက်ဆုံး (၃) ကြိမ် တွေ့ဆုံမှု ရလဒ်များ:** `{trend_str}`"
    
    return insight
    
def calculate_kelly_criterion(true_prob, decimal_odds):
    """
    Kelly Criterion ဖြင့် လောင်းသင့်သော ငွေပမာဏ (ရာခိုင်နှုန်း) ကို တွက်ချက်ခြင်း
    true_prob: AI မှ တွက်ထားသော နိုင်နိုင်ခြေ (0 to 1)
    decimal_odds: Bookmaker ပေးထားသော ပေါက်ကြေး
    """
    # နိုင်လျှင်ရမည့် အမြတ် (Net Odds)
    b = decimal_odds - 1.0 
    
    # Kelly Formula: (bp - q) / b
    # p = နိုင်နိုင်ခြေ, q = ရှုံးနိုင်ခြေ (1 - p)
    p = true_prob
    q = 1.0 - p
    
    if b <= 0:
        return 0.0
        
    kelly_pct = ((b * p) - q) / b
    
    # Value မရှိလျှင် (အနှုတ်ထွက်လျှင်) 0 ဟု သတ်မှတ်မည်
    return max(0.0, kelly_pct * 100)


def predict_goals_poisson(home_xg_for, home_xga, away_xg_for, away_xga):
    """
    Poisson Distribution ကို အသုံးပြု၍ Correct Score, Over/Under 2.5 နှင့် BTTS ကို တွက်ချက်ခြင်း
    """
    lambda_home = (home_xg_for + away_xga) / 2.0
    lambda_away = (away_xg_for + home_xga) / 2.0

    lambda_home = max(0.1, lambda_home)
    lambda_away = max(0.1, lambda_away)

    score_probs = {}
    over_2_5_prob = 0.0
    under_2_5_prob = 0.0
    btts_yes_prob = 0.0 # 🌟 BTTS အတွက် အသစ်တိုးထားသည်

    for h in range(6):
        for a in range(6):
            prob_h = ((lambda_home**h) * math.exp(-lambda_home)) / math.factorial(h)
            prob_a = ((lambda_away**a) * math.exp(-lambda_away)) / math.factorial(a)
            prob = prob_h * prob_a
            
            score_probs[f"{h} - {a}"] = prob
            
            if h + a > 2.5:
                over_2_5_prob += prob
            else:
                under_2_5_prob += prob
                
            # နှစ်သင်းစလုံး ဂိုးရလဒ် 0 ထက်ကြီးပါက BTTS (Yes) ဖြစ်သည်
            if h > 0 and a > 0:
                btts_yes_prob += prob

    sorted_scores = sorted(score_probs.items(), key=lambda item: item[1], reverse=True)
    top_3_scores = sorted_scores[:3]

    total_ou = over_2_5_prob + under_2_5_prob
    if total_ou > 0:
        over_2_5_pct = (over_2_5_prob / total_ou) * 100
        under_2_5_pct = (under_2_5_prob / total_ou) * 100
        btts_yes_pct = (btts_yes_prob / total_ou) * 100 # 🌟 BTTS (Yes) ရာခိုင်နှုန်း
    else:
        over_2_5_pct, under_2_5_pct, btts_yes_pct = 50.0, 50.0, 50.0
        
    btts_no_pct = 100.0 - btts_yes_pct # 🌟 BTTS (No) ရာခိုင်နှုန်း

    # Return ပြန်ပေးသည့်အခါ BTTS များကိုပါ ထည့်ပေးလိုက်သည်
    return top_3_scores, over_2_5_pct, under_2_5_pct, btts_yes_pct, btts_no_pct    