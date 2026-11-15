"""
batting_model.py — Batting pressure performance model.

Calculates player-level batting metrics under pressure vs normal conditions,
computes context-adjusted impact, consistency, and composite ratings.

Generates three distinct ranking views:
1. Raw Pressure Performance (Impact per ball, Strike Rate)
2. Pressure Uplift over Baseline (SR Uplift, Impact Uplift)
3. Context-Adjusted Shrunk Rating (Primary Rating combining impact, uplift, consistency, volume)
"""
import numpy as np
import pandas as pd


def compute_batting_aggregates(df, pressure_col="pressure_category"):
    """
    Compute batting aggregates for each player under pressure vs non-pressure baseline.
    
    Categories:
    - 'high': High pressure deliveries (top 25%)
    - 'normal': Non-high-pressure baseline (all other balls faced by the player)
    - 'all': Overall career deliveries
    """
    batter_df = df[df["ball_faced"] == 1].copy()
    
    batter_df["batter_dismissed"] = (
        batter_df["is_wicket"] & 
        (batter_df["dismissed_player_id"] == batter_df["striker_id"])
    ).astype(int)
    
    results = []
    
    for category in ["high", "normal", "all"]:
        if category == "all":
            cat_df = batter_df
        elif category == "high":
            cat_df = batter_df[batter_df[pressure_col] == "high"]
        elif category == "normal":
            # True non-pressure baseline: all balls NOT in high pressure
            cat_df = batter_df[batter_df[pressure_col] != "high"]
        
        if len(cat_df) == 0:
            continue
        
        agg_dict = {
            "balls_faced": ("ball_faced", "sum"),
            "runs": ("batter_runs", "sum"),
            "dismissals": ("batter_dismissed", "sum"),
            "fours": ("is_four", "sum"),
            "sixes": ("is_six", "sum"),
            "dots": ("is_dot", "sum"),
            "matches": ("match_id", "nunique"),
            "total_expected": ("expected_batting_runs", "sum") if "expected_batting_runs" in cat_df.columns else ("batter_runs", "sum"),
            "batting_impact_sum": ("batting_impact", "sum") if "batting_impact" in cat_df.columns else ("batter_runs", "sum"),
        }
        if "striker_name" in cat_df.columns:
            agg_dict["player_name"] = ("striker_name", "first")
            
        agg = cat_df.groupby("striker_id").agg(**agg_dict).reset_index()
        
        agg["strike_rate"] = np.where(agg["balls_faced"] > 0, agg["runs"] / agg["balls_faced"] * 100.0, 0.0)
        agg["boundary_pct"] = np.where(
            agg["balls_faced"] > 0, 
            (agg["fours"] + agg["sixes"]) / agg["balls_faced"] * 100.0, 0.0
        )
        agg["dot_pct"] = np.where(agg["balls_faced"] > 0, agg["dots"] / agg["balls_faced"] * 100.0, 0.0)
        agg["dismissal_rate"] = np.where(agg["balls_faced"] > 0, agg["dismissals"] / agg["balls_faced"] * 100.0, 0.0)
        agg["avg"] = np.where(agg["dismissals"] > 0, agg["runs"] / agg["dismissals"], agg["runs"])
        
        agg["impact_per_ball"] = np.where(
            agg["balls_faced"] > 0, agg["batting_impact_sum"] / agg["balls_faced"], 0.0
        )
        
        agg["pressure_category"] = category
        results.append(agg)
    
    return pd.concat(results, ignore_index=True)


