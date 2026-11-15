"""
Page 3: Batter Rankings — Top 10 batters under pressure with 3 comparison rankings & audit.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Batter Rankings — PRESSURE IQ", page_icon="🏏", layout="wide")
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.markdown("# 🏏 Batter Pressure Rankings & Comparative Audit")
st.markdown("*Statistically Defensible Pressure Performance Intelligence System*")
st.markdown("---")

@st.cache_data
def load_data():
    data = {}
    for fname, key in [
        ("batter_rankings.csv", "primary"),
        ("batter_rankings_raw.csv", "raw"),
        ("batter_rankings_uplift.csv", "uplift"),
        ("player_audit_table.csv", "audit"),
        ("all_batter_ratings.csv", "all_batters"),
        ("batting_bootstrap.csv", "bootstrap"),
        ("batting_threshold_sensitivity.csv", "sensitivity"),
    ]:
        fpath = os.path.join(project_root, "outputs", fname)
        if os.path.exists(fpath):
            data[key] = pd.read_csv(fpath)
        else:
            data[key] = None
    return data

data = load_data()

if data["primary"] is None:
    st.error("Please run the pipeline first: `python scripts/run_pipeline.py`")
    st.stop()

primary_df = data["primary"]
raw_df = data["raw"]
uplift_df = data["uplift"]
audit_df = data["audit"]

# Top level metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Top Ranked Batter", primary_df.iloc[0]["player_name"], f"{primary_df.iloc[0]['shrunk_rating']:.4f} Rating")
m2.metric("Leader Pressure SR", f"{primary_df.iloc[0]['strike_rate_pressure']:.1f}", f"+{primary_df.iloc[0]['sr_uplift']:.1f} Uplift")
m3.metric("Leader Pressure Volume", f"{int(primary_df.iloc[0]['balls_faced_pressure'])} balls", f"{int(primary_df.iloc[0]['pressure_matches'])} matches")
m4.metric("Qualifying Sample Floor", "≥ 60 Pressure Balls", "Empirical Bayes N₀=75")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Primary Model (Context-Adjusted + Shrunk)",
    "⚡ Raw Pressure Performance",
    "📈 Pressure Uplift Over Baseline",
    "🔬 Comprehensive Player Audit Table"
])

# -------------------------------------------------------------
# TAB 1: Primary Model
# -------------------------------------------------------------
with tab1:
    st.markdown("### 🏆 Primary Top 10 Batters Under Pressure")
    st.info(
        "**Methodology:** Combines context-adjusted impact per ball ($Actual - Expected$) derived from a GroupKFold "
        "HistGradientBoosting model with strike rate uplift over normal non-pressure deliveries, tempered by Empirical "
        "Bayes shrinkage ($N_0 = 75$ deliveries) and match-level clustering."
    )
    
    display_cols = {
        "rank": "#",
        "player_name": "Player",
        "shrunk_rating": "Rating",
        "strike_rate_pressure": "SR (Pressure)",
        "strike_rate_normal": "SR (Normal)",
        "sr_uplift": "SR Uplift",
        "pressure_uplift": "Impact Uplift",
        "balls_faced_pressure": "Pressure Balls",
        "total_matches": "Matches",
        "pressure_matches": "Pressure Matches",
        "reliability_level": "Reliability",
    }
    avail = {k: v for k, v in display_cols.items() if k in primary_df.columns}
    st.dataframe(primary_df[list(avail.keys())].rename(columns=avail), hide_index=True, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Pressure vs Normal Strike Rate")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=primary_df["player_name"], y=primary_df["strike_rate_pressure"],
            name="Pressure SR", marker_color="#ef4444"
        ))
        fig.add_trace(go.Bar(
            x=primary_df["player_name"], y=primary_df["strike_rate_normal"],
            name="Normal SR", marker_color="#3b82f6"
        ))
        fig.update_layout(
            barmode="group",
            template="plotly_dark",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Rating with 95% Confidence Intervals")
        fig2 = go.Figure()
        error_y = primary_df["rating_se"] * 1.96 if "rating_se" in primary_df.columns else None
        fig2.add_trace(go.Scatter(
            x=primary_df["player_name"],
            y=primary_df["shrunk_rating"],
            mode="markers+lines",
            marker=dict(size=10, color="#10b981"),
            error_y=dict(type='data', array=error_y, visible=True, color="#6ee7b7") if error_y is not None else None,
            name="Shrunk Rating"
        ))
        fig2.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis_title="Shrunk Rating (with 95% CI)"
        )
        st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------------------
# TAB 2: Raw Pressure Performance
# -------------------------------------------------------------
with tab2:
    st.markdown("### ⚡ Ranking Based on Raw Pressure Performance")
    st.warning(
        "**Analytical Limitation:** Raw pressure ranking ranks players solely on their strike rate and raw impact during "
        "high-pressure deliveries. It ignores the player's baseline capabilities and does not shrink small samples towards "
        "the population mean, favoring high-variance finishers with lower sample counts."
    )
    if raw_df is not None:
        raw_disp = {
            "rank_raw": "Raw Rank",
            "player_name": "Player",
            "strike_rate_pressure": "Pressure SR",
            "impact_per_ball_pressure": "Raw Impact/Ball",
            "balls_faced_pressure": "Pressure Balls",
            "pressure_matches": "Pressure Matches"
        }
        avail_raw = {k: v for k, v in raw_disp.items() if k in raw_df.columns}
        st.dataframe(raw_df[list(avail_raw.keys())].rename(columns=avail_raw), hide_index=True, use_container_width=True)
        
        fig_raw = px.scatter(
            raw_df, x="balls_faced_pressure", y="strike_rate_pressure",
            size="pressure_matches", color="impact_per_ball_pressure",
            hover_name="player_name", text="player_name",
            title="Raw Pressure Strike Rate vs Balls Faced",
            template="plotly_dark",
            color_continuous_scale="Viridis"
        )
        fig_raw.update_traces(textposition='top center')
        st.plotly_chart(fig_raw, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: Pressure Uplift Over Baseline
# -------------------------------------------------------------
with tab3:
    st.markdown("### 📈 Ranking Based on Pressure Uplift Over Baseline")
    st.warning(
        "**Analytical Limitation:** Uplift ranking evaluates the difference between a player's pressure strike rate and "
        "their normal baseline ($SR_{pressure} - SR_{normal}$). While intuitive, it inherently rewards players with artificially "
        "low baseline strike rates (anchor bias) rather than absolute match-winning output."
    )
    if uplift_df is not None:
        uplift_disp = {
            "rank_uplift": "Uplift Rank",
            "player_name": "Player",
            "sr_uplift": "SR Uplift",
            "strike_rate_pressure": "Pressure SR",
            "strike_rate_normal": "Normal SR",
            "balls_faced_pressure": "Pressure Balls",
            "balls_faced_normal": "Normal Balls"
        }
        avail_up = {k: v for k, v in uplift_disp.items() if k in uplift_df.columns}
        st.dataframe(uplift_df[list(avail_up.keys())].rename(columns=avail_up), hide_index=True, use_container_width=True)

        fig_up = px.bar(
            uplift_df.head(10), x="player_name", y="sr_uplift",
            color="sr_uplift", color_continuous_scale="Tealgrn",
            title="Top 10 Batters by Strike Rate Uplift (Pressure SR − Normal SR)",
            template="plotly_dark"
        )
        st.plotly_chart(fig_up, use_container_width=True)

# -------------------------------------------------------------
# TAB 4: Comprehensive Player Audit Table
# -------------------------------------------------------------
with tab4:
    st.markdown("### 🔬 Complete Player Audit & Data Traceability")
    st.markdown(
        "Every single metric traced directly to raw ball-by-ball records, context-adjusted expected runs, "
        "runs above expectation, and statistical uncertainty intervals."
    )
    if audit_df is not None:
        bat_audit = audit_df[audit_df["role"] == "Batter"] if "role" in audit_df.columns else audit_df
        st.dataframe(bat_audit, hide_index=True, use_container_width=True)
        
        st.download_button(
            label="📥 Download Full Batter Audit CSV",
            data=bat_audit.to_csv(index=False),
            file_name="batter_audit_table.csv",
            mime="text/csv"
        )
