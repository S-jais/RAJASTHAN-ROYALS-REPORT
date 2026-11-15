"""
data_loader.py — Load and validate all raw datasets for PRESSURE IQ.
"""
import pandas as pd
import numpy as np
import os
import yaml
import json
from pathlib import Path


def get_project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


def load_config():
    """Load the YAML configuration."""
    root = get_project_root()
    with open(root / "config.yaml", "r") as f:
        return yaml.safe_load(f)


def load_raw_data(raw_dir=None):
    """Load all raw CSV files into a dictionary of DataFrames."""
    if raw_dir is None:
        raw_dir = get_project_root() / "data" / "raw"
    else:
        raw_dir = Path(raw_dir)

    data = {}
    files = {
        "ball_by_ball": "ball_by_ball.csv",
        "matches": "matches.csv",
        "competitions": "competitions.csv",
        "teams": "teams.csv",
        "playing_eleven": "playing_eleven.csv",
        "player_mapping": "competition_team_player_mapping.csv",
    }

    for key, filename in files.items():
        path = raw_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")
        data[key] = pd.read_csv(path)
        print(f"  Loaded {filename}: {data[key].shape[0]:,} rows, {data[key].shape[1]} cols")

    return data


def build_player_registry(player_mapping_df):
    """
    Build a canonical player ID -> name mapping.
    Uses the most recent competition appearance for the canonical name.
    """
    # Group by player_id, take last occurrence (most recent comp)
    registry = (
        player_mapping_df.sort_values("comp_id")
        .drop_duplicates(subset=["player_id"], keep="last")[["player_id", "player_name"]]
        .set_index("player_id")["player_name"]
        .to_dict()
    )
    return registry


def validate_data_quality(data):
    """
    Perform comprehensive data quality checks.
    Returns a report dictionary.
    """
    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "datasets": {},
        "warnings": [],
        "errors": [],
    }

    bbb = data["ball_by_ball"]
    matches = data["matches"]
    comps = data["competitions"]
    teams = data["teams"]
    pe = data["playing_eleven"]
    pm = data["player_mapping"]

    # --- Ball by ball checks ---
    bbb_report = {
        "rows": len(bbb),
        "columns": len(bbb.columns),
        "unique_matches": bbb["match_id"].nunique(),
        "unique_batters": bbb["striker_id"].nunique(),
        "unique_bowlers": bbb["bowler_id"].nunique(),
        "innings_values": sorted(bbb["innings"].unique().tolist()),
        "missing_values": bbb.isnull().sum().to_dict(),
        "duplicates": int(bbb.duplicated().sum()),
    }

    # Check runs range
    if bbb["runs"].min() < 0 or bbb["runs"].max() > 6:
        report["warnings"].append(f"Unusual runs values: min={bbb['runs'].min()}, max={bbb['runs'].max()}")

    # Check extras encoding
    extras_vals = bbb["extras1_runs"].unique().tolist()
    bbb_report["extras1_runs_values"] = sorted(extras_vals)

    # Validate dismissal attribution
    dismissals = bbb[bbb["is_wicket"] == True]
    non_striker_dismissed = dismissals[dismissals["dismissed_player_id"] != dismissals["striker_id"]]
    bbb_report["total_wickets"] = len(dismissals)
    bbb_report["non_striker_dismissals"] = len(non_striker_dismissed)
    bbb_report["dismissal_types"] = dismissals["dismissal_type"].value_counts().to_dict()

    # Check over numbering
    max_over = bbb["overid"].max()
    bbb_report["max_over_id"] = int(max_over)

    report["datasets"]["ball_by_ball"] = bbb_report

    # --- Matches checks ---
    m_report = {
        "rows": len(matches),
        "unique_matches": matches["match_id"].nunique(),
        "matches_with_result": int(matches["win_team_id"].notna().sum()),
        "no_result_matches": int(matches["win_team_id"].isna().sum()),
        "dls_matches": int(matches["revised_target"].notna().sum()),
        "date_range": [matches["match_date"].min(), matches["match_date"].max()],
    }
    report["datasets"]["matches"] = m_report

    # --- Competitions checks ---
    c_report = {
        "rows": len(comps),
        "formats": comps["match_format"].unique().tolist(),
        "seasons": sorted(comps["season"].unique().tolist()),
        "ipl_seasons": comps[comps["comp_name"].str.contains("IPL", case=False)]["season"].tolist(),
    }
    report["datasets"]["competitions"] = c_report

    # --- Cross-validation ---
    bbb_match_ids = set(bbb["match_id"].unique())
    match_ids = set(matches["match_id"].unique())
    orphan_bbb = bbb_match_ids - match_ids
    orphan_matches = match_ids - bbb_match_ids

    if orphan_bbb:
        report["warnings"].append(f"{len(orphan_bbb)} match_ids in ball_by_ball not found in matches")
    if orphan_matches:
        report["warnings"].append(f"{len(orphan_matches)} match_ids in matches with no ball_by_ball data")

    report["datasets"]["cross_validation"] = {
        "bbb_matches_in_matches": len(bbb_match_ids & match_ids),
        "orphan_bbb_matches": len(orphan_bbb),
        "orphan_match_records": len(orphan_matches),
    }

    # Player registry
    registry = build_player_registry(pm)
    bbb_striker_ids = set(bbb["striker_id"].unique())
    bbb_bowler_ids = set(bbb["bowler_id"].unique())
    all_bbb_players = bbb_striker_ids | bbb_bowler_ids
    unmapped_players = all_bbb_players - set(registry.keys())
    if unmapped_players:
        report["warnings"].append(f"{len(unmapped_players)} player IDs in ball_by_ball not found in player mapping")

    report["datasets"]["players"] = {
        "registry_size": len(registry),
        "unique_batters_in_bbb": len(bbb_striker_ids),
        "unique_bowlers_in_bbb": len(bbb_bowler_ids),
        "unmapped_players": len(unmapped_players),
    }

    return report


