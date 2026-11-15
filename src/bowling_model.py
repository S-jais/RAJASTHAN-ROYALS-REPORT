"""
bowling_model.py — Bowling pressure performance model.

Calculates player-level bowling metrics under pressure vs non-pressure baseline,
computes context-adjusted impact, economy uplift, wicket value, and composite ratings.

Generates three distinct ranking views:
1. Raw Pressure Performance (Pressure Economy, Runs Saved per Ball)
2. Economy Improvement over Baseline (Economy Improvement, Impact Uplift)
3. Context-Adjusted Shrunk Rating (Primary Rating combining impact, uplift, wickets, consistency, volume)
"""
import numpy as np
import pandas as pd


def compute_bowling_aggregates(df, pressure_col="pressure_category"):
    """
    Compute bowling aggregates for each player under pressure vs non-pressure baseline.
    """
    bowl_df = df.copy()
    
    results = []
    
    for category in ["high", "normal", "all"]:
        if category == "all":
            cat_df = bowl_df
        elif category == "high":
            cat_df = bowl_df[bowl_df[pressure_col] == "high"]
        elif category == "normal":
            # True non-pressure baseline: all balls NOT in high pressure
            cat_df = bowl_df[bowl_df[pressure_col] != "high"]
        
        if len(cat_df) == 0:
            continue
        
        agg_dict = {
            "total_deliveries": ("bowler_id", "count"),
            "legal_balls": ("is_legal", "sum"),
            "bowler_runs_conceded": ("bowler_runs", "sum"),
            "bowler_wickets": ("is_bowler_wicket", "sum"),
            "total_wickets": ("is_wicket", "sum"),
            "dots": ("is_dot", "sum"),
            "fours_conceded": ("is_four", "sum"),
            "sixes_conceded": ("is_six", "sum"),
            "wides": ("is_wide", "sum"),
            "noballs": ("is_noball", "sum"),
            "matches": ("match_id", "nunique"),
            "expected_runs_sum": ("expected_bowling_runs", "sum") if "expected_bowling_runs" in cat_df.columns else ("bowler_runs", "sum"),
            "bowling_impact_sum": ("bowling_impact", "sum") if "bowling_impact" in cat_df.columns else ("bowler_runs", "sum"),
        }
        if "bowler_name" in cat_df.columns:
            agg_dict["player_name"] = ("bowler_name", "first")
            
        agg = cat_df.groupby("bowler_id").agg(**agg_dict).reset_index()
        
        # Economy rate per 6 legal deliveries
        agg["economy"] = np.where(
            agg["legal_balls"] > 0,
            agg["bowler_runs_conceded"] * 6.0 / agg["legal_balls"],
            0.0
        )
        
        agg["dot_pct"] = np.where(
            agg["legal_balls"] > 0,
            agg["dots"] / agg["legal_balls"] * 100.0,
            0.0
        )
        
        agg["bowling_sr"] = np.where(
            agg["bowler_wickets"] > 0,
            agg["legal_balls"] / agg["bowler_wickets"],
            999.0
        )
        
        agg["boundary_pct"] = np.where(
            agg["total_deliveries"] > 0,
            (agg["fours_conceded"] + agg["sixes_conceded"]) / agg["total_deliveries"] * 100.0,
            0.0
        )
        
        agg["impact_per_ball"] = np.where(
            agg["legal_balls"] > 0,
            agg["bowling_impact_sum"] / agg["legal_balls"],
            0.0
        )
        
        agg["pressure_category"] = category
        results.append(agg)
    
    return pd.concat(results, ignore_index=True)


def compute_wicket_value(df):
    """
    Compute context-dependent wicket value.
    """
    wicket_df = df[df["is_bowler_wicket"]].copy()
    
    if len(wicket_df) == 0:
        return pd.DataFrame()
    
    wicket_df["wicket_value"] = (
        wicket_df["wickets_remaining"] / 10.0 *
        wicket_df["balls_remaining"] / 120.0 *
        wicket_df["pressure_index"] *
        15.0
    )
    
    wicket_agg = wicket_df.groupby("bowler_id").agg(
        total_wicket_value=("wicket_value", "sum"),
        avg_wicket_value=("wicket_value", "mean"),
        pressure_wickets=("pressure_index", "count"),
    ).reset_index()
    
    return wicket_agg


