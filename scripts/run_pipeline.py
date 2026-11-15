"""
run_pipeline.py — Main pipeline for PRESSURE IQ.

Executes the complete analysis:
1. Load and validate data
2. Compute innings state
3. Calculate Pressure Index
4. Build expected performance models
5. Calculate batting and bowling ratings (3 distinct rankings each)
6. Apply Empirical Bayes shrinkage
7. Generate player audit tables
8. Run robustness analysis
9. Export all outputs
"""
import sys
import os
import json
import time
import warnings

warnings.filterwarnings("ignore")

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import numpy as np
import pandas as pd
import yaml

from src.data_loader import (
    load_raw_data, build_player_registry, validate_data_quality,
    prepare_ball_by_ball, compute_innings_state
)
from src.pressure_index import calculate_pressure_index, classify_pressure
from src.expected_performance import build_batting_expected_model, build_bowling_expected_model
from src.batting_model import compute_batting_aggregates, compute_batting_consistency, compute_batting_ratings
from src.bowling_model import compute_bowling_aggregates, compute_bowling_consistency, compute_bowling_ratings, compute_wicket_value
from src.statistical_shrinkage import empirical_bayes_shrinkage
from src.robustness import sensitivity_pressure_thresholds, bootstrap_rankings, competition_sensitivity