def prepare_ball_by_ball(bbb, matches, comps):
    """
    Prepare and enrich the ball-by-ball DataFrame with match context.
    
    This function:
    1. Merges match and competition info
    2. Computes correct run attributions (batter runs vs total runs)
    3. Identifies legal deliveries
    4. Computes innings-level cumulative state
    """
    # Merge match info
    match_cols = ["match_id", "comp_id", "match_date", "home_team_id", "away_team_id",
                  "win_team_id", "result", "first_inn_revised_overs", 
                  "second_inn_revised_overs", "revised_target"]
    df = bbb.merge(matches[match_cols], on="match_id", how="left")

    # Merge competition info
    df = df.merge(comps[["comp_id", "comp_name", "match_format", "season"]], on="comp_id", how="left")

    # --- Run attribution ---
    # 'runs' column = batter runs
    # extras1_runs encoding: 6=normal, 1=no-ball, 2=wide, 3=legbye, 4/5=bye/penalty
    # extras_2_runs = additional extra runs
    
    df["batter_runs"] = df["runs"].copy()
    df["is_wide"] = df["extras_type"] == "wide"
    df["is_noball"] = df["extras_type"] == "Overstep"
    df["is_legbye"] = df["extras_type"] == "legbyes"
    df["is_bye"] = df["extras_type"] == "byes"
    
    # On wides, batter_runs should be 0 (already is in the data)
    # On leg-byes, batter_runs should be 0 (already is, mostly)
    
    # Wide runs: extras_2_runs on wide deliveries + 1 for the wide itself
    df["wide_runs"] = np.where(df["is_wide"], 1 + df["extras_2_runs"], 0)
    
    # No-ball runs: 1 for the no-ball + batter_runs + extras_2_runs
    df["noball_runs"] = np.where(df["is_noball"], 1 + df["extras_2_runs"], 0)
    
    # Leg-bye runs
    df["legbye_runs"] = np.where(df["is_legbye"], df["extras_2_runs"], 0)
    
    # Bye runs 
    df["bye_runs"] = np.where(df["is_bye"], df["extras_2_runs"], 0)
    
    # Total runs off the delivery
    df["total_runs"] = df["batter_runs"] + df["wide_runs"] + df["noball_runs"] + df["legbye_runs"] + df["bye_runs"]
    
    # Runs charged to bowler: batter_runs + wides + no-balls (not byes/leg-byes)
    df["bowler_runs"] = df["batter_runs"] + df["wide_runs"] + df["noball_runs"]
    
    # --- Legal delivery flag ---
    # Wides and no-balls are NOT legal deliveries
    df["is_legal"] = ~(df["is_wide"] | df["is_noball"])
    
    # --- Ball faced by batter ---
    # Wides are NOT faced by batter; no-balls ARE faced
    df["ball_faced"] = np.where(df["is_wide"], 0, 1)
    
    # --- Bowler-credited wicket ---
    bowler_wicket_types = ["Bowled", "Caught", "LBW", "Stump", "Hit Wicket"]
    df["is_bowler_wicket"] = (
        df["is_wicket"] & 
        df["dismissal_type"].isin(bowler_wicket_types)
    )
    
    # --- Dot ball (no runs scored off the bat, legal delivery, not extras scoring) ---
    df["is_dot"] = (df["total_runs"] == 0) & df["is_legal"]
    
    # --- Is boundary ---
    df["is_boundary"] = df["is_four"] | df["is_six"]
    
    # --- Innings phase ---
    # overid is 1-indexed
    df["over_0idx"] = df["overid"] - 1  # 0-indexed over number
    conditions = [
        df["over_0idx"] <= 5,
        (df["over_0idx"] >= 6) & (df["over_0idx"] <= 14),
        df["over_0idx"] >= 15,
    ]
    choices = ["powerplay", "middle", "death"]
    df["innings_phase"] = np.select(conditions, choices, default="middle")
    
    # --- Is second innings (chase) ---
    df["is_chase"] = df["innings"] == 2
    
    # Convert match_date to datetime
    df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
    
    # Sort by match, innings, delivery order
    df = df.sort_values(["match_id", "innings", "innings_ball_num"]).reset_index(drop=True)
    
    return df


