"""
Page 4: Bowler Rankings — Top 10 bowlers under pressure with 3 comparison rankings & audit.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Bowler Rankings — PRESSURE IQ", page_icon="🎯", layout="wide")
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.markdown("# 🎯 Bowler Pressure Rankings & Comparative Audit")
st.markdown("*Statistically Defensible Bowling Performance Under High Leverage*")
st.markdown("---")

@st.cache_data
def load_data():
    data = {}
    for fname, key in [
        ("bowler_rankings.csv", "primary"),
        ("bowler_rankings_raw.csv", "raw"),
        ("bowler_rankings_uplift.csv", "uplift"),
        ("player_audit_table.csv", "audit"),
        ("all_bowler_ratings.csv", "all_bowlers"),
        ("bowling_bootstrap.csv", "bootstrap"),
        ("bowling_threshold_sensitivity.csv", "sensitivity"),
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
m1.metric("Top Ranked Bowler", primary_df.iloc[0]["player_name"], f"{primary_df.iloc[0]['shrunk_rating']:.4f} Rating")
m2.metric("Leader Pressure Economy", f"{primary_df.iloc[0]['economy_pressure']:.2f} RPO", f"{primary_df.iloc[0]['economy_improvement']:+.2f} RPO Imprv")
m3.metric("Leader Pressure Volume", f"{int(primary_df.iloc[0]['legal_balls_pressure'])} balls", f"{int(primary_df.iloc[0]['bowler_wickets_pressure'])} Wickets")
m4.metric("Qualifying Sample Floor", "≥ 60 Legal Pressure Balls", "Empirical Bayes N₀=75")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Primary Model (Context-Adjusted + Shrunk)",
    "⚡ Raw Pressure Performance",
    "📈 Pressure Economy Uplift Over Baseline",
    "🔬 Comprehensive Player Audit Table"
])

# -------------------------------------------------------------
# TAB 1: Primary Model
# -------------------------------------------------------------
with tab1:
    st.markdown("### 🏆 Primary Top 10 Bowlers Under Pressure")
    st.info(
        "**Methodology:** Evaluates context-adjusted runs saved per ball ($Expected - Actual$) using out-of-sample "
        "GroupKFold predictions, bowling economy improvement over normal baseline, and high-leverage wicket taking, "
        "stabilized via Empirical Bayes shrinkage ($N_0 = 75$ deliveries)."
    )
    
    display_cols = {
        "rank": "#",
        "player_name": "Player",
        "shrunk_rating": "Rating",
        "economy_pressure": "Econ (Pressure)",
        "economy_normal": "Econ (Normal)",
        "economy_improvement": "Econ Imprv",
        "bowler_wickets_pressure": "Pressure Wickets",
        "legal_balls_pressure": "Pressure Balls",
        "total_matches": "Matches",
        "pressure_matches": "Pressure Matches",
        "reliability_level": "Reliability",
    }
    avail = {k: v for k, v in display_cols.items() if k in primary_df.columns}
    st.dataframe(primary_df[list(avail.keys())].rename(columns=avail), hide_index=True, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Pressure vs Normal Economy Rate")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=primary_df["player_name"], y=primary_df["economy_pressure"],
            name="Pressure Economy", marker_color="#ef4444"
        ))
        fig.add_trace(go.Bar(
            x=primary_df["player_name"], y=primary_df["economy_normal"],
            name="Normal Economy", marker_color="#3b82f6"
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
            marker=dict(size=10, color="#38bdf8"),
            error_y=dict(type='data', array=error_y, visible=True, color="#93c5fd") if error_y is not None else None,
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
    st.markdown("### ⚡ Ranking Based on Raw Pressure Economy")
    st.warning(
        "**Analytical Limitation:** Raw pressure ranking orders bowlers strictly by lowest economy rate in high-pressure "
        "deliveries. It does not adjust for whether the bowler delivered in high-scoring venues, their normal baseline, "
        "or small sample noise."
    )
    if raw_df is not None:
        raw_disp = {
            "rank_raw": "Raw Rank",
            "player_name": "Player",
            "economy_pressure": "Pressure Economy",
            "impact_per_ball_pressure": "Raw Impact/Ball",
            "bowler_wickets_pressure": "Wickets",
            "legal_balls_pressure": "Pressure Balls",
            "pressure_matches": "Pressure Matches"
        }
        avail_raw = {k: v for k, v in raw_disp.items() if k in raw_df.columns}
        st.dataframe(raw_df[list(avail_raw.keys())].rename(columns=avail_raw), hide_index=True, use_container_width=True)

        fig_raw = px.scatter(
            raw_df, x="legal_balls_pressure", y="economy_pressure",
            size="bowler_wickets_pressure", color="impact_per_ball_pressure",
            hover_name="player_name", text="player_name",
            title="Raw Pressure Economy vs Legal Balls Bowled",
            template="plotly_dark",
            color_continuous_scale="Plasma"
        )
        fig_raw.update_traces(textposition='top center')
        st.plotly_chart(fig_raw, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: Pressure Economy Uplift Over Baseline
# -------------------------------------------------------------
with tab3:
    st.markdown("### 📈 Ranking Based on Economy Improvement Over Baseline")
    st.warning(
        "**Analytical Limitation:** Uplift ranking rewards bowlers who reduce their economy the most between normal "
        "overs and pressure overs ($Econ_{normal} - Econ_{pressure}$). This favors bowlers with unusually high normal "
        "economies over steady elite performers like Sunil Narine whose baseline economy is already ultra-stingy."
    )
    if uplift_df is not None:
        uplift_disp = {
            "rank_uplift": "Uplift Rank",
            "player_name": "Player",
            "economy_improvement": "Econ Improvement (RPO)",
            "economy_pressure": "Pressure Econ",
            "economy_normal": "Normal Econ",
            "legal_balls_pressure": "Pressure Balls",
            "legal_balls_normal": "Normal Balls"
        }
        avail_up = {k: v for k, v in uplift_disp.items() if k in uplift_df.columns}
        st.dataframe(uplift_df[list(avail_up.keys())].rename(columns=avail_up), hide_index=True, use_container_width=True)

        fig_up = px.bar(
            uplift_df.head(10), x="player_name", y="economy_improvement",
            color="economy_improvement", color_continuous_scale="Tealgrn",
            title="Top 10 Bowlers by Economy Improvement (Normal Econ − Pressure Econ)",
            template="plotly_dark"
        )
        st.plotly_chart(fig_up, use_container_width=True)

# -------------------------------------------------------------
# TAB 4: Comprehensive Player Audit Table
# -------------------------------------------------------------
with tab4:
    st.markdown("### 🔬 Complete Player Audit & Data Traceability")
    st.markdown(
        "Complete verification tracing every bowler back to ball-by-ball deliveries, normal vs pressure overs, "
        "bowler-credited wickets, and shrinkage reliability metrics."
    )
    if audit_df is not None:
        bowl_audit = audit_df[audit_df["role"] == "Bowler"] if "role" in audit_df.columns else audit_df
        st.dataframe(bowl_audit, hide_index=True, use_container_width=True)
        
        st.download_button(
            label="📥 Download Full Bowler Audit CSV",
            data=bowl_audit.to_csv(index=False),
            file_name="bowler_audit_table.csv",
            mime="text/csv"
        )