def compute_bowling_consistency(df, pressure_col="pressure_category"):
    """
    Compute match-level consistency of bowling performance under pressure.
    """
    bowl_df = df[df[pressure_col] == "high"].copy()
    
    match_agg = bowl_df.groupby(["bowler_id", "match_id"]).agg(
        match_deliveries=("bowler_id", "count"),
        match_legal_balls=("is_legal", "sum"),
        match_runs=("bowler_runs", "sum"),
        match_wickets=("is_bowler_wicket", "sum"),
        match_impact=("bowling_impact", "sum") if "bowling_impact" in bowl_df.columns else ("bowler_runs", "sum"),
    ).reset_index()
    
    # Matches with at least 6 legal deliveries (1 over) under pressure
    filtered_matches = match_agg[match_agg["match_legal_balls"] >= 6]
    filtered_matches["match_impact_per_ball"] = filtered_matches["match_impact"] / np.maximum(filtered_matches["match_legal_balls"], 1)
    
    consistency = filtered_matches.groupby("bowler_id").agg(
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


def compute_bowling_ratings(aggregates, consistency, wicket_values=None, config=None):
    """
    Compute bowling ratings and generate the three comparison rankings.
    """
    if config is None:
        config = {
            "context_adjusted_weight": 0.35,
            "pressure_uplift_weight": 0.30,
            "wicket_impact_weight": 0.15,
            "consistency_weight": 0.10,
            "reliability_weight": 0.10,
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
        normal[["bowler_id", "economy", "impact_per_ball", "legal_balls", "bowler_runs_conceded", "bowler_wickets", "dot_pct"]],
        on="bowler_id", suffixes=("_pressure", "_normal"), how="left"
    )
    
    merged = merged.merge(
        overall[["bowler_id", "legal_balls", "bowler_runs_conceded", "bowler_wickets", "matches"]].rename(
            columns={"legal_balls": "total_balls", "bowler_runs_conceded": "total_runs", "bowler_wickets": "total_wickets", "matches": "total_matches"}
        ),
        on="bowler_id", how="left"
    )
    
    merged = merged.merge(
        consistency[["bowler_id", "consistency_score", "pressure_matches"]],
        on="bowler_id", how="left"
    )
    
    if wicket_values is not None and len(wicket_values) > 0:
        merged = merged.merge(
            wicket_values[["bowler_id", "total_wicket_value", "avg_wicket_value"]],
            on="bowler_id", how="left"
        )
        merged["total_wicket_value"] = merged["total_wicket_value"].fillna(0.0)
    else:
        merged["total_wicket_value"] = 0.0
    
    merged["consistency_score"] = merged["consistency_score"].fillna(0.35)
    merged["pressure_matches"] = merged["pressure_matches"].fillna(0)
    
    # Uplifts
    merged["pressure_uplift"] = merged["impact_per_ball_pressure"] - merged["impact_per_ball_normal"].fillna(0.0)
    merged["economy_improvement"] = merged["economy_normal"].fillna(0.0) - merged["economy_pressure"]
    
    # Eligibility
    merged["eligible"] = (
        (merged["legal_balls_pressure"] >= config.get("min_pressure_balls", 60)) &
        (merged["legal_balls_normal"].fillna(0) >= config.get("min_normal_balls", 60)) &
        (merged["total_matches"] >= config.get("min_matches", 5)) &
        (merged["pressure_matches"] >= config.get("min_pressure_matches", 4))
    )
    
    # Scores
    merged["quality_score"] = merged["impact_per_ball_pressure"].rank(pct=True)
    merged["uplift_score"] = merged["economy_improvement"].rank(pct=True)
    merged["wicket_score"] = merged["bowler_wickets_pressure"].rank(pct=True)
    merged["consistency_component"] = merged["consistency_score"]
    merged["volume_score"] = np.clip(merged["legal_balls_pressure"] / 300.0, 0.0, 1.0)
    
    # Composite Raw Rating
    merged["bowling_pressure_rating"] = (
        config.get("context_adjusted_weight", 0.35) * merged["quality_score"] +
        config.get("pressure_uplift_weight", 0.30) * merged["uplift_score"] +
        config.get("wicket_impact_weight", 0.15) * merged["wicket_score"] +
        config.get("consistency_weight", 0.10) * merged["consistency_component"] +
        config.get("reliability_weight", 0.10) * merged["volume_score"]
    )
    
    return merged
