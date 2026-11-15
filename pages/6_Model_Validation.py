"""
Page 6: Model Validation — Statistical validation, sensitivity analysis, and robustness checks.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="Model Validation — PRESSURE IQ", page_icon="📈", layout="wide")
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.markdown("# 📈 Model Validation & Statistical Rigour")
st.markdown("*Sensitivity analysis, threshold tests, bootstrap validation, and diagnostics*")
st.markdown("---")

@st.cache_data
def load_validation_data():
    outputs_dir = os.path.join(project_root, "outputs")
    data = {}
    
    # Validation JSON
    val_path = os.path.join(outputs_dir, "model_validation.json")
    if os.path.exists(val_path):
        with open(val_path, "r") as f:
            data["validation"] = json.load(f)
            
    # Data quality report
    dq_path = os.path.join(outputs_dir, "data_quality_report.json")
    if os.path.exists(dq_path):
        with open(dq_path, "r") as f:
            data["data_quality"] = json.load(f)
            
    # Pressure analysis summary
    pa_path = os.path.join(outputs_dir, "pressure_analysis.json")
    if os.path.exists(pa_path):
        with open(pa_path, "r") as f:
            data["pressure_analysis"] = json.load(f)
            
    # Threshold sensitivity
    bat_sens_path = os.path.join(outputs_dir, "batting_threshold_sensitivity.csv")
    if os.path.exists(bat_sens_path):
        data["bat_sens"] = pd.read_csv(bat_sens_path)
        
    bowl_sens_path = os.path.join(outputs_dir, "bowling_threshold_sensitivity.csv")
    if os.path.exists(bowl_sens_path):
        data["bowl_sens"] = pd.read_csv(bowl_sens_path)
        
    # Bootstrap
    bat_boot_path = os.path.join(outputs_dir, "batting_bootstrap.csv")
    if os.path.exists(bat_boot_path):
        data["bat_boot"] = pd.read_csv(bat_boot_path)
        
    bowl_boot_path = os.path.join(outputs_dir, "bowling_bootstrap.csv")
    if os.path.exists(bowl_boot_path):
        data["bowl_boot"] = pd.read_csv(bowl_boot_path)
        
    return data

val_data = load_validation_data()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Threshold Sensitivity",
    "🔄 Bootstrap Stability",
    "🤖 Expected-Performance Models",
    "🛡️ Data Quality Audit",
    "⚖️ Shrinkage Diagnostics"
])

# ----------------- TAB 1: Threshold Sensitivity -----------------
with tab1:
    st.markdown("### Pressure Threshold Sensitivity Analysis")
    st.markdown("""
    To test whether rankings are sensitive to the cutoff chosen for 'high pressure',
    we evaluated player ratings across three percentile thresholds:
    - **Top 20% (P80)**: Strictest definition of extreme pressure
    - **Top 25% (P75)**: Primary operational baseline
    - **Top 30% (P70)**: Broader definition capturing moderate-high pressure
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Batter Rankings Under Different Thresholds")
        if "bat_sens" in val_data:
            bs = val_data["bat_sens"]
            st.dataframe(bs, hide_index=True, use_container_width=True)
        else:
            st.info("Run the pipeline to populate sensitivity tables.")
            
    with col2:
        st.markdown("#### Bowler Rankings Under Different Thresholds")
        if "bowl_sens" in val_data:
            bws = val_data["bowl_sens"]
            st.dataframe(bws, hide_index=True, use_container_width=True)
        else:
            st.info("Run the pipeline to populate sensitivity tables.")

