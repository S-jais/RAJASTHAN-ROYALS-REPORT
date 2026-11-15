"""
PRESSURE IQ — Cricket Performance Intelligence
SupeRR Selector Season 2

Main Streamlit application entry point.
"""
import streamlit as st
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

st.set_page_config(
    page_title="PRESSURE IQ — Cricket Performance Intelligence",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium dark theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #121829 50%, #0d1117 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1220 0%, #151d30 100%);
        border-right: 1px solid #1e2d4a;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #e8edf5 !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #141b2d 0%, #1a2332 100%);
        border: 1px solid #1e2d4a;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    [data-testid="stMetricValue"] {
        color: #4ade80 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* DataFrames */
    .stDataFrame {
        border: 1px solid #1e2d4a;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1a5c2e 0%, #22763a 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #22763a 0%, #2d9a4e 100%);
        box-shadow: 0 4px 12px rgba(34, 118, 58, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #141b2d;
        border: 1px solid #1e2d4a;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1a5c2e 0%, #22763a 100%) !important;
        color: white !important;
        border-color: #22763a !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: #141b2d;
        border: 1px solid #1e2d4a;
        border-radius: 8px;
    }
    
    /* Custom classes */
    .pressure-high { color: #ef4444; font-weight: 700; }
    .pressure-normal { color: #4ade80; font-weight: 700; }
    .pressure-mid { color: #fbbf24; font-weight: 700; }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4ade80 0%, #22d3ee 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        margin-bottom: 0;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #64748b;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: -8px;
    }
    
    .rank-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1a5c2e 0%, #22763a 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .card {
        background: linear-gradient(135deg, #141b2d 0%, #1a2332 100%);
        border: 1px solid #1e2d4a;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    /* Divider */
    hr {
        border-color: #1e2d4a !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<p class="hero-title" style="font-size: 1.8rem;">PRESSURE IQ</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle" style="font-size: 0.75rem;">Cricket Performance Intelligence</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**SupeRR Selector Season 2**")
    st.markdown("*Identifying reliable players under pressure*")
    st.markdown("---")
    st.markdown("### Navigation")
    st.markdown("""
    Use the sidebar pages to explore:
    - 👑 **RR Auction Strategy 2027** — IPL 2027 Auction & Player Fits
    - 📊 **Overview** — Key metrics
    - 🔍 **Pressure Explorer** — Ball-level analysis
    - 🏏 **Batter Rankings** — Top 10 batters (3 models)
    - 🎯 **Bowler Rankings** — Top 10 bowlers (3 models)
    - 👤 **Player Intelligence** — Individual profiles
    - 📈 **Model Validation** — Statistical checks
    - 📖 **Methodology** — How it works
    """)

# Main page content
st.markdown('<p class="hero-title">PRESSURE IQ</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Cricket Performance Intelligence — SupeRR Selector Season 2</p>', unsafe_allow_html=True)

# RR 2027 Auction Banner
st.markdown("""
<div style="background: linear-gradient(135deg, #0B1B3D 0%, #1E3A8A 50%, #D81B60 100%); padding: 16px 20px; border-radius: 10px; margin-top: 15px; margin-bottom: 20px; border-left: 5px solid #FFB703;">
    <span style="font-size: 18px; font-weight: 700; color: #FFFFFF;">👑 RAJASTHAN ROYALS: IPL 2027 AUCTION INTELLIGENCE DOSSIER</span><br/>
    <span style="font-size: 13px; color: #E2E8F0;">Complete tactical analysis on how the Top 10 Pressure Batters and Bowlers strengthen Rajasthan Royals' squad. Explore via <b>Page 8 (RR Auction Strategy 2027)</b> or download the official PDF & PPT deliverables in <code>outputs/</code>.</span>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Load data
@st.cache_data
def load_dashboard_data():
    """Load processed data for the dashboard."""
    import pandas as pd
    import json
    
    processed_dir = os.path.join(project_root, "data", "processed")
    output_dir = os.path.join(project_root, "outputs")
    
    data = {}
    
    try:
        data["full_df"] = pd.read_parquet(os.path.join(processed_dir, "full_processed_data.parquet"))
    except:
        data["full_df"] = None
    
    try:
        data["player_registry"] = pd.read_csv(
            os.path.join(processed_dir, "player_registry.csv")
        ).set_index("player_id")["player_name"].to_dict()
    except:
        data["player_registry"] = {}
    
    try:
        data["batter_rankings"] = pd.read_csv(os.path.join(output_dir, "batter_rankings.csv"))
    except:
        data["batter_rankings"] = None
    
    try:
        data["bowler_rankings"] = pd.read_csv(os.path.join(output_dir, "bowler_rankings.csv"))
    except:
        data["bowler_rankings"] = None
    
    try:
        data["all_batters"] = pd.read_csv(os.path.join(output_dir, "all_batter_ratings.csv"))
    except:
        data["all_batters"] = None
    
    try:
        data["all_bowlers"] = pd.read_csv(os.path.join(output_dir, "all_bowler_ratings.csv"))
    except:
        data["all_bowlers"] = None
    
    try:
        with open(os.path.join(output_dir, "pressure_analysis.json")) as f:
            data["pressure_analysis"] = json.load(f)
    except:
        data["pressure_analysis"] = None
    
    try:
        with open(os.path.join(output_dir, "model_validation.json")) as f:
            data["model_validation"] = json.load(f)
    except:
        data["model_validation"] = None
    
    try:
        data["bat_bootstrap"] = pd.read_csv(os.path.join(output_dir, "batting_bootstrap.csv"))
    except:
        data["bat_bootstrap"] = None
    
    try:
        data["bowl_bootstrap"] = pd.read_csv(os.path.join(output_dir, "bowling_bootstrap.csv"))
    except:
        data["bowl_bootstrap"] = None
    
    return data


data = load_dashboard_data()

if data["pressure_analysis"] is None:
    st.error("⚠️ Pipeline has not been run yet. Please run `python scripts/run_pipeline.py` first.")
    st.info("This will process the raw data, calculate pressure indices, build models, and generate rankings.")
    st.stop()

pa = data["pressure_analysis"]

# Overview metrics
st.markdown("### 📊 Key Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Matches", f"{pa.get('total_matches', 0):,}")
c2.metric("Total Deliveries", f"{pa.get('total_deliveries', 0):,}")
c3.metric("Unique Batters", f"{pa.get('total_batters', 0):,}")
c4.metric("Unique Bowlers", f"{pa.get('total_bowlers', 0):,}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("High Pressure Balls", f"{pa.get('high_pressure_deliveries', 0):,}")
c6.metric("Mean Pressure Index", f"{pa.get('mean_pressure_index', 0):.3f}")
c7.metric("Seasons", f"{len(pa.get('seasons', []))}")
c8.metric("Competitions", f"{len(pa.get('competitions', []))}")

st.markdown("---")

# Quick Top 10 summaries
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 🏏 Top 10 Batters Under Pressure")
    if data["batter_rankings"] is not None:
        display_cols = ["rank", "player_name", "shrunk_rating", "strike_rate_pressure", 
                       "strike_rate_normal", "sr_uplift", "balls_faced_pressure"]
        available = [c for c in display_cols if c in data["batter_rankings"].columns]
        st.dataframe(
            data["batter_rankings"][available].rename(columns={
                "shrunk_rating": "Rating",
                "strike_rate_pressure": "SR (Pressure)",
                "strike_rate_normal": "SR (Normal)",
                "sr_uplift": "SR Uplift",
                "balls_faced_pressure": "Pressure Balls",
                "player_name": "Player",
                "rank": "#"
            }),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.warning("Batter rankings not available")

with col_right:
    st.markdown("### 🎯 Top 10 Bowlers Under Pressure")
    if data["bowler_rankings"] is not None:
        display_cols = ["rank", "player_name", "shrunk_rating", "economy_pressure",
                       "economy_normal", "economy_improvement", "legal_balls_pressure"]
        available = [c for c in display_cols if c in data["bowler_rankings"].columns]
        st.dataframe(
            data["bowler_rankings"][available].rename(columns={
                "shrunk_rating": "Rating",
                "economy_pressure": "Econ (Pressure)",
                "economy_normal": "Econ (Normal)",
                "economy_improvement": "Econ Improvement",
                "legal_balls_pressure": "Pressure Balls",
                "player_name": "Player",
                "rank": "#"
            }),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.warning("Bowler rankings not available")

st.markdown("---")

# Pressure Distribution
if data["full_df"] is not None:
    import plotly.express as px
    import plotly.graph_objects as go
    
    st.markdown("### 📈 Pressure Index Distribution")
    
    df = data["full_df"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            df.sample(min(50000, len(df))),
            x="pressure_index",
            nbins=50,
            color="pressure_category",
            color_discrete_map={"high": "#ef4444", "normal": "#4ade80", "intermediate": "#fbbf24"},
            title="Pressure Index Distribution by Category",
            template="plotly_dark",
        )
        fig.update_layout(
            plot_bgcolor="rgba(20,27,45,0.8)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8edf5",
            title_font_size=16,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        phase_pressure = df.groupby("innings_phase")["pressure_index"].mean().reset_index()
        fig2 = px.bar(
            phase_pressure,
            x="innings_phase",
            y="pressure_index",
            title="Mean Pressure by Innings Phase",
            template="plotly_dark",
            color="pressure_index",
            color_continuous_scale=["#4ade80", "#fbbf24", "#ef4444"],
        )
        fig2.update_layout(
            plot_bgcolor="rgba(20,27,45,0.8)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8edf5",
            title_font_size=16,
        )
        st.plotly_chart(fig2, use_container_width=True)

