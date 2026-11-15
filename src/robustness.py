"""
robustness.py — Sensitivity and robustness analysis for rankings.

Tests ranking stability under alternative model specifications:
- Different pressure thresholds
- Different minimum sample sizes
- Competition-specific rankings
- Bootstrap confidence intervals
"""
import numpy as np
import pandas as pd
from src.pressure_index import classify_pressure
from src.batting_model import compute_batting_aggregates, compute_batting_consistency, compute_batting_ratings
from src.bowling_model import compute_bowling_aggregates, compute_bowling_consistency, compute_bowling_ratings, compute_wicket_value
from src.statistical_shrinkage import empirical_bayes_shrinkage


def sensitivity_pressure_thresholds(df, player_registry, thresholds=None):
    """
    Test ranking stability under different pressure threshold definitions.
    """
    if thresholds is None:
        thresholds = [
            {"high": 80, "normal": 20, "label": "Top 20%"},
            {"high": 75, "normal": 25, "label": "Top 25%"},
            {"high": 70, "normal": 30, "label": "Top 30%"},
        ]
    
    bat_results = []
    bowl_results = []
    
    for thresh in thresholds:
        df_t = df.copy()
        df_t, h_thresh, n_thresh = classify_pressure(df_t, thresh["high"], thresh["normal"])
        
        # Batting
        bat_agg = compute_batting_aggregates(df_t)
        bat_con = compute_batting_consistency(df_t)
        bat_rat = compute_batting_ratings(bat_agg, bat_con)
        eligible = bat_rat[bat_rat["eligible"]].head(10).copy()
        eligible["threshold"] = thresh["label"]
        eligible["player_name"] = eligible["striker_id"].map(player_registry)
        bat_results.append(eligible[["striker_id", "player_name", "batting_pressure_rating", "threshold"]])
        
        # Bowling
        bowl_agg = compute_bowling_aggregates(df_t)
        bowl_con = compute_bowling_consistency(df_t)
        wv = compute_wicket_value(df_t)
        bowl_rat = compute_bowling_ratings(bowl_agg, bowl_con, wv)
        eligible_b = bowl_rat[bowl_rat["eligible"]].head(10).copy()
        eligible_b["threshold"] = thresh["label"]
        eligible_b["player_name"] = eligible_b["bowler_id"].map(player_registry)
        bowl_results.append(eligible_b[["bowler_id", "player_name", "bowling_pressure_rating", "threshold"]])
    
    return pd.concat(bat_results), pd.concat(bowl_results)


def sensitivity_sample_size(df, player_registry, min_balls_list=None):
    """
    Test ranking stability under different minimum sample size requirements.
    """
    if min_balls_list is None:
        min_balls_list = [20, 30, 40, 50]
    
    bat_results = []
    bowl_results = []
    
    for min_b in min_balls_list:
        bat_config = {
            "context_adjusted_weight": 0.35,
            "pressure_uplift_weight": 0.30,
            "consistency_weight": 0.20,
            "reliability_weight": 0.15,
            "min_pressure_balls": min_b,
            "min_total_balls": min_b * 3,
            "min_matches": 3,
            "min_pressure_matches": 2,
        }
        
        bat_agg = compute_batting_aggregates(df)
        bat_con = compute_batting_consistency(df)
        bat_rat = compute_batting_ratings(bat_agg, bat_con, bat_config)
        eligible = bat_rat[bat_rat["eligible"]].head(10).copy()
        eligible["min_balls"] = min_b
        eligible["player_name"] = eligible["striker_id"].map(player_registry)
        bat_results.append(eligible[["striker_id", "player_name", "batting_pressure_rating", "min_balls"]])
        
        bowl_config = {
            "context_adjusted_weight": 0.35,
            "pressure_uplift_weight": 0.30,
            "wicket_impact_weight": 0.15,
            "consistency_weight": 0.10,
            "reliability_weight": 0.10,
            "min_pressure_balls": min_b,
            "min_total_balls": min_b * 3,
            "min_matches": 3,
            "min_pressure_matches": 2,
        }
        
        bowl_agg = compute_bowling_aggregates(df)
        bowl_con = compute_bowling_consistency(df)
        wv = compute_wicket_value(df)
        bowl_rat = compute_bowling_ratings(bowl_agg, bowl_con, wv, bowl_config)
        eligible_b = bowl_rat[bowl_rat["eligible"]].head(10).copy()
        eligible_b["min_balls"] = min_b
        eligible_b["player_name"] = eligible_b["bowler_id"].map(player_registry)
        bowl_results.append(eligible_b[["bowler_id", "player_name", "bowling_pressure_rating", "min_balls"]])
    
    return pd.concat(bat_results), pd.concat(bowl_results)


