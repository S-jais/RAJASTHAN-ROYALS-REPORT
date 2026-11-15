"""
test_pressure_index.py — Tests for Pressure Index calculation, monotonicity, and boundary conditions.
"""
import pytest
import numpy as np
import pandas as pd
from src.pressure_index import calculate_pressure_index, compute_chase_urgency, compute_resource_pressure


def create_scenario_df(rows):
    """Create a standardized dataframe for testing pressure logic."""
    df = pd.DataFrame(rows)
    # Fill in required standard columns if not provided
    defaults = {
        "innings": 2, "is_chase": True, "overid": 18, "over_0idx": 17,
        "innings_phase": "death", "total_innings_balls": 120,
        "cum_runs_before": 140, "cum_legal_balls_before": 102,
        "current_rr": 8.23, "target": 180,
    }
    for col, val in defaults.items():
        if col not in df.columns:
            df[col] = val
    if "runs_required" not in df.columns:
        df["runs_required"] = np.maximum(df["target"] - df["cum_runs_before"], 0)
    if "required_rr" not in df.columns:
        df["required_rr"] = np.where(df["balls_remaining"] > 0, df["runs_required"] * 6.0 / df["balls_remaining"], 0)
    return df


def test_pressure_index_range():
    """Ensure all pressure scores are strictly bounded between 0 and 1."""
    rows = [
        # Extreme high pressure: 36 off 6 balls, 1 wicket in hand
        {"balls_remaining": 6, "wickets_remaining": 1, "runs_required": 36, "is_chase": True, "innings": 2},
        # Extreme low pressure: 2 off 60 balls, 10 wickets in hand
        {"balls_remaining": 60, "wickets_remaining": 10, "runs_required": 2, "is_chase": True, "innings": 2},
        # First innings death over with 2 wickets in hand
        {"balls_remaining": 12, "wickets_remaining": 2, "is_chase": False, "innings": 1, "innings_phase": "death", "over_0idx": 18},
        # First innings powerplay with 0 wickets down
        {"balls_remaining": 114, "wickets_remaining": 10, "is_chase": False, "innings": 1, "innings_phase": "powerplay", "over_0idx": 1},
    ]
    df = create_scenario_df(rows)
    df_pi = calculate_pressure_index(df)
    
    assert (df_pi["pressure_index"] >= 0.0).all(), "Pressure index cannot be negative"
    assert (df_pi["pressure_index"] <= 1.0).all(), "Pressure index cannot exceed 1.0"


def test_chase_urgency_monotonicity():
    """Verify that requiring more runs from the same balls with same wickets increases urgency."""
    scenarios = [
        # Scenario A: Needing 15 off 12 balls (RRR = 7.5), 6 wickets left
        {"balls_remaining": 12, "wickets_remaining": 6, "runs_required": 15, "is_chase": True, "innings": 2},
        # Scenario B: Needing 30 off 12 balls (RRR = 15.0), 6 wickets left
        {"balls_remaining": 12, "wickets_remaining": 6, "runs_required": 30, "is_chase": True, "innings": 2},
        # Scenario C: Needing 45 off 12 balls (RRR = 22.5), 6 wickets left
        {"balls_remaining": 12, "wickets_remaining": 6, "runs_required": 45, "is_chase": True, "innings": 2},
    ]
    df = create_scenario_df(scenarios)
    df_pi = calculate_pressure_index(df)
    
    pi_a = df_pi.iloc[0]["pressure_index"]
    pi_b = df_pi.iloc[1]["pressure_index"]
    pi_c = df_pi.iloc[2]["pressure_index"]
    
    assert pi_a < pi_b, f"Scenario B should have higher pressure than A ({pi_b:.3f} vs {pi_a:.3f})"
    assert pi_b < pi_c, f"Scenario C should have higher pressure than B ({pi_c:.3f} vs {pi_b:.3f})"


def test_resource_pressure_wicket_depletion():
    """Verify that having fewer wickets remaining substantially increases pressure under identical runs/balls."""
    scenarios = [
        # 8 wickets in hand, needing 24 off 18 balls
        {"balls_remaining": 18, "wickets_remaining": 8, "runs_required": 24, "is_chase": True, "innings": 2},
        # 2 wickets in hand, needing 24 off 18 balls
        {"balls_remaining": 18, "wickets_remaining": 2, "runs_required": 24, "is_chase": True, "innings": 2},
        # 1 wicket in hand (last pair), needing 24 off 18 balls
        {"balls_remaining": 18, "wickets_remaining": 1, "runs_required": 24, "is_chase": True, "innings": 2},
    ]
    df = create_scenario_df(scenarios)
    df_pi = calculate_pressure_index(df)
    
    assert df_pi.iloc[0]["pressure_index"] < df_pi.iloc[1]["pressure_index"]
    assert df_pi.iloc[1]["pressure_index"] < df_pi.iloc[2]["pressure_index"]


def test_first_innings_no_target():
    """Ensure first innings deliveries without target receive meaningful pressure scores."""
    rows = [
        {"balls_remaining": 18, "wickets_remaining": 3, "is_chase": False, "innings": 1, "innings_phase": "death", "over_0idx": 17, "cum_legal_balls_before": 102},
        {"balls_remaining": 90, "wickets_remaining": 9, "is_chase": False, "innings": 1, "innings_phase": "powerplay", "over_0idx": 5, "cum_legal_balls_before": 30},
    ]
    df = create_scenario_df(rows)
    df_pi = calculate_pressure_index(df)
    
    # Death overs with only 3 wickets in hand should have substantially higher PI than Powerplay with 9 wickets
    assert df_pi.iloc[0]["pressure_index"] > df_pi.iloc[1]["pressure_index"]
    assert not np.isnan(df_pi.iloc[0]["pressure_index"])
    assert not np.isnan(df_pi.iloc[1]["pressure_index"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

