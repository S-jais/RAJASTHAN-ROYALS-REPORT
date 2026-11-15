"""
expected_performance.py — Context-adjusted expected performance models.

These models predict what an average player would produce in a given match
situation. The difference between actual and expected is the player's
context-adjusted impact.

Key design decisions:
- Player identity is NOT a feature (to avoid absorbing the signal we want to measure)
- Models use only pre-delivery match state
- Match-grouped cross-validation to avoid leakage
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, GradientBoostingRegressor
from sklearn.model_selection import GroupKFold


def build_batting_expected_model(df):
    """
    Build a model predicting expected batter runs per delivery given match context.
    
    Features: innings, over_0idx, balls_remaining, wickets_remaining,
              pressure_index, is_chase, match_format_encoded, innings_phase_encoded
    
    Target: batter_runs (on balls actually faced by the batter)
    
    Uses GroupKFold by match_id for out-of-sample predictions.
    """
    # Filter to balls faced by batter (exclude wides)
    model_df = df[df["ball_faced"] == 1].copy()
    
    # Encode categoricals
    model_df["phase_enc"] = model_df["innings_phase"].map(
        {"powerplay": 0, "middle": 1, "death": 2}
    ).fillna(1)
    
    model_df["format_enc"] = model_df["match_format"].map(
        {"T20": 0, "T20I": 1}
    ).fillna(0)
    
    features = [
        "innings", "over_0idx", "balls_remaining", "wickets_remaining",
        "pressure_index", "phase_enc", "format_enc", "cum_runs_before",
        "current_rr"
    ]
    
    # Add chase features for 2nd innings
    model_df["rrr_safe"] = model_df["required_rr"].fillna(0)
    model_df["rr_diff_safe"] = model_df["rr_diff"].fillna(0)
    model_df["runs_req_safe"] = model_df["runs_required"].fillna(0)
    features += ["rrr_safe", "rr_diff_safe", "runs_req_safe"]
    
    # Drop rows with NaN in features
    valid_mask = model_df[features].notna().all(axis=1)
    model_df = model_df[valid_mask].copy()
    
    X = model_df[features].values
    y = model_df["batter_runs"].values
    groups = model_df["match_id"].values
    
    # Out-of-sample predictions using GroupKFold
    predictions = np.zeros(len(y))
    gkf = GroupKFold(n_splits=5)
    
    models = []
    for train_idx, test_idx in gkf.split(X, y, groups):
        hgbr = HistGradientBoostingRegressor(
            max_iter=60,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
            min_samples_leaf=40,
        )
        hgbr.fit(X[train_idx], y[train_idx])
        predictions[test_idx] = hgbr.predict(X[test_idx])
        models.append(hgbr)
    
    model_df["expected_batting_runs"] = predictions
    model_df["batting_impact"] = model_df["batter_runs"] - predictions
    
    # Feature importances via fast tree
    tree_gbr = GradientBoostingRegressor(n_estimators=35, max_depth=3, random_state=42)
    sample_idx = np.random.RandomState(42).choice(len(X), size=min(25000, len(X)), replace=False)
    tree_gbr.fit(X[sample_idx], y[sample_idx])
    feature_importance = dict(zip(features, tree_gbr.feature_importances_.tolist()))
    
    return model_df, models, feature_importance


def build_bowling_expected_model(df):
    """
    Build a model predicting expected bowler runs conceded per delivery.
    
    Uses similar context features but targets bowler_runs.
    Only includes legal deliveries + wides/no-balls (all charged to bowler).
    """
    # All deliveries count for bowler analysis (including extras)
    model_df = df.copy()
    
    # Encode categoricals
    model_df["phase_enc"] = model_df["innings_phase"].map(
        {"powerplay": 0, "middle": 1, "death": 2}
    ).fillna(1)
    
    model_df["format_enc"] = model_df["match_format"].map(
        {"T20": 0, "T20I": 1}
    ).fillna(0)
    
    features = [
        "innings", "over_0idx", "balls_remaining", "wickets_remaining",
        "pressure_index", "phase_enc", "format_enc", "cum_runs_before",
        "current_rr"
    ]
    
    model_df["rrr_safe"] = model_df["required_rr"].fillna(0)
    model_df["rr_diff_safe"] = model_df["rr_diff"].fillna(0)
    model_df["runs_req_safe"] = model_df["runs_required"].fillna(0)
    features += ["rrr_safe", "rr_diff_safe", "runs_req_safe"]
    
    valid_mask = model_df[features].notna().all(axis=1)
    model_df = model_df[valid_mask].copy()
    
    X = model_df[features].values
    y = model_df["bowler_runs"].values
    groups = model_df["match_id"].values
    
    predictions = np.zeros(len(y))
    gkf = GroupKFold(n_splits=5)
    
    models = []
    for train_idx, test_idx in gkf.split(X, y, groups):
        hgbr = HistGradientBoostingRegressor(
            max_iter=60,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
            min_samples_leaf=40,
        )
        hgbr.fit(X[train_idx], y[train_idx])
        predictions[test_idx] = hgbr.predict(X[test_idx])
        models.append(hgbr)
    
    model_df["expected_bowling_runs"] = predictions
    model_df["bowling_impact"] = predictions - model_df["bowler_runs"]  # Positive = saved runs
    
    # Feature importances via fast tree
    tree_gbr = GradientBoostingRegressor(n_estimators=35, max_depth=3, random_state=42)
    sample_idx = np.random.RandomState(42).choice(len(X), size=min(25000, len(X)), replace=False)
    tree_gbr.fit(X[sample_idx], y[sample_idx])
    feature_importance = dict(zip(features, tree_gbr.feature_importances_.tolist()))
    
    return model_df, models, feature_importance