def compute_innings_state(df):
    """
    Compute cumulative innings state for each delivery.
    This is critical for pressure index calculation.
    
    For each delivery, compute:
    - cumulative runs scored in the innings so far
    - wickets fallen so far
    - legal balls bowled so far
    - balls remaining (estimated)
    - For 2nd innings: runs required, required run rate
    """
    # Group by match_id and innings
    results = []
    # Precompute first innings totals for O(1) target lookup
    first_inn_totals = df[df["innings"] == 1].groupby("match_id")["total_runs"].sum().to_dict()
    
    for (match_id, innings), group in df.groupby(["match_id", "innings"]):
        g = group.copy()
        
        # Cumulative runs (total runs, before this ball)
        g["cum_runs_before"] = g["total_runs"].cumsum().shift(1, fill_value=0)
        g["cum_runs_after"] = g["total_runs"].cumsum()
        
        # Cumulative wickets before this ball
        g["cum_wickets_before"] = g["is_wicket"].astype(int).cumsum().shift(1, fill_value=0)
        g["cum_wickets_after"] = g["is_wicket"].astype(int).cumsum()
        
        # Cumulative legal balls before this ball
        g["cum_legal_balls_before"] = g["is_legal"].astype(int).cumsum().shift(1, fill_value=0)
        g["cum_legal_balls_after"] = g["is_legal"].astype(int).cumsum()
        
        # Determine total overs for the innings
        # Check for revised overs (DLS)
        if innings == 1:
            revised = g["first_inn_revised_overs"].iloc[0]
        else:
            revised = g["second_inn_revised_overs"].iloc[0]
        
        if pd.notna(revised) and revised > 0:
            total_legal_balls = int(revised) * 6
        else:
            total_legal_balls = 120  # Standard 20 overs
        
        g["total_innings_balls"] = total_legal_balls
        g["balls_remaining"] = np.maximum(total_legal_balls - g["cum_legal_balls_before"], 0)
        g["wickets_remaining"] = np.maximum(10 - g["cum_wickets_before"], 0)
        
        # Current run rate (per over = per 6 legal balls)
        g["current_rr"] = np.where(
            g["cum_legal_balls_before"] > 0,
            g["cum_runs_before"] * 6.0 / g["cum_legal_balls_before"],
            0.0
        )
        
        # For second innings: target and required run rate
        if innings == 2:
            first_inn_total = first_inn_totals.get(match_id, 0)
            
            # Check for revised target (DLS)
            revised_target = g["revised_target"].iloc[0]
            if pd.notna(revised_target) and revised_target > 0:
                target = int(revised_target)
            else:
                target = first_inn_total + 1
            
            g["target"] = target
            g["runs_required"] = np.maximum(target - g["cum_runs_before"], 0)
            g["required_rr"] = np.where(
                g["balls_remaining"] > 0,
                g["runs_required"] * 6.0 / g["balls_remaining"],
                0.0
            )
            g["rr_diff"] = g["required_rr"] - g["current_rr"]
        else:
            g["target"] = np.nan
            g["runs_required"] = np.nan
            g["required_rr"] = np.nan
            g["rr_diff"] = np.nan
        
        results.append(g)
    
    return pd.concat(results, ignore_index=True)