def main():
    start_time = time.time()
    print("=" * 70)
    print("  PRESSURE IQ — Cricket Performance Intelligence Pipeline (Audited v2.0)")
    print("  SupeRR Selector Season 2")
    print("=" * 70, flush=True)

    with open(os.path.join(project_root, "config.yaml"), "r") as f:
        config = yaml.safe_load(f)

    raw_dir = os.path.join(project_root, config["data"]["raw_dir"])
    processed_dir = os.path.join(project_root, config["data"]["processed_dir"])
    output_dir = os.path.join(project_root, config["data"]["output_dir"])
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # ===================================================================
    # PHASE 1: DATA LOADING AND VALIDATION
    # ===================================================================
    print("\n[PHASE 1] Loading and validating data...", flush=True)
    data = load_raw_data(raw_dir)

    player_registry = build_player_registry(data["player_mapping"])
    print(f"  Player registry: {len(player_registry)} players", flush=True)

    bbb = data["ball_by_ball"]
    for col_id, col_name in [("striker_id", "striker_name"), ("bowler_id", "bowler_name")]:
        for pid, pname in zip(bbb[col_id], bbb[col_name]):
            if pid not in player_registry:
                player_registry[pid] = pname

    dq_report = validate_data_quality(data)
    dq_path = os.path.join(output_dir, "data_quality_report.json")
    with open(dq_path, "w") as f:
        json.dump(dq_report, f, indent=2, default=str)
    print(f"  Data quality report saved: {dq_path}", flush=True)

    # ===================================================================
    # PHASE 2: DATA PREPARATION
    # ===================================================================
    print("\n[PHASE 2] Preparing ball-by-ball data...", flush=True)
    bbb_filtered = bbb[bbb["innings"].isin([1, 2])].copy()
    print(f"  Filtered to innings 1 & 2: {len(bbb_filtered):,} deliveries", flush=True)

    df = prepare_ball_by_ball(bbb_filtered, data["matches"], data["competitions"])
    print(f"  Prepared data: {len(df):,} deliveries", flush=True)

    print("  Computing innings state (O(1) target lookup)...", flush=True)
    df = compute_innings_state(df)
    print(f"  Innings state computed: {len(df):,} deliveries", flush=True)

    # ===================================================================
    # PHASE 3: PRESSURE INDEX
    # ===================================================================
    print("\n[PHASE 3] Calculating Pressure Index...", flush=True)
    pi_config = config["pressure_index"]
    df = calculate_pressure_index(df, pi_config)
    
    df, high_thresh, normal_thresh = classify_pressure(
        df, 
        pi_config["high_pressure_percentile"],
        pi_config["normal_pressure_percentile"]
    )
    
    print(f"  Pressure Index range: {df['pressure_index'].min():.3f} - {df['pressure_index'].max():.3f}", flush=True)
    print(f"  Mean PI: {df['pressure_index'].mean():.3f}, Median: {df['pressure_index'].median():.3f}", flush=True)
    print(f"  High pressure threshold (P{pi_config['high_pressure_percentile']}): {high_thresh:.3f}", flush=True)
    print(f"  Normal baseline threshold (P{pi_config['normal_pressure_percentile']}): {normal_thresh:.3f}", flush=True)
    print(f"  High pressure deliveries: {(df['pressure_category'] == 'high').sum():,}", flush=True)
    print(f"  Normal baseline deliveries: {(df['pressure_category'] == 'normal').sum():,}", flush=True)

    # Save pressure features
    pressure_cols = [
        "match_id", "innings", "innings_ball_num", "overid", "over_ball_num", "striker_id", "bowler_id",
        "batter_runs", "total_runs", "bowler_runs", "is_wicket", "is_bowler_wicket",
        "is_legal", "ball_faced", "innings_phase", "is_chase",
        "cum_runs_before", "cum_wickets_before", "balls_remaining", "wickets_remaining",
        "current_rr", "required_rr", "runs_required", "target",
        "pi_chase_urgency", "pi_resource", "pi_phase", "pi_competitiveness",
        "pi_first_inn_par", "pressure_index", "pressure_category",
        "match_format", "season", "comp_name"
    ]
    existing_cols = [c for c in pressure_cols if c in df.columns]
    df[existing_cols].to_parquet(
        os.path.join(processed_dir, "pressure_delivery_features.parquet"),
        index=False
    )
    df[existing_cols].to_parquet(
        os.path.join(output_dir, "pressure_delivery_features.parquet"),
        index=False
    )
    print("  Pressure features saved to parquet", flush=True)

    # ===================================================================
    # PHASE 4: EXPECTED PERFORMANCE MODELS
    # ===================================================================
    print("\n[PHASE 4] Building expected performance models...", flush=True)
    
    print("  Training batting expected model (GroupKFold by match)...", flush=True)
    bat_model_df, bat_models, bat_feat_imp = build_batting_expected_model(df)
    print(f"  Batting model: {len(bat_model_df):,} predictions", flush=True)
    
    df = df.merge(
        bat_model_df[["match_id", "innings", "innings_ball_num",
                       "expected_batting_runs", "batting_impact"]].drop_duplicates(),
        on=["match_id", "innings", "innings_ball_num"],
        how="left"
    )
    
    print("  Training bowling expected model (GroupKFold by match)...", flush=True)
    bowl_model_df, bowl_models, bowl_feat_imp = build_bowling_expected_model(df)
    print(f"  Bowling model: {len(bowl_model_df):,} predictions", flush=True)
    
    df = df.merge(
        bowl_model_df[["match_id", "innings", "innings_ball_num",
                        "expected_bowling_runs", "bowling_impact"]].drop_duplicates(),
        on=["match_id", "innings", "innings_ball_num"],
        how="left"
    )

    # Save full processed data
    df.to_parquet(os.path.join(processed_dir, "full_processed_data.parquet"), index=False)

    # ===================================================================
    # PHASE 5: BATTING RATINGS & THREE RANKINGS
    # ===================================================================
    print("\n[PHASE 5] Computing batting ratings...", flush=True)
    bat_agg = compute_batting_aggregates(df)
    bat_consistency = compute_batting_consistency(df)
    bat_ratings = compute_batting_ratings(bat_agg, bat_consistency, config["batting"])
    
    # Map player names & competitions
    bat_ratings["player_name"] = bat_ratings["striker_id"].map(player_registry)
    
    # Player competition associations
    player_comps = df.groupby("striker_id")["comp_name"].unique().apply(
        lambda comps: ", ".join(sorted(set(str(c) for c in comps if pd.notna(c))))
    ).to_dict()
    bat_ratings["competitions"] = bat_ratings["striker_id"].map(player_comps)
    
    eligible_batters = bat_ratings[bat_ratings["eligible"]].copy()
    
    # Empirical Bayes shrinkage with prior_sample = 75.0
    prior_n = config["batting"].get("prior_sample", 75.0)
    eligible_batters = empirical_bayes_shrinkage(
        eligible_batters,
        rating_col="batting_pressure_rating",
        sample_col="balls_faced_pressure",
        id_col="striker_id",
        prior_sample=prior_n
    )
    
    # 1. Primary Ranking: Context-Adjusted Shrunk Pressure Rating
    primary_batters = eligible_batters.sort_values("shrunk_rating", ascending=False).reset_index(drop=True)
    primary_batters["rank"] = range(1, len(primary_batters) + 1)
    
    # 2. Comparison Ranking 1: Raw Pressure Performance (Impact per ball)
    raw_batters = eligible_batters.sort_values("impact_per_ball_pressure", ascending=False).reset_index(drop=True)
    raw_batters["rank_raw"] = range(1, len(raw_batters) + 1)
    
    # 3. Comparison Ranking 2: Pressure Uplift Over Baseline
    uplift_batters = eligible_batters.sort_values("sr_uplift", ascending=False).reset_index(drop=True)
    uplift_batters["rank_uplift"] = range(1, len(uplift_batters) + 1)

    top10_batters = primary_batters.head(10)
    print(f"\n  === PRIMARY TOP 10 BATTERS UNDER PRESSURE (Context-Adjusted + Shrunk) ===", flush=True)
    for _, row in top10_batters.iterrows():
        print(f"  #{row['rank']:2d} {row['player_name']:<22s} Rating: {row['shrunk_rating']:.4f} "
              f"P_Balls: {int(row['balls_faced_pressure']):3d} P_SR: {row['strike_rate_pressure']:.1f} "
              f"NP_SR: {row['strike_rate_normal']:.1f} Uplift: {row['sr_uplift']:+5.1f} Matches: {int(row['pressure_matches'])}", flush=True)

    # ===================================================================
    # PHASE 6: BOWLING RATINGS & THREE RANKINGS
    # ===================================================================
    print("\n[PHASE 6] Computing bowling ratings...", flush=True)
    bowl_agg = compute_bowling_aggregates(df)
    bowl_consistency = compute_bowling_consistency(df)
    wicket_values = compute_wicket_value(df)
    bowl_ratings = compute_bowling_ratings(bowl_agg, bowl_consistency, wicket_values, config["bowling"])
    
    bowl_ratings["player_name"] = bowl_ratings["bowler_id"].map(player_registry)
    bowl_comps = df.groupby("bowler_id")["comp_name"].unique().apply(
        lambda comps: ", ".join(sorted(set(str(c) for c in comps if pd.notna(c))))
    ).to_dict()
    bowl_ratings["competitions"] = bowl_ratings["bowler_id"].map(bowl_comps)
    
    eligible_bowlers = bowl_ratings[bowl_ratings["eligible"]].copy()
    
    prior_w = config["bowling"].get("prior_sample", 75.0)
    eligible_bowlers = empirical_bayes_shrinkage(
        eligible_bowlers,
        rating_col="bowling_pressure_rating",
        sample_col="legal_balls_pressure",
        id_col="bowler_id",
        prior_sample=prior_w
    )
    
    # 1. Primary Ranking: Context-Adjusted Shrunk Pressure Rating
    primary_bowlers = eligible_bowlers.sort_values("shrunk_rating", ascending=False).reset_index(drop=True)
    primary_bowlers["rank"] = range(1, len(primary_bowlers) + 1)
    
    # 2. Comparison Ranking 1: Raw Pressure Bowling (Runs Saved / Economy)
    raw_bowlers = eligible_bowlers.sort_values("economy_pressure", ascending=True).reset_index(drop=True)
    raw_bowlers["rank_raw"] = range(1, len(raw_bowlers) + 1)
    
    # 3. Comparison Ranking 2: Economy Improvement Over Baseline
    uplift_bowlers = eligible_bowlers.sort_values("economy_improvement", ascending=False).reset_index(drop=True)
    uplift_bowlers["rank_uplift"] = range(1, len(uplift_bowlers) + 1)

    top10_bowlers = primary_bowlers.head(10)
    print(f"\n  === PRIMARY TOP 10 BOWLERS UNDER PRESSURE (Context-Adjusted + Shrunk) ===", flush=True)
    for _, row in top10_bowlers.iterrows():
        print(f"  #{row['rank']:2d} {row['player_name']:<22s} Rating: {row['shrunk_rating']:.4f} "
              f"P_Balls: {int(row['legal_balls_pressure']):3d} P_Econ: {row['economy_pressure']:.2f} "
              f"NP_Econ: {row['economy_normal']:.2f} Imprv: {row['economy_improvement']:+4.2f} Wkts: {int(row['bowler_wickets_pressure'])}", flush=True)

    # ===================================================================
    # PHASE 7: ROBUSTNESS ANALYSIS
    # ===================================================================
    print("\n[PHASE 7] Running robustness analysis...", flush=True)
    
    print("  Pressure threshold sensitivity...", flush=True)
    bat_sens, bowl_sens = sensitivity_pressure_thresholds(df, player_registry)
    
    print("  Bootstrap analysis (50 iterations)...", flush=True)
    bat_boot, bowl_boot = bootstrap_rankings(df, player_registry, n_bootstrap=50, top_n=10)

    # ===================================================================
    # PHASE 8: EXPORT ALL OUTPUTS & AUDIT TABLES
    # ===================================================================
    print("\n[PHASE 8] Exporting outputs and player audit tables...", flush=True)
    
    # Primary top 10 files
    bat_export_cols = [
        "rank", "player_name", "striker_id", "shrunk_rating", "batting_pressure_rating",
        "balls_faced_pressure", "runs_pressure", "strike_rate_pressure", "balls_faced_normal",
        "runs_normal", "strike_rate_normal", "sr_uplift", "pressure_uplift",
        "impact_per_ball_pressure", "impact_per_ball_normal",
        "total_balls", "total_runs", "total_matches", "pressure_matches",
        "weight", "shrinkage_factor", "rating_se", "ci_lower", "ci_upper", "reliability_level", "competitions"
    ]
    avail_bat_cols = [c for c in bat_export_cols if c in top10_batters.columns]
    top10_batters[avail_bat_cols].to_csv(os.path.join(output_dir, "batter_rankings.csv"), index=False)
    
    bowl_export_cols = [
        "rank", "player_name", "bowler_id", "shrunk_rating", "bowling_pressure_rating",
        "legal_balls_pressure", "bowler_runs_conceded_pressure", "economy_pressure",
        "legal_balls_normal", "bowler_runs_conceded_normal", "economy_normal",
        "economy_improvement", "pressure_uplift",
        "impact_per_ball_pressure", "impact_per_ball_normal", "bowler_wickets_pressure",
        "total_balls", "total_runs", "total_wickets", "total_matches", "pressure_matches",
        "weight", "shrinkage_factor", "rating_se", "ci_lower", "ci_upper", "reliability_level", "competitions"
    ]
    avail_bowl_cols = [c for c in bowl_export_cols if c in top10_bowlers.columns]
    top10_bowlers[avail_bowl_cols].to_csv(os.path.join(output_dir, "bowler_rankings.csv"), index=False)
    
    # Comparison rankings
    raw_batters[["rank_raw", "player_name", "striker_id", "impact_per_ball_pressure", "strike_rate_pressure", "balls_faced_pressure", "pressure_matches"]].head(15).to_csv(
        os.path.join(output_dir, "batter_rankings_raw.csv"), index=False
    )
    uplift_batters[["rank_uplift", "player_name", "striker_id", "sr_uplift", "pressure_uplift", "strike_rate_pressure", "strike_rate_normal", "balls_faced_pressure", "balls_faced_normal"]].head(15).to_csv(
        os.path.join(output_dir, "batter_rankings_uplift.csv"), index=False
    )
    
    raw_bowlers[["rank_raw", "player_name", "bowler_id", "economy_pressure", "impact_per_ball_pressure", "bowler_wickets_pressure", "legal_balls_pressure", "pressure_matches"]].head(15).to_csv(
        os.path.join(output_dir, "bowler_rankings_raw.csv"), index=False
    )
    uplift_bowlers[["rank_uplift", "player_name", "bowler_id", "economy_improvement", "pressure_uplift", "economy_pressure", "economy_normal", "legal_balls_pressure", "legal_balls_normal"]].head(15).to_csv(
        os.path.join(output_dir, "bowler_rankings_uplift.csv"), index=False
    )
    
    # All qualifying player ratings
    all_bat = primary_batters.copy()
    all_bat["player_type"] = "batter"
    all_bat["player_id"] = all_bat["striker_id"]
    all_bat.to_csv(os.path.join(output_dir, "all_batter_ratings.csv"), index=False)
    
    all_bowl = primary_bowlers.copy()
    all_bowl["player_type"] = "bowler"
    all_bowl["player_id"] = all_bowl["bowler_id"]
    all_bowl.to_csv(os.path.join(output_dir, "all_bowler_ratings.csv"), index=False)
    
    all_players = pd.concat([
        all_bat[["player_id", "player_name", "player_type", "shrunk_rating", "reliability_level", "eligible", "competitions"]],
        all_bowl[["player_id", "player_name", "player_type", "shrunk_rating", "reliability_level", "eligible", "competitions"]]
    ], ignore_index=True)
    all_players.to_csv(os.path.join(output_dir, "all_player_ratings.csv"), index=False)
    
    # Full player audit table
    audit_bat_rows = []
    for _, r in primary_batters.head(15).iterrows():
        audit_bat_rows.append({
            "role": "Batter",
            "player_id": r["striker_id"],
            "player_name": r["player_name"],
            "competitions": r.get("competitions", "")[:60] + "...",
            "total_matches": r["total_matches"],
            "pressure_matches": r["pressure_matches"],
            "pressure_balls": r["balls_faced_pressure"],
            "pressure_runs": r["runs_pressure"],
            "pressure_sr": round(r["strike_rate_pressure"], 2),
            "normal_balls": r["balls_faced_normal"],
            "normal_runs": r["runs_normal"],
            "normal_sr": round(r["strike_rate_normal"], 2),
            "expected_runs_pressure": round(r.get("total_expected_pressure", r["runs_pressure"] - r["impact_per_ball_pressure"]*r["balls_faced_pressure"]), 1),
            "runs_above_expectation": round(r["impact_per_ball_pressure"] * r["balls_faced_pressure"], 1),
            "pressure_uplift_sr": round(r["sr_uplift"], 2),
            "uncertainty_se": round(r["rating_se"], 4),
            "ci_95": f"[{r['ci_lower']:.3f}, {r['ci_upper']:.3f}]",
            "final_shrunk_rating": round(r["shrunk_rating"], 4)
        })
    pd.DataFrame(audit_bat_rows).to_csv(os.path.join(output_dir, "player_audit_table.csv"), index=False)

    # Save sensitivity and bootstrap files
    bat_boot.to_csv(os.path.join(output_dir, "batting_bootstrap.csv"), index=False)
    bowl_boot.to_csv(os.path.join(output_dir, "bowling_bootstrap.csv"), index=False)
    bat_sens.to_csv(os.path.join(output_dir, "batting_threshold_sensitivity.csv"), index=False)
    bowl_sens.to_csv(os.path.join(output_dir, "bowling_threshold_sensitivity.csv"), index=False)
    
    # Save robustness analysis summary
    robustness = pd.concat([bat_boot.head(10), bowl_boot.head(10)], ignore_index=True)
    robustness.to_csv(os.path.join(output_dir, "robustness_analysis.csv"), index=False)
    
    # Pressure analysis summary JSON
    pressure_summary = {
        "total_deliveries": int(len(df)),
        "high_pressure_deliveries": int((df["pressure_category"] == "high").sum()),
        "normal_pressure_deliveries": int((df["pressure_category"] == "normal").sum()),
        "high_pressure_threshold": float(high_thresh),
        "normal_pressure_threshold": float(normal_thresh),
        "mean_pressure_index": float(df["pressure_index"].mean()),
        "median_pressure_index": float(df["pressure_index"].median()),
        "total_matches": int(df["match_id"].nunique()),
        "total_batters": int(df["striker_id"].nunique()),
        "total_bowlers": int(df["bowler_id"].nunique()),
        "qualifying_batters": int(len(primary_batters)),
        "qualifying_bowlers": int(len(primary_bowlers)),
        "top10_batters": top10_batters["player_name"].tolist(),
        "top10_bowlers": top10_bowlers["player_name"].tolist(),
        "batting_model_importances": bat_feat_imp,
        "bowling_model_importances": bowl_feat_imp,
    }
    with open(os.path.join(output_dir, "pressure_analysis.json"), "w") as f:
        json.dump(pressure_summary, f, indent=2, default=str)
        
    elapsed = time.time() - start_time
    print(f"\n{'=' * 70}")
    print(f"  Pipeline completed in {elapsed:.1f} seconds")
    print(f"  Outputs successfully saved to: {output_dir}")
    print(f"{'=' * 70}", flush=True)


if __name__ == "__main__":
    main()
