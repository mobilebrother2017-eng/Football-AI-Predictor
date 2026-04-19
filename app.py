import streamlit as st
import pandas as pd

# 🌟 API Component အသစ်ကို ခေါ်ယူခြင်း
from live_data_api import get_todays_fixtures 

# Data & Logic Components များကို ခေါ်ယူခြင်း
from data_loader import fetch_and_clean_data
from main_predictor import predict_match
from analysis_engine import (
    get_current_teams, calculate_form_and_trend, calculate_h2h_stats, 
    generate_league_table, calculate_xg_proxy, get_motivation_status,
    analyze_historical_context, predict_goals_poisson, analyze_specific_fixture_history
)

# 🎨 UI Components များကို ခေါ်ယူခြင်း
from ui_components import (
    inject_custom_css, create_donut_chart, render_team_info_cards, 
    render_value_metrics, render_top_scores, create_radar_chart
)

# စာမျက်နှာ အပြင်အဆင် သတ်မှတ်ခြင်း
st.set_page_config(page_title="Pro Football AI Predictor", page_icon="⚽", layout="wide")
inject_custom_css()

# 🌟 မှတ်ဉာဏ်စနစ် (Session States) များ ကြေညာခြင်း
if 'bet_slip' not in st.session_state:
    st.session_state.bet_slip = []
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'last_home' not in st.session_state:
    st.session_state.last_home = ""
if 'last_away' not in st.session_state:
    st.session_state.last_away = ""
# 🌟 API အတွက် မှတ်ဉာဏ်အသစ်
if 'live_list' not in st.session_state:
    st.session_state.live_list = []

# ဥရောပ ထိပ်သီးလိဂ် (၅) ခုစာရင်း[cite: 1]
SUPPORTED_LEAGUES = {
    "🇬🇧 Premier League (England)": "E0.csv",
    "🇪🇸 La Liga (Spain)": "SP1.csv",
    "🇮🇹 Serie A (Italy)": "I1.csv",
    "🇩🇪 Bundesliga (Germany)": "D1.csv",
    "🇫🇷 Ligue 1 (France)": "F1.csv"
}

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1165/1165183.png", width=100)

st.sidebar.header("🌍 Select League")
selected_league_name = st.sidebar.selectbox("Choose a League", list(SUPPORTED_LEAGUES.keys()))
selected_league_code = SUPPORTED_LEAGUES[selected_league_name]

@st.cache_data
def load_cached_data(league_code):
    df = fetch_and_clean_data(league_code)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    return df

data_df = load_cached_data(selected_league_code)

st.title(f"⚽ Elite Analytics - {selected_league_name.split(' (')[0]}")
st.markdown("*Powered by XGBoost Machine Learning & Poisson Distribution*")

tab1, tab2, tab3 = st.tabs(["🎯 AI Match Predictor", "🏆 League Table", "🔗 Accumulator (မောင်းစနစ်)"])

