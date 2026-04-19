# retrain.py
from main_predictor import train_model

SUPPORTED_LEAGUES = [
    "E0.csv",  # Premier League
    "SP1.csv", # La Liga
    "I1.csv",  # Serie A
    "D1.csv",  # Bundesliga
    "F1.csv"   # Ligue 1
]

def retrain_all_models():
    print("🔄 Starting Auto-Retraining for all leagues...")
    
    for league in SUPPORTED_LEAGUES:
        try:
            print(f"⚙️ Retraining model for {league}...")
            # main_predictor ထဲမှ train_model function ကို လှမ်းခေါ်ခြင်း
            train_model(league)
            print(f"✅ Successfully retrained {league}\n")
        except Exception as e:
            print(f"❌ Error retraining {league}: {e}")
            
    print("🎉 All models retrained successfully! Ready for the new week.")

if __name__ == "__main__":
    retrain_all_models()
