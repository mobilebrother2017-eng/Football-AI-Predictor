import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import xgboost as xgb
import joblib
import os

from data_loader import fetch_and_clean_data
from feature_engineering import preprocess_data

FEATURE_NAMES = [
    'B365H', 'B365D', 'B365A', 
    'Implied_Prob_H', 'Implied_Prob_D', 'Implied_Prob_A',
    'Home_Team_Form', 'Away_Team_Form', 'H2H_Home_Win_Rate'
]

def train_model(league_code="E0.csv"):
    """League အလိုက် သီးသန့် XGBoost Model တစ်ခုစီ Train ခြင်း"""
    model_filename = f"xgb_model_{league_code.replace('.csv', '')}.pkl"
    print(f"🔄 {league_code} အတွက် Historical Data များကို ဆွဲယူနေပါသည်...")
    
    raw_data = fetch_and_clean_data(league_code)
    
    if raw_data.empty:
        return None

    processed_data = preprocess_data(raw_data)
    processed_data = processed_data.dropna(subset=FEATURE_NAMES + ['Target'])
    
    X = processed_data[FEATURE_NAMES]
    y = processed_data['Target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBClassifier(
        objective='multi:softprob', num_class=3, learning_rate=0.05,
        max_depth=5, n_estimators=200, subsample=0.8, colsample_bytree=0.8, random_state=42
    )
    
    model.fit(X_train, y_train)
    joblib.dump(model, model_filename)
    return model

def predict_match(home_odds, draw_odds, away_odds, home_form, away_form, h2h_rate, league_code="E0.csv"):
    """ရွေးချယ်ထားသော League ၏ Model ကိုပြန်ခေါ်၍ တွက်ချက်ခြင်း"""
    model_filename = f"xgb_model_{league_code.replace('.csv', '')}.pkl"
    
    if not os.path.exists(model_filename):
        model = train_model(league_code)
    else:
        model = joblib.load(model_filename)
        
    implied_h = 1 / home_odds
    implied_d = 1 / draw_odds
    implied_a = 1 / away_odds
    
    input_df = pd.DataFrame([[
        home_odds, draw_odds, away_odds, implied_h, implied_d, implied_a, 
        home_form, away_form, h2h_rate
    ]], columns=FEATURE_NAMES)
    
    probabilities = model.predict_proba(input_df)[0]
    
    return {
        "Home": float(probabilities[0]),
        "Draw": float(probabilities[1]),
        "Away": float(probabilities[2])
    }