with tab1:
    st.sidebar.markdown("---")
    st.sidebar.header("📋 Match Setup")

    # 🌟 📡 Live API Fixtures Section 🌟
    st.sidebar.subheader("📡 Live Fixtures")
    if st.sidebar.button("🔄 Fetch Today's Matches", use_container_width=True):
        with st.sidebar:
            with st.spinner("Fetching..."):
                live_matches = get_todays_fixtures(selected_league_code)
                if live_matches:
                    st.session_state.live_list = live_matches
                    st.success(f"Found {len(live_matches)} matches!")
                else:
                    st.warning("No matches found for today.")

    teams_list = get_current_teams(data_df)
    
    # 🌟 အသင်းနာမည်များကို API မှရလာသည်များဖြင့် အလိုအလျောက် ချိန်ညှိခြင်း 🌟
    h_idx, a_idx = 0, 1
    if st.session_state.live_list:
        match_options = [m['Match'] for m in st.session_state.live_list]
        selected_live = st.sidebar.selectbox("🎯 Quick Match Select", ["-- Manual Select --"] + match_options)
        
        if selected_live != "-- Manual Select --":
            m_info = next(m for m in st.session_state.live_list if m['Match'] == selected_live)
            # အနီးစပ်ဆုံးတူညီသော အသင်းနာမည်ကို CSV List ထဲမှ ရှာခြင်း
            for i, team in enumerate(teams_list):
                if m_info['Home'] in team or team in m_info['Home']: h_idx = i
                if m_info['Away'] in team or team in m_info['Away']: a_idx = i

    home_team = st.sidebar.selectbox("🏠 Home Team", teams_list, index=h_idx)
    away_team = st.sidebar.selectbox("✈️ Away Team", teams_list, index=a_idx)

    # User က အသင်းတွေကို ပြောင်းရွေးလိုက်ရင် အဟောင်းတွေကို ဖျောက်ရန်[cite: 1]
    if home_team != st.session_state.last_home or away_team != st.session_state.last_away:
        st.session_state.show_results = False

    # Data Calculations[cite: 1]
    auto_home_form, home_trend = calculate_form_and_trend(home_team, data_df)
    auto_away_form, away_trend = calculate_form_and_trend(away_team, data_df)
    auto_h2h, hist_h, hist_d, hist_a = calculate_h2h_stats(home_team, away_team, data_df)
    home_xg_for, home_xg_against = calculate_xg_proxy(home_team, data_df)
    away_xg_for, away_xg_against = calculate_xg_proxy(away_team, data_df)
    league_table = generate_league_table(data_df)
    home_motivation = get_motivation_status(home_team, league_table)
    away_motivation = get_motivation_status(away_team, league_table)

    st.sidebar.markdown("---")
    st.sidebar.header("📊 Live Odds")
    home_odds = st.sidebar.number_input(f"{home_team} Odds", min_value=1.01, value=1.63, step=0.01)
    draw_odds = st.sidebar.number_input("Draw Odds", min_value=1.01, value=3.75, step=0.01)
    away_odds = st.sidebar.number_input(f"{away_team} Odds", min_value=1.01, value=6.00, step=0.01)

    predict_btn = st.sidebar.button("🚀 Run AI Analysis", use_container_width=True)

    if predict_btn:
        if home_team == away_team:
            st.error("⚠️ အိမ်ကွင်း နှင့် အဝေးကွင်း အသင်း တူညီနေပါသည်။")
        else:
            st.session_state.show_results = True
            st.session_state.last_home = home_team
            st.session_state.last_away = away_team

    if st.session_state.show_results:
        with st.spinner(f'Processing data for {home_team} vs {away_team}...'):
            try:
                results = predict_match(home_odds, draw_odds, away_odds, auto_home_form, auto_away_form, auto_h2h, selected_league_code)
                model_prob_h, model_prob_d, model_prob_a = results['Home'], results['Draw'], results['Away']
                true_odds_h = 1 / model_prob_h if model_prob_h > 0 else 0
                true_odds_d = 1 / model_prob_d if model_prob_d > 0 else 0
                true_odds_a = 1 / model_prob_a if model_prob_a > 0 else 0
                
                top_scores, over_25_pct, under_25_pct, btts_yes_pct, btts_no_pct = predict_goals_poisson(
                    home_xg_for, home_xg_against, away_xg_for, away_xg_against
                )
                
                st.markdown(f"## ⚔️ {home_team} vs {away_team}")
                
                # UI Renderings[cite: 1]
                render_team_info_cards(home_team, away_team, home_motivation, away_motivation, 
                                       home_trend, away_trend, auto_home_form, auto_away_form, 
                                       home_xg_for, home_xg_against, away_xg_for, away_xg_against)
                
                # Strength Stats Calculation[cite: 1]
                h_atk = min((home_xg_for / 3.0) * 100, 100)
                a_atk = min((away_xg_for / 3.0) * 100, 100)
                h_def = max(0, 100 - ((home_xg_against / 3.0) * 100))
                a_def = max(0, 100 - ((away_xg_against / 3.0) * 100))
                h_form_pct = (auto_home_form / 15.0) * 100
                a_form_pct = (auto_away_form / 15.0) * 100
                
                def get_mot_score(mot_str):
                    if "High" in mot_str: return 100
                    elif "Normal" in mot_str: return 60
                    else: return 30
                
                h_h2h_pct = auto_h2h * 100
                a_h2h_pct = (1.0 - auto_h2h) * 100 if auto_h2h > 0 else 50
                
                home_radar_stats = [h_atk, h_def, h_form_pct, get_mot_score(home_motivation), h_h2h_pct]
                away_radar_stats = [a_atk, a_def, a_form_pct, get_mot_score(away_motivation), a_h2h_pct]
                
                st.markdown("### 🕸️ Team Strength Comparison")
                fig_radar = create_radar_chart(home_team, away_team, home_radar_stats, away_radar_stats)
                st.plotly_chart(fig_radar, use_container_width=True)
                
                st.markdown("### ⚔️ Fixture History Analysis")
                st.info(analyze_specific_fixture_history(home_team, away_team, data_df))

                render_value_metrics(home_odds, true_odds_h, model_prob_h)
                
                # Betting Insights[cite: 1]
                if true_odds_h > home_odds:
                    st.error(f"🚫 **AVOID BET:** Negative Value! Real odds: {true_odds_h:.2f}, Bookie: {home_odds}.")
                elif "High Motivation" in home_motivation and "Low Motivation" in away_motivation:
                    st.success(f"🔥 **HIGH CONFIDENCE:** Motivation advantage for {home_team}.")
                elif true_odds_h < home_odds and home_xg_for > away_xg_for:
                    st.success(f"💎 **VALUE BET DETECTED:** superior attacking for {home_team}.")
                else:
                    st.warning("⚖️ **NO CLEAR EDGE:** Odds are accurately priced.")

                st.markdown("---")
                
                # Donut Charts[cite: 1]
                st.markdown("### 📊 AI Match Predictions")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.plotly_chart(create_donut_chart([model_prob_h, model_prob_d, model_prob_a], 
                        [f'{home_team}', 'Draw', f'{away_team}'], ['#1E88E5', '#757575', '#E53935'], "Outcome"), use_container_width=True)
                with c2:
                    st.plotly_chart(create_donut_chart([over_25_pct, under_25_pct], 
                        ['Over 2.5', 'Under 2.5'], ['#00E676', '#FF9100'], "O/U 2.5"), use_container_width=True)
                with c3:
                    st.plotly_chart(create_donut_chart([btts_yes_pct, btts_no_pct], 
                        ['BTTS: Yes', 'BTTS: No'], ['#B2FF59', '#FF5252'], "BTTS"), use_container_width=True)

                render_top_scores(top_scores)
                        
                with st.expander("🕰️ AI Historical Backtesting"):
                    st.info(f"**{home_team}:** {analyze_historical_context(home_team, home_odds, True, data_df)}")
                    st.info(f"**{away_team}:** {analyze_historical_context(away_team, away_odds, False, data_df)}")

                st.markdown("---")
                
                # Accumulator Logic[cite: 1]
                st.markdown("### ➕ Add to Accumulator")
                acc1, acc2, acc3 = st.columns(3)
                if acc1.button(f"Add {home_team} (Home)", key="h"):
                    st.session_state.bet_slip.append({"Match": f"{home_team} vs {away_team}", "Pick": home_team, "Bookie Odds": home_odds, "AI True Odds": true_odds_h, "Probability (%)": model_prob_h * 100})
                    st.toast("Added Home Win!")
                if acc2.button("Add Draw (သရေ)", key="d"):
                    st.session_state.bet_slip.append({"Match": f"{home_team} vs {away_team}", "Pick": "Draw", "Bookie Odds": draw_odds, "AI True Odds": true_odds_d, "Probability (%)": model_prob_d * 100})
                    st.toast("Added Draw!")
                if acc3.button(f"Add {away_team} (Away)", key="a"):
                    st.session_state.bet_slip.append({"Match": f"{home_team} vs {away_team}", "Pick": away_team, "Bookie Odds": away_odds, "AI True Odds": true_odds_a, "Probability (%)": model_prob_a * 100})
                    st.toast("Added Away Win!")

            except Exception as e:
                st.error(f"Analysis Error: {e}")

with tab2:
    st.subheader(f"🏆 {selected_league_name.split(' (')[0]} Standings")
    st.dataframe(generate_league_table(data_df), use_container_width=True)

with tab3:
    st.subheader("🔗 Accumulator Builder")
    if not st.session_state.bet_slip:
        st.info("📥 မောင်းထဲတွင် ပွဲမရှိသေးပါ။")
    else:
        slip_df = pd.DataFrame(st.session_state.bet_slip)
        st.dataframe(slip_df, use_container_width=True)
        
        t_bookie = slip_df['Bookie Odds'].prod()
        t_ai = slip_df['AI True Odds'].prod()
        t_prob = (slip_df['Probability (%)'] / 100).prod() * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Bookmaker Odds", f"{t_bookie:.2f}")
        c2.metric("Total AI True Odds", f"{t_ai:.2f}")
        c3.metric("Combined Win Prob", f"{t_prob:.2f}%")
        
        if t_bookie > t_ai: st.success("🔥 **Value Accumulator!**")
        else: st.error("⚠️ **Negative Value!**")
            
        if st.button("🗑️ Clear Accumulator"):
            st.session_state.bet_slip = []
            st.rerun()