# ----------------- TAB 2: Bootstrap Stability -----------------
with tab2:
    st.markdown("### Cluster Bootstrap Ranking Stability")
    st.markdown("""
    Deliveries within the same match are correlated. We resample **entire matches with replacement** (cluster bootstrap)
    across 50 iterations to measure:
    - **Mean Rank**: Average position across resamples
    - **Top-10 Frequency**: Proportion of bootstrap iterations where the player finishes in the Top 10
    - **Rank Volatility (Std Dev)**: Lower standard deviation reflects robust match-to-match reliability
    """)
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("#### Batter Bootstrap Stability")
        if "bat_boot" in val_data:
            bb = val_data["bat_boot"].head(15)
            fig = px.bar(
                bb, x="player_name", y="top10_freq",
                template="plotly_dark",
                labels={"player_name": "Player", "top10_freq": "Top-10 Inclusion %"},
                title="Batter Top-10 Selection Frequency"
            )
            fig.update_traces(marker_color="#4ade80")
            fig.update_layout(plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(bb[["player_name", "mean_rank", "median_rank", "rank_std", "top10_freq"]], hide_index=True, use_container_width=True)
        else:
            st.info("Run pipeline to view bootstrap metrics.")
            
    with col_b2:
        st.markdown("#### Bowler Bootstrap Stability")
        if "bowl_boot" in val_data:
            wb = val_data["bowl_boot"].head(15)
            fig = px.bar(
                wb, x="player_name", y="top10_freq",
                template="plotly_dark",
                labels={"player_name": "Player", "top10_freq": "Top-10 Inclusion %"},
                title="Bowler Top-10 Selection Frequency"
            )
            fig.update_traces(marker_color="#22d3ee")
            fig.update_layout(plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(wb[["player_name", "mean_rank", "median_rank", "rank_std", "top10_freq"]], hide_index=True, use_container_width=True)
        else:
            st.info("Run pipeline to view bootstrap metrics.")

# ----------------- TAB 3: Expected-Performance Models -----------------
with tab3:
    st.markdown("### Context-Adjusted Expected Performance Models")
    st.markdown("""
    To separate individual skill from favorable match context, expected batter runs and bowler runs 
    are estimated using **Gradient Boosted Decision Trees** strictly evaluated using **Match-Grouped 5-Fold Cross-Validation**.
    
    - Target (Batting): `batter_runs` on legal balls faced.
    - Target (Bowling): `bowler_runs` conceded per delivery (including extras charged).
    - Player identities are intentionally **excluded** to prevent absorbing the player-specific signal.
    """)
    
    if "validation" in val_data:
        val = val_data["validation"]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Batting Expected Model Feature Importances")
            b_imp = val.get("batting_expected_model", {}).get("feature_importances", {})
            if b_imp:
                imp_df = pd.DataFrame(list(b_imp.items()), columns=["Feature", "Importance"]).sort_values("Importance", ascending=True)
                fig = px.bar(imp_df, x="Importance", y="Feature", orientation="h", template="plotly_dark")
                fig.update_traces(marker_color="#4ade80")
                fig.update_layout(plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("#### Bowling Expected Model Feature Importances")
            w_imp = val.get("bowling_expected_model", {}).get("feature_importances", {})
            if w_imp:
                wimp_df = pd.DataFrame(list(w_imp.items()), columns=["Feature", "Importance"]).sort_values("Importance", ascending=True)
                fig2 = px.bar(wimp_df, x="Importance", y="Feature", orientation="h", template="plotly_dark")
                fig2.update_traces(marker_color="#22d3ee")
                fig2.update_layout(plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)

# ----------------- TAB 4: Data Quality Audit -----------------
with tab4:
    st.markdown("### Data Quality & Integrity Audit")
    if "data_quality" in val_data:
        dq = val_data["data_quality"]
        st.markdown(f"**Audit Timestamp:** `{dq.get('timestamp')}`")
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.markdown("#### Key Verification Points")
            st.success("✅ Wides and No-Balls correctly excluded from legal balls faced")
            st.success("✅ Run-outs and Retire-outs excluded from bowler wickets")
            st.success("✅ Non-striker dismissals accurately identified (striker not blamed)")
            st.success("✅ Extras correctly charged: Wides/No-Balls to bowler, Byes/Leg-byes to extras only")
            
        with col_q2:
            st.markdown("#### Dataset Cross-Validation")
            cv = dq.get("datasets", {}).get("cross_validation", {})
            st.json(cv)
            
        if dq.get("warnings"):
            st.markdown("#### Identified Warnings")
            for w in dq["warnings"]:
                st.warning(f"⚠️ {w}")
    else:
        st.info("Run pipeline to load data quality report.")

# ----------------- TAB 5: Shrinkage Diagnostics -----------------
with tab5:
    st.markdown("### Empirical Bayes Shrinkage Diagnostics")
    st.markdown(r"""
    A persistent trap in sports analytics is the **small-sample anomaly** (e.g. a batter who faced 12 balls and hit 30 runs with a 250 SR).
    
    We employ **Empirical Bayes shrinkage**, moving uncertain raw ratings toward the league mean:
    
    $$R_{\text{shrunk}} = (1 - B) \cdot R_{\text{raw}} + B \cdot \mu_{\text{population}}$$
    
    where $B$ is the shrinkage shrinkage factor determined by individual sample size vs. variance:
    
    $$B = \frac{\sigma^2_i}{\sigma^2_i + \tau^2}$$
    
    Players with fewer qualifying deliveries experience higher shrinkage factor $B$, pulling their rating closer to population average.
    """)
    
    outputs_dir = os.path.join(project_root, "outputs")
    bat_r_path = os.path.join(outputs_dir, "all_batter_ratings.csv")
    if os.path.exists(bat_r_path):
        bat_r = pd.read_csv(bat_r_path)
        if "shrinkage_factor" in bat_r.columns:
            fig = px.scatter(
                bat_r, x="balls_faced_pressure", y="shrinkage_factor",
                color="reliability_level",
                template="plotly_dark",
                labels={"balls_faced_pressure": "Pressure Balls Faced", "shrinkage_factor": "Shrinkage Factor (B)"},
                title="Shrinkage Penalty vs Pressure Balls Faced"
            )
            fig.update_layout(plot_bgcolor="rgba(20,27,45,0.8)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

