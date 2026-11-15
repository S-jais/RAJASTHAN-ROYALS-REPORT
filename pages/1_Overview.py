"""
Page 1: Overview — Summary dashboard with key metrics and visualizations.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json

st.set_page_config(page_title="Overview — PRESSURE IQ", page_icon="📊", layout="wide")

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.markdown("# 📊 Overview")
st.markdown("*Comprehensive summary of the PRESSURE IQ analysis*")
st.markdown("---")

@st.cache_data
def load_data():
    data = {}
    try:
        data["df"] = pd.read_parquet(os.path.join(project_root, "data", "processed", "full_processed_data.parquet"))
    except:
        data["df"] = None
    try:
        with open(os.path.join(project_root, "outputs", "pressure_analysis.json")) as f:
            data["analysis"] = json.load(f)
    except:
        data["analysis"] = None
    try:
        data["bat"] = pd.read_csv(os.path.join(project_root, "outputs", "batter_rankings.csv"))
    except:
        data["bat"] = None
    try:
        data["bowl"] = pd.read_csv(os.path.join(project_root, "outputs", "bowler_rankings.csv"))
    except:
        data["bowl"] = None
    return data

data = load_data()

if data["df"] is None:
    st.error("Run the pipeline first: `python scripts/run_pipeline.py`")
    st.stop()

df = data["df"]
pa = data["analysis"] or {}

# Key metrics row 1
st.markdown("### Dataset Coverage")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Matches", f"{df['match_id'].nunique():,}")
c2.metric("Deliveries", f"{len(df):,}")
c3.metric("Batters", f"{df['striker_id'].nunique():,}")
c4.metric("Bowlers", f"{df['bowler_id'].nunique():,}")
c5.metric("Seasons", f"{df['season'].nunique()}")

# Key metrics row 2
st.markdown("### Pressure Analysis")
c1, c2, c3, c4 = st.columns(4)
c1.metric("High Pressure Balls", f"{(df['pressure_category']=='high').sum():,}")
c2.metric("Mean PI", f"{df['pressure_index'].mean():.3f}")
c3.metric("Median PI", f"{df['pressure_index'].median():.3f}")
c4.metric("PI Std Dev", f"{df['pressure_index'].std():.3f}")

st.markdown("---")

# Visualizations
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Pressure Index Distribution")
    sample = df.sample(min(50000, len(df)), random_state=42)
    fig = px.histogram(
        sample, x="pressure_index", nbins=60,
        color="pressure_category",
        color_discrete_map={"high": "#ef4444", "normal": "#4ade80", "intermediate": "#fbbf24"},
        template="plotly_dark",
    )
    fig.update_layout(
        plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e8edf5", height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Pressure by Over Number")
    over_pi = df.groupby("overid")["pressure_index"].mean().reset_index()
    fig = px.line(
        over_pi, x="overid", y="pressure_index",
        template="plotly_dark", markers=True,
    )
    fig.update_traces(line_color="#4ade80", marker_color="#22d3ee")
    fig.update_layout(
        plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e8edf5", height=400,
        xaxis_title="Over", yaxis_title="Mean Pressure Index"
    )
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("### Pressure: 1st vs 2nd Innings")
    inn_pi = df.groupby(["innings", "overid"])["pressure_index"].mean().reset_index()
    fig = px.line(
        inn_pi, x="overid", y="pressure_index", color="innings",
        template="plotly_dark",
        color_discrete_map={1: "#4ade80", 2: "#ef4444"},
    )
    fig.update_layout(
        plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e8edf5", height=400,
        xaxis_title="Over", yaxis_title="Mean Pressure Index"
    )
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.markdown("### Pressure Components Breakdown")
    pi_cols = ["pi_chase_urgency", "pi_resource", "pi_phase", "pi_competitiveness", "pi_first_inn_par"]
    existing = [c for c in pi_cols if c in df.columns]
    means = df[existing].mean().reset_index()
    means.columns = ["Component", "Mean Value"]
    means["Component"] = means["Component"].str.replace("pi_", "").str.replace("_", " ").str.title()
    fig = px.bar(
        means, x="Component", y="Mean Value",
        template="plotly_dark", color="Mean Value",
        color_continuous_scale=["#4ade80", "#fbbf24", "#ef4444"],
    )
    fig.update_layout(
        plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e8edf5", height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

# Competition breakdown
st.markdown("### Competition Coverage")
if "match_format" in df.columns:
    fmt_stats = df.groupby("match_format").agg(
        Matches=("match_id", "nunique"),
        Deliveries=("match_id", "count"),
        Mean_PI=("pressure_index", "mean"),
    ).reset_index()
    st.dataframe(fmt_stats, hide_index=True, use_container_width=True)

# Season breakdown
st.markdown("### Season Coverage")
if "season" in df.columns:
    season_stats = df.groupby("season").agg(
        Matches=("match_id", "nunique"),
        Deliveries=("match_id", "count"),
        Mean_PI=("pressure_index", "mean"),
        High_Pressure_Pct=("pressure_category", lambda x: (x == "high").mean() * 100),
    ).reset_index()
    st.dataframe(season_stats, hide_index=True, use_container_width=True)

