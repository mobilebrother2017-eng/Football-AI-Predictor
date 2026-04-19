import streamlit as st
import plotly.graph_objects as go
from analysis_engine import calculate_kelly_criterion

def inject_custom_css():
    st.markdown("""
        <style>
        /* 🌟 ခလုတ်များကို 3D Glowing Effect ဖြစ်စေရန် */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #1cb5e0 0%, #000851 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 800;
            padding: 0.6rem 1.2rem;
            transition: all 0.3s ease 0s;
        }
        div.stButton > button:first-child:hover {
            box-shadow: 0px 10px 20px rgba(28, 181, 224, 0.4);
            transform: translateY(-3px); /* နှိပ်လိုက်လျှင် အပေါ်သို့ အနည်းငယ်ကြွတက်လာမည် */
            color: #00FF00;
        }

        /* 🌟 Metrics များ (Odds အကွက်များ) ကို မှန်ကဲ့သို့ ကြည်လင်သော Glassmorphism Effect ပေးရန် */
        div[data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* 🌟 အဓိက ခေါင်းစဉ်များကို Gradient အရောင်ပြောင်းရန် */
        h1, h2, h3 {
            background: -webkit-linear-gradient(#00C9FF, #92FE9D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

def create_donut_chart(probs, labels, colors, title):
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=probs, hole=.55, marker_colors=colors,
        textinfo='label+percent', textposition='inside', insidetextorientation='radial',
        textfont_size=12
    )])
    fig.update_layout(
        title_text=title, title_x=0.5, title_font_size=15, template='plotly_dark',
        margin=dict(t=35, b=10, l=10, r=10), height=280, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def render_team_info_cards(home_team, away_team, h_mot, a_mot, h_trend, a_trend, h_pts, a_pts, h_xg, h_xga, a_xg, a_xga):
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**🏠 {home_team} (Home)**\n\n🎯 Motivation: {h_mot}\n\n📈 Form: `{h_trend}` ({h_pts} Pts)\n\n⚽ xG: {h_xg} | 🛡️ xGA: {h_xga}")
    with c2:
        st.info(f"**✈️ {away_team} (Away)**\n\n🎯 Motivation: {a_mot}\n\n📉 Form: `{a_trend}` ({a_pts} Pts)\n\n⚽ xG: {a_xg} | 🛡️ xGA: {a_xga}")

def render_value_metrics(home_odds, true_odds_h, true_prob_h):
    st.markdown("### 💸 Value & Betting Analysis")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Live Odds (Bookie)", f"{home_odds}")
    col2.metric("True Odds (AI)", f"{true_odds_h:.2f}")
    
    odds_diff = home_odds - true_odds_h
    col3.metric("Value Edge", f"{odds_diff:.2f}", delta=f"{odds_diff:.2f}")
    
    kelly_rec = calculate_kelly_criterion(true_prob_h, home_odds)
    if kelly_rec > 0:
        safe_kelly = kelly_rec / 2
        col4.metric("Kelly Stake (Rec. Bet)", f"{safe_kelly:.1f}%", delta="Bankroll", delta_color="normal")
    else:
        col4.metric("Kelly Stake (Rec. Bet)", "0.0%", delta="No Value", delta_color="inverse")

def render_top_scores(top_scores):
    st.markdown("### 🎯 Top 3 Correct Score Predictions")
    score_cols = st.columns(3)
    for i, (score, prob) in enumerate(top_scores):
        with score_cols[i]:
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            st.markdown(f"""
            <div style="background-color:#1E2130; padding:20px; border-radius:10px; text-align:center; box-shadow: 0 4px 8px rgba(0,0,0,0.5);">
                <h2 style="color:#00E676; margin-bottom:0;">{medal} {score}</h2>
                <p style="color:gray;">Probability: <b>{prob * 100:.1f}%</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            
# ui_components.py ၏ အောက်ဆုံးတွင် ထည့်ရန်

def create_radar_chart(home_team, away_team, home_stats, away_stats):
    """အသင်းနှစ်သင်း၏ အချက်အလက် ၅ ခုကို ယှဉ်ပြမည့် Radar (Spider) Chart"""
    categories = ['Attacking (xG)', 'Defending (xGA)', 'Current Form', 'Motivation', 'H2H Dominance']
    
    fig = go.Figure()
    
    # Home Team အတွက် (အစိမ်းရောင်)
    fig.add_trace(go.Scatterpolar(
        r=home_stats,
        theta=categories,
        fill='toself',
        name=home_team,
        line_color='#00E676',
        fillcolor='rgba(0, 230, 118, 0.4)' # အကြည်ရောင်
    ))
    
    # Away Team အတွက် (အနီရောင်)
    fig.add_trace(go.Scatterpolar(
        r=away_stats,
        theta=categories,
        fill='toself',
        name=away_team,
        line_color='#E53935',
        fillcolor='rgba(229, 57, 53, 0.4)' # အကြည်ရောင်
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color='gray') # 0 မှ 100 ရာခိုင်နှုန်းထိ
        ),
        showlegend=True,
        template='plotly_dark',
        margin=dict(t=40, b=30, l=30, r=30),
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    
    return fig            