def bootstrap_rankings(df, player_registry, n_bootstrap=50, top_n=10):
    """
    Bootstrap confidence intervals for rankings by resampling matches.
    Pre-groups by match_id for rapid O(1) sampling.
    """
    match_ids = df["match_id"].unique()
    n_matches = len(match_ids)
    
    # Pre-index match dataframes
    match_groups = dict(tuple(df.groupby("match_id")))
    
    bat_rank_counts = {}  # player_id -> list of ranks
    bowl_rank_counts = {}
    
    for i in range(n_bootstrap):
        # Sample matches with replacement
        sampled_matches = np.random.choice(match_ids, size=n_matches, replace=True)
        boot_dfs = [match_groups[mid] for mid in sampled_matches if mid in match_groups]
        if not boot_dfs:
            continue
            
        boot_df = pd.concat(boot_dfs, ignore_index=True)
        
        try:
            # Batting rankings
            bat_agg = compute_batting_aggregates(boot_df)
            bat_con = compute_batting_consistency(boot_df)
            bat_rat = compute_batting_ratings(bat_agg, bat_con)
            eligible = bat_rat[bat_rat["eligible"]].head(top_n)
            
            for rank, (_, row) in enumerate(eligible.iterrows(), 1):
                pid = row["striker_id"]
                if pid not in bat_rank_counts:
                    bat_rank_counts[pid] = []
                bat_rank_counts[pid].append(rank)
            
            # Bowling rankings
            bowl_agg = compute_bowling_aggregates(boot_df)
            bowl_con = compute_bowling_consistency(boot_df)
            wv = compute_wicket_value(boot_df)
            bowl_rat = compute_bowling_ratings(bowl_agg, bowl_con, wv)
            eligible_b = bowl_rat[bowl_rat["eligible"]].head(top_n)
            
            for rank, (_, row) in enumerate(eligible_b.iterrows(), 1):
                pid = row["bowler_id"]
                if pid not in bowl_rank_counts:
                    bowl_rank_counts[pid] = []
                bowl_rank_counts[pid].append(rank)
        except Exception:
            continue
    
    # Summarise
    bat_boot = []
    for pid, ranks in bat_rank_counts.items():
        bat_boot.append({
            "player_id": pid,
            "player_name": player_registry.get(pid, f"ID_{pid}"),
            "mean_rank": np.mean(ranks),
            "median_rank": np.median(ranks),
            "rank_std": np.std(ranks),
            "top10_freq": len(ranks) / n_bootstrap,
            "best_rank": min(ranks),
            "worst_rank": max(ranks),
            "appearances": len(ranks),
        })
    
    bowl_boot = []
    for pid, ranks in bowl_rank_counts.items():
        bowl_boot.append({
            "player_id": pid,
            "player_name": player_registry.get(pid, f"ID_{pid}"),
            "mean_rank": np.mean(ranks),
            "median_rank": np.median(ranks),
            "rank_std": np.std(ranks),
            "top10_freq": len(ranks) / n_bootstrap,
            "best_rank": min(ranks),
            "worst_rank": max(ranks),
            "appearances": len(ranks),
        })
    
    bat_boot_df = pd.DataFrame(bat_boot).sort_values("mean_rank")
    bowl_boot_df = pd.DataFrame(bowl_boot).sort_values("mean_rank")
    
    return bat_boot_df, bowl_boot_df


def competition_sensitivity(df, player_registry, comps_df):
    """
    Compare rankings when using only IPL or only T20I data.
    """
    results = {}
    
    for fmt_label, fmt_filter in [("IPL", "T20"), ("T20I", "T20I")]:
        fmt_df = df[df["match_format"] == fmt_filter].copy()
        
        if len(fmt_df) < 1000:
            continue
        
        # Re-classify pressure for this subset
        fmt_df, _, _ = classify_pressure(fmt_df)
        
        bat_agg = compute_batting_aggregates(fmt_df)
        bat_con = compute_batting_consistency(fmt_df)
        bat_rat = compute_batting_ratings(bat_agg, bat_con)
        bat_rat["player_name"] = bat_rat["striker_id"].map(player_registry)
        
        bowl_agg = compute_bowling_aggregates(fmt_df)
        bowl_con = compute_bowling_consistency(fmt_df)
        wv = compute_wicket_value(fmt_df)
        bowl_rat = compute_bowling_ratings(bowl_agg, bowl_con, wv)
        bowl_rat["player_name"] = bowl_rat["bowler_id"].map(player_registry)
        
        results[fmt_label] = {
            "batting": bat_rat[bat_rat["eligible"]].head(10),
            "bowling": bowl_rat[bowl_rat["eligible"]].head(10),
        }
    
    return results

