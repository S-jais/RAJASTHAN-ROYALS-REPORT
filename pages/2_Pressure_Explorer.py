"""
Page 2: Pressure Explorer — Explore individual match situations and pressure levels.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Pressure Explorer — PRESSURE IQ", page_icon="🔍", layout="wide")
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.markdown("# 🔍 Pressure Explorer")
st.markdown("*Explore ball-by-ball pressure situations across matches*")
st.markdown("---")

@st.cache_data
def load_data():
    try:
        df = pd.read_parquet(os.path.join(project_root, "data", "processed", "full_processed_data.parquet"))
        registry = pd.read_csv(os.path.join(project_root, "data", "processed", "player_registry.csv"))
        return df, registry.set_index("player_id")["player_name"].to_dict()
    except:
        return None, {}

df, registry = load_data()

if df is None:
    st.error("Run the pipeline first: `python scripts/run_pipeline.py`")
    st.stop()

# Filters
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    formats = ["All"] + sorted(df["match_format"].dropna().unique().tolist())
    selected_format = st.selectbox("Match Format", formats)

with col_f2:
    if selected_format != "All":
        comps = df[df["match_format"] == selected_format]["comp_name"].dropna().unique().tolist()
    else:
        comps = df["comp_name"].dropna().unique().tolist()
    comp_options = ["All"] + sorted(comps)
    selected_comp = st.selectbox("Competition", comp_options)

with col_f3:
    pressure_filter = st.selectbox("Pressure Level", ["All", "High", "Normal", "Intermediate"])

# Apply filters
filtered = df.copy()
if selected_format != "All":
    filtered = filtered[filtered["match_format"] == selected_format]
if selected_comp != "All":
    filtered = filtered[filtered["comp_name"] == selected_comp]
if pressure_filter != "All":
    filtered = filtered[filtered["pressure_category"] == pressure_filter.lower()]

# Match selector
match_cols = [c for c in ["match_id", "comp_name", "match_date"] if c in filtered.columns]
matches = filtered[match_cols].drop_duplicates()
if "match_date" in matches.columns:
    matches = matches.sort_values("match_date", ascending=False)
if "match_date" in matches.columns and "comp_name" in matches.columns:
    matches["label"] = matches["match_id"].astype(str) + " — " + matches["comp_name"].fillna("") + " (" + matches["match_date"].astype(str).str[:10] + ")"
elif "comp_name" in matches.columns:
    matches["label"] = matches["match_id"].astype(str) + " — " + matches["comp_name"].fillna("")
else:
    matches["label"] = matches["match_id"].astype(str)

selected_match_label = st.selectbox("Select Match", matches["label"].tolist()[:100])
if selected_match_label:
    selected_match_id = int(selected_match_label.split(" — ")[0])
    match_df = filtered[filtered["match_id"] == selected_match_id]
    
    st.markdown(f"### Match {selected_match_id}")
    
    # Match summary
    for inn in sorted(match_df["innings"].unique()):
        inn_df = match_df[match_df["innings"] == inn]
        batting_team = inn_df["batting_team_id"].iloc[0] if len(inn_df) > 0 else "?"
        total_runs = inn_df["total_runs"].sum()
        total_wickets = inn_df["is_wicket"].sum()
        
        st.markdown(f"**Innings {inn}**: {total_runs}/{total_wickets}")
    
    # Pressure over time
    st.markdown("### Pressure Index Over the Match")
    
    fig = go.Figure()
    
    for inn in sorted(match_df["innings"].unique()):
        inn_df = match_df[match_df["innings"] == inn]
        if "innings_ball_num" in inn_df.columns:
            inn_df = inn_df.sort_values("innings_ball_num")
            x_vals = inn_df["innings_ball_num"]
        elif "overid" in inn_df.columns and "over_ball_num" in inn_df.columns:
            inn_df = inn_df.sort_values(["overid", "over_ball_num"])
            x_vals = inn_df["overid"] * 6 + inn_df["over_ball_num"]
        else:
            x_vals = np.arange(1, len(inn_df) + 1)
        
        color = "#4ade80" if inn == 1 else "#ef4444"
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=inn_df["pressure_index"],
            mode="lines+markers",
            name=f"Innings {inn}",
            line=dict(color=color, width=2),
            marker=dict(size=3),
            hovertemplate=(
                "Ball: %{x}<br>"
                "PI: %{y:.3f}<br>"
                "<extra></extra>"
            )
        ))
    
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(20,27,45,0.8)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e8edf5",
        height=400,
        xaxis_title="Ball Number in Innings",
        yaxis_title="Pressure Index",
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed delivery table
    st.markdown("### Ball-by-Ball Details")
    
    display_cols = [
        "innings", "innings_ball_num", "overid", "over_ball_num", "striker_name", "bowler_name",
        "batter_runs", "total_runs", "is_wicket", "dismissal_type",
        "pressure_index", "pressure_category",
        "cum_runs_before", "cum_wickets_before", "balls_remaining",
        "wickets_remaining", "current_rr", "required_rr",
        "pi_chase_urgency", "pi_resource", "pi_phase"
    ]
    available = [c for c in display_cols if c in match_df.columns]
    
    # Sort first on match_df so that available columns don't constrain sorting
    sort_cols = [c for c in ["innings", "innings_ball_num", "overid", "over_ball_num"] if c in match_df.columns]
    sorted_df = match_df.sort_values(sort_cols) if sort_cols else match_df
    
    st.dataframe(
        sorted_df[available],
        hide_index=True,
        use_container_width=True,
        height=400,
    )

# High pressure situations leaderboard
st.markdown("---")
st.markdown("### 🔥 Highest Pressure Deliveries")

top_pressure = df.nlargest(20, "pressure_index")
wanted_cols = ["match_id", "innings", "overid", "over_ball_num", 
               "striker_name", "bowler_name", "batter_runs", 
               "is_wicket", "pressure_index", "pressure_category",
               "balls_remaining", "wickets_remaining", "comp_name"]
avail_top = [c for c in wanted_cols if c in top_pressure.columns]
display = top_pressure[avail_top].copy()
display = display.rename(columns={
    "pressure_index": "PI", "striker_name": "Batter", "bowler_name": "Bowler",
    "batter_runs": "Runs", "comp_name": "Competition"
})

st.dataframe(display, hide_index=True, use_container_width=True)