def compute_batting_consistency(df, pressure_col="pressure_category"):
    """
    Compute match-level consistency of batting performance under pressure.
    """
    batter_df = df[(df["ball_faced"] == 1) & (df[pressure_col] == "high")].copy()
    
    match_agg = batter_df.groupby(["striker_id", "match_id"]).agg(
        match_balls=("ball_faced", "sum"),
        match_runs=("batter_runs", "sum"),
        match_impact=("batting_impact", "sum") if "batting_impact" in batter_df.columns else ("batter_runs", "sum"),
    ).reset_index()
    
    match_agg["match_impact_per_ball"] = match_agg["match_impact"] / np.maximum(match_agg["match_balls"], 1)
    
    # Filter to matches where batter faced at least 4 balls under pressure
    filtered_matches = match_agg[match_agg["match_balls"] >= 4]
    
    consistency = filtered_matches.groupby("striker_id").agg(
        pressure_matches=("match_id", "nunique"),
        mean_impact=("match_impact_per_ball", "mean"),
        std_impact=("match_impact_per_ball", "std"),
    ).reset_index()
    
    consistency["cv_impact"] = np.where(
        consistency["mean_impact"].abs() > 0.02,
        consistency["std_impact"] / consistency["mean_impact"].abs(),
        2.0
    )
    
    consistency["consistency_score"] = 1.0 / (1.0 + np.clip(consistency["cv_impact"].fillna(2.0), 0.0, 5.0))
    return consistency


def compute_batting_ratings(aggregates, consistency, config=None):
    """
    Compute batting ratings and generate the three comparison rankings.
    """
    if config is None:
        config = {
            "context_adjusted_weight": 0.35,
            "pressure_uplift_weight": 0.30,
            "consistency_weight": 0.20,
            "reliability_weight": 0.15,
            "min_pressure_balls": 60,
            "min_normal_balls": 60,
            "min_total_balls": 150,
            "min_matches": 5,
            "min_pressure_matches": 4,
        }
    
    pressure = aggregates[aggregates["pressure_category"] == "high"].copy()
    normal = aggregates[aggregates["pressure_category"] == "normal"].copy()
    overall = aggregates[aggregates["pressure_category"] == "all"].copy()
    
    merged = pressure.merge(
        normal[["striker_id", "strike_rate", "impact_per_ball", "balls_faced", "runs", "dismissal_rate"]],
        on="striker_id", suffixes=("_pressure", "_normal"), how="left"
    )
    
    merged = merged.merge(
        overall[["striker_id", "balls_faced", "runs", "matches"]].rename(
            columns={"balls_faced": "total_balls", "runs": "total_runs", "matches": "total_matches"}
        ),
        on="striker_id", how="left"
    )
    
    merged = merged.merge(
        consistency[["striker_id", "consistency_score", "pressure_matches"]],
        on="striker_id", how="left"
    )
    
    merged["consistency_score"] = merged["consistency_score"].fillna(0.35)
    merged["pressure_matches"] = merged["pressure_matches"].fillna(0)
    
    # Pressure Uplifts
    merged["pressure_uplift"] = merged["impact_per_ball_pressure"] - merged["impact_per_ball_normal"].fillna(0.0)
    merged["sr_uplift"] = merged["strike_rate_pressure"] - merged["strike_rate_normal"].fillna(0.0)
    
    # Eligibility filter
    merged["eligible"] = (
        (merged["balls_faced_pressure"] >= config.get("min_pressure_balls", 60)) &
        (merged["balls_faced_normal"].fillna(0) >= config.get("min_normal_balls", 60)) &
        (merged["total_matches"] >= config.get("min_matches", 5)) &
        (merged["pressure_matches"] >= config.get("min_pressure_matches", 4))
    )
    
    # Scoring components
    merged["quality_score"] = merged["impact_per_ball_pressure"].rank(pct=True)
    merged["uplift_score"] = merged["pressure_uplift"].rank(pct=True)
    merged["consistency_component"] = merged["consistency_score"]
    merged["volume_score"] = np.clip(merged["balls_faced_pressure"] / 300.0, 0.0, 1.0)
    
    # Composite Raw Rating
    merged["batting_pressure_rating"] = (
        config.get("context_adjusted_weight", 0.35) * merged["quality_score"] +
        config.get("pressure_uplift_weight", 0.30) * merged["uplift_score"] +
        config.get("consistency_weight", 0.20) * merged["consistency_component"] +
        config.get("reliability_weight", 0.15) * merged["volume_score"]
    )
    
    return merged
