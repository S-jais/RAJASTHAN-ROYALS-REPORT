"""
test_batting_model.py — Unit tests for batting performance metrics, uplift, and ratings.
"""
import pytest
import numpy as np
import pandas as pd
from src.batting_model import compute_batting_aggregates, compute_batting_consistency, compute_batting_ratings


def create_mock_batter_df():
    """Create a mock delivery dataset for two batters with contrasting pressure profiles."""
    records = []
    
    # Batter 1: Clutch Performer (Good under pressure, average normally)
    # 40 balls under pressure: 70 runs (SR = 175)
    # 100 balls normal: 130 runs (SR = 130) -> Positive uplift
    for i in range(40):
        records.append({
            "match_id": 1 + (i % 6), "innings": 2, "overid": 18, "over_ball_num": 1,
            "striker_id": 101, "striker_name": "Clutch Batter",
            "ball_faced": 1, "batter_runs": 2 if i % 2 == 0 else (4 if i % 3 == 0 else 0),
            "is_wicket": False, "dismissed_player_id": np.nan,
            "is_four": (i % 3 == 0), "is_six": False, "is_dot": (i % 4 == 0),
            "expected_batting_runs": 1.1, "batting_impact": 0.65,
            "pressure_category": "high"
        })
    for i in range(100):
        records.append({
            "match_id": 1 + (i % 6), "innings": 2, "overid": 8, "over_ball_num": 1,
            "striker_id": 101, "striker_name": "Clutch Batter",
            "ball_faced": 1, "batter_runs": 1 if i % 2 == 0 else 2,
            "is_wicket": False, "dismissed_player_id": np.nan,
            "is_four": False, "is_six": False, "is_dot": False,
            "expected_batting_runs": 1.3, "batting_impact": 0.0,
            "pressure_category": "normal"
        })
        
    # Batter 2: Pressure Choker (Great normally, collapses under pressure)
    # 40 balls under pressure: 30 runs (SR = 75)
    # 100 balls normal: 180 runs (SR = 180) -> Negative uplift
    for i in range(40):
        records.append({
            "match_id": 1 + (i % 6), "innings": 2, "overid": 19, "over_ball_num": 1,
            "striker_id": 102, "striker_name": "Choker Batter",
            "ball_faced": 1, "batter_runs": 0 if i % 2 == 0 else 1,
            "is_wicket": (i == 39), "dismissed_player_id": 102 if i == 39 else np.nan,
            "is_four": False, "is_six": False, "is_dot": True,
            "expected_batting_runs": 1.4, "batting_impact": -0.65,
            "pressure_category": "high"
        })
    for i in range(100):
        records.append({
            "match_id": 1 + (i % 6), "innings": 2, "overid": 4, "over_ball_num": 1,
            "striker_id": 102, "striker_name": "Choker Batter",
            "ball_faced": 1, "batter_runs": 4 if i % 2 == 0 else 0,
            "is_wicket": False, "dismissed_player_id": np.nan,
            "is_four": (i % 2 == 0), "is_six": False, "is_dot": False,
            "expected_batting_runs": 1.2, "batting_impact": 0.6,
            "pressure_category": "normal"
        })
        
    return pd.DataFrame(records)


def test_pressure_uplift_distinction():
    """Verify that Clutch Batter receives a higher pressure rating than Choker Batter."""
    df = create_mock_batter_df()
    agg = compute_batting_aggregates(df)
    consistency = compute_batting_consistency(df)
    ratings = compute_batting_ratings(agg, consistency)
    
    clutch = ratings[ratings["striker_id"] == 101].iloc[0]
    choker = ratings[ratings["striker_id"] == 102].iloc[0]
    
    assert clutch["pressure_uplift"] > choker["pressure_uplift"], "Clutch batter must have higher uplift"
    assert clutch["batting_pressure_rating"] > choker["batting_pressure_rating"], "Clutch batter must rank higher overall"


def test_batting_eligibility_filter():
    """Verify that players with insufficient pressure sample size are flagged as ineligible."""
    df = create_mock_batter_df()
    # Add an emergent player with only 5 pressure balls
    small_sample_rows = [
        {
            "match_id": 1, "innings": 2, "overid": 20, "over_ball_num": 1,
            "striker_id": 103, "striker_name": "Tiny Sample Batter",
            "ball_faced": 1, "batter_runs": 6, "is_wicket": False, "dismissed_player_id": np.nan,
            "is_four": False, "is_six": True, "is_dot": False,
            "expected_batting_runs": 1.5, "batting_impact": 4.5,
            "pressure_category": "high"
        }
    ] * 5
    
    full_df = pd.concat([df, pd.DataFrame(small_sample_rows)], ignore_index=True)
    agg = compute_batting_aggregates(full_df)
    consistency = compute_batting_consistency(full_df)
    ratings = compute_batting_ratings(agg, consistency)
    
    small = ratings[ratings["striker_id"] == 103].iloc[0]
    assert small["eligible"] == False, "Player with 5 balls must NOT be marked eligible"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

