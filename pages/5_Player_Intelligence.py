"""
Page 5: Player Intelligence — Detailed individual player profiles.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="Player Intelligence — PRESSURE IQ", page_icon="👤", layout="wide")
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.markdown("# 👤 Player Intelligence")
st.markdown("*Deep dive into individual player pressure performance*")
st.markdown("---")

@st.cache_data
def load_data():
    data = {}
    try:
        data["df"] = pd.read_parquet(os.path.join(project_root, "data", "processed", "full_processed_data.parquet"))
        data["registry"] = pd.read_csv(
            os.path.join(project_root, "data", "processed", "player_registry.csv")
        ).set_index("player_id")["player_name"].to_dict()
    except:
        data["df"] = None
        data["registry"] = {}
    try:
        data["all_batters"] = pd.read_csv(os.path.join(project_root, "outputs", "all_batter_ratings.csv"))
    except:
        data["all_batters"] = None
    try:
        data["all_bowlers"] = pd.read_csv(os.path.join(project_root, "outputs", "all_bowler_ratings.csv"))
    except:
        data["all_bowlers"] = None
    return data

data = load_data()

if data["df"] is None:
    st.error("Run the pipeline first: `python scripts/run_pipeline.py`")
    st.stop()

df = data["df"]
registry = data["registry"]

# Player selection
all_player_names = sorted(set(registry.values()))
selected_player = st.selectbox("Select Player", all_player_names, index=0)

if not selected_player:
    st.stop()

# Find player ID(s)
player_ids = [pid for pid, pname in registry.items() if pname == selected_player]

if not player_ids:
    st.warning("Player not found in registry")
    st.stop()

pid = player_ids[0]

# Get batting and bowling data
bat_data = df[df["striker_id"] == pid]
bowl_data = df[df["bowler_id"] == pid]

st.markdown(f"## {selected_player}")
st.markdown(f"*Player ID: {pid}*")

# Tabs
tab_bat, tab_bowl = st.tabs(["🏏 Batting", "🎯 Bowling"])

with tab_bat:
    if len(bat_data[bat_data["ball_faced"] == 1]) == 0:
        st.info("No batting data available for this player")
    else:
        bat_faced = bat_data[bat_data["ball_faced"] == 1]
        
        # Summary stats
        c1, c2, c3, c4, c5 = st.columns(5)
        total_runs = bat_faced["batter_runs"].sum()
        total_balls = len(bat_faced)
        total_matches = bat_faced["match_id"].nunique()
        sr = total_runs / total_balls * 100 if total_balls > 0 else 0
        
        c1.metric("Total Runs", f"{total_runs:,}")
        c2.metric("Balls Faced", f"{total_balls:,}")
        c3.metric("Strike Rate", f"{sr:.1f}")
        c4.metric("Matches", f"{total_matches}")
        c5.metric("Fours/Sixes", f"{bat_faced['is_four'].sum()}/{bat_faced['is_six'].sum()}")
        
        # Pressure vs Normal breakdown
        st.markdown("### Pressure vs Normal Performance")
        
        pressure_bat = bat_faced[bat_faced["pressure_category"] == "high"]
        normal_bat = bat_faced[bat_faced["pressure_category"] == "normal"]
        
        comp_data = {
            "Metric": ["Balls Faced", "Runs", "Strike Rate", "Avg", "Boundary %", "Dot %", "Matches"],
        }
        
        for label, subset in [("Pressure", pressure_bat), ("Normal", normal_bat), ("Overall", bat_faced)]:
            balls = len(subset)
            runs = subset["batter_runs"].sum()
            sr_val = runs / balls * 100 if balls > 0 else 0
            dismissed = (subset["is_wicket"] & (subset["dismissed_player_id"] == subset["striker_id"])).sum()
            avg_val = runs / dismissed if dismissed > 0 else runs
            boundary_pct = (subset["is_four"].sum() + subset["is_six"].sum()) / balls * 100 if balls > 0 else 0
            dot_pct = subset["is_dot"].sum() / balls * 100 if balls > 0 else 0
            matches = subset["match_id"].nunique()
            
            comp_data[label] = [balls, runs, f"{sr_val:.1f}", f"{avg_val:.1f}", 
                               f"{boundary_pct:.1f}%", f"{dot_pct:.1f}%", matches]
        
        st.dataframe(pd.DataFrame(comp_data), hide_index=True, use_container_width=True)
        
        # Pressure performance across matches
        st.markdown("### Match-by-Match Pressure Performance")
        match_perf = pressure_bat.groupby("match_id").agg(
            runs=("batter_runs", "sum"),
            balls=("ball_faced", "sum"),
            mean_pi=("pressure_index", "mean"),
        ).reset_index()
        match_perf["sr"] = match_perf["runs"] / match_perf["balls"] * 100
        
        if len(match_perf) > 0:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=list(range(1, len(match_perf)+1)),
                y=match_perf["sr"],
                marker_color=np.where(match_perf["sr"] >= sr, "#4ade80", "#ef4444"),
                name="Pressure SR"
            ))
            fig.add_hline(y=sr, line_dash="dash", line_color="#fbbf24",
                         annotation_text=f"Overall SR: {sr:.1f}")
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e8edf5", height=350,
                xaxis_title="Match #", yaxis_title="Strike Rate (Pressure Balls)",
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # PI distribution for this batter
        st.markdown("### Pressure Index Distribution")
        fig = px.histogram(
            bat_faced, x="pressure_index", nbins=30,
            color="pressure_category",
            color_discrete_map={"high": "#ef4444", "normal": "#4ade80", "intermediate": "#fbbf24"},
            template="plotly_dark",
        )
        fig.update_layout(
            plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8edf5", height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance by over
        st.markdown("### Performance by Over Number")
        over_perf = bat_faced.groupby("overid").agg(
            runs=("batter_runs", "sum"),
            balls=("ball_faced", "sum"),
        ).reset_index()
        over_perf["sr"] = over_perf["runs"] / over_perf["balls"] * 100
        
        fig = px.bar(
            over_perf, x="overid", y="sr",
            template="plotly_dark", color="sr",
            color_continuous_scale=["#ef4444", "#fbbf24", "#4ade80"],
        )
        fig.update_layout(
            plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8edf5", height=300,
            xaxis_title="Over", yaxis_title="Strike Rate",
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Ranking position
        if data["all_batters"] is not None:
            player_bat = data["all_batters"][data["all_batters"]["striker_id"] == pid]
            if len(player_bat) > 0:
                row = player_bat.iloc[0]
                st.markdown("### Batting Ranking Position")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Rank", f"#{int(row.get('rank', 'N/A'))}")
                c2.metric("Rating", f"{row.get('shrunk_rating', 0):.4f}")
                c3.metric("Eligible", "✅" if row.get("eligible", False) else "❌")
                c4.metric("Reliability", str(row.get("reliability_level", "N/A")))

        # Competition breakdown
        st.markdown("### Competition Breakdown")
        if "match_format" in bat_faced.columns:
            comp_perf = bat_faced.groupby("match_format").agg(
                Matches=("match_id", "nunique"),
                Balls=("ball_faced", "sum"),
                Runs=("batter_runs", "sum"),
            ).reset_index()
            comp_perf["SR"] = comp_perf["Runs"] / comp_perf["Balls"] * 100
            st.dataframe(comp_perf, hide_index=True, use_container_width=True)

with tab_bowl:
    if len(bowl_data) == 0:
        st.info("No bowling data available for this player")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        legal_balls = bowl_data["is_legal"].sum()
        runs_conceded = bowl_data["bowler_runs"].sum()
        wickets = bowl_data["is_bowler_wicket"].sum()
        econ = runs_conceded * 6.0 / legal_balls if legal_balls > 0 else 0
        matches = bowl_data["match_id"].nunique()
        
        c1.metric("Wickets", f"{wickets}")
        c2.metric("Legal Balls", f"{legal_balls:,}")
        c3.metric("Economy", f"{econ:.2f}")
        c4.metric("Matches", f"{matches}")
        c5.metric("Dots", f"{bowl_data['is_dot'].sum()}")
        
        # Pressure vs Normal
        st.markdown("### Pressure vs Normal Bowling")
        pressure_bowl = bowl_data[bowl_data["pressure_category"] == "high"]
        normal_bowl = bowl_data[bowl_data["pressure_category"] == "normal"]
        
        comp_data = {"Metric": ["Deliveries", "Legal Balls", "Runs", "Economy", "Wickets", "Dot %", "Matches"]}
        for label, subset in [("Pressure", pressure_bowl), ("Normal", normal_bowl), ("Overall", bowl_data)]:
            dels = len(subset)
            lb = subset["is_legal"].sum()
            rc = subset["bowler_runs"].sum()
            ec = rc * 6.0 / lb if lb > 0 else 0
            wk = subset["is_bowler_wicket"].sum()
            dp = subset["is_dot"].sum() / lb * 100 if lb > 0 else 0
            mt = subset["match_id"].nunique()
            comp_data[label] = [dels, lb, rc, f"{ec:.2f}", wk, f"{dp:.1f}%", mt]
        
        st.dataframe(pd.DataFrame(comp_data), hide_index=True, use_container_width=True)
        
        # Match-by-match
        st.markdown("### Match-by-Match Bowling Economy (Pressure)")
        match_bowl = pressure_bowl.groupby("match_id").agg(
            runs=("bowler_runs", "sum"),
            legal=("is_legal", "sum"),
            wickets=("is_bowler_wicket", "sum"),
        ).reset_index()
        match_bowl["economy"] = match_bowl["runs"] * 6.0 / np.maximum(match_bowl["legal"], 1)
        
        if len(match_bowl) > 0:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=list(range(1, len(match_bowl)+1)),
                y=match_bowl["economy"],
                marker_color=np.where(match_bowl["economy"] <= econ, "#4ade80", "#ef4444"),
            ))
            fig.add_hline(y=econ, line_dash="dash", line_color="#fbbf24",
                         annotation_text=f"Overall Econ: {econ:.2f}")
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e8edf5", height=350,
                xaxis_title="Match #", yaxis_title="Economy Rate (Pressure)",
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Ranking position
        if data["all_bowlers"] is not None:
            player_bowl = data["all_bowlers"][data["all_bowlers"]["bowler_id"] == pid]
            if len(player_bowl) > 0:
                row = player_bowl.iloc[0]
                st.markdown("### Bowling Ranking Position")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Rank", f"#{int(row.get('rank', 'N/A'))}")
                c2.metric("Rating", f"{row.get('shrunk_rating', 0):.4f}")
                c3.metric("Eligible", "✅" if row.get("eligible", False) else "❌")
                c4.metric("Reliability", str(row.get("reliability_level", "N/A")))

