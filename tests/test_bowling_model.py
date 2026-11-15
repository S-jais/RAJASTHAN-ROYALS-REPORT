"""
test_bowling_model.py — Unit tests for bowling performance, economy uplift, and wicket values.
"""
import pytest
import numpy as np
import pandas as pd
from src.bowling_model import compute_bowling_aggregates, compute_bowling_consistency, compute_bowling_ratings, compute_wicket_value


def create_mock_bowler_df():
    """Create a mock dataset for testing bowling impact."""
    records = []
    
    # Bowler 1: Death Specialist (concedes fewer than expected runs under pressure)
    for i in range(36): # 6 overs under pressure
        records.append({
            "match_id": 1 + (i % 6), "innings": 2, "overid": 19, "over_ball_num": 1 + (i % 6),
            "bowler_id": 201, "bowler_name": "Death Specialist",
            "is_legal": True, "bowler_runs": 0 if i % 2 == 0 else 1,
            "is_wicket": (i % 6 == 0), "is_bowler_wicket": (i % 6 == 0),
            "dismissal_type": "Bowled" if (i % 6 == 0) else np.nan,
            "is_dot": (i % 2 == 0), "is_four": False, "is_six": False,
            "is_wide": False, "is_noball": False,
            "expected_bowling_runs": 1.7, "bowling_impact": 1.2,
            "pressure_category": "high", "wickets_remaining": 4, "balls_remaining": 12, "pressure_index": 0.85
        })
    for i in range(72): # 12 overs normal
        records.append({
            "match_id": 1 + (i % 6), "innings": 2, "overid": 10, "over_ball_num": 1 + (i % 6),
            "bowler_id": 201, "bowler_name": "Death Specialist",
            "is_legal": True, "bowler_runs": 1,
            "is_wicket": False, "is_bowler_wicket": False,
            "dismissal_type": np.nan, "is_dot": False, "is_four": False, "is_six": False,
            "is_wide": False, "is_noball": False,
            "expected_bowling_runs": 1.2, "bowling_impact": 0.2,
            "pressure_category": "normal", "wickets_remaining": 7, "balls_remaining": 60, "pressure_index": 0.2
        })
        
    # Bowler 2: Expensive Bowler
    for i in range(36):
        records.append({
            "match_id": 1 + (i % 6), "innings": 2, "overid": 20, "over_ball_num": 1 + (i % 6),
            "bowler_id": 202, "bowler_name": "Expensive Bowler",
            "is_legal": True, "bowler_runs": 3,
            "is_wicket": False, "is_bowler_wicket": False,
            "dismissal_type": np.nan, "is_dot": False, "is_four": True, "is_six": False,
            "is_wide": False, "is_noball": False,
            "expected_bowling_runs": 1.7, "bowling_impact": -1.3,
            "pressure_category": "high", "wickets_remaining": 6, "balls_remaining": 6, "pressure_index": 0.85
        })
    for i in range(72):
        records.append({
            "match_id": 1 + (i % 6), "innings": 2, "overid": 8, "over_ball_num": 1 + (i % 6),
            "bowler_id": 202, "bowler_name": "Expensive Bowler",
            "is_legal": True, "bowler_runs": 1,
            "is_wicket": False, "is_bowler_wicket": False,
            "dismissal_type": np.nan, "is_dot": False, "is_four": False, "is_six": False,
            "is_wide": False, "is_noball": False,
            "expected_bowling_runs": 1.2, "bowling_impact": 0.2,
            "pressure_category": "normal", "wickets_remaining": 8, "balls_remaining": 72, "pressure_index": 0.2
        })
        
    return pd.DataFrame(records)


def test_bowling_economy_and_impact():
    """Verify that Death Specialist outperforms Expensive Bowler in economy and impact under pressure."""
    df = create_mock_bowler_df()
    agg = compute_bowling_aggregates(df)
    consistency = compute_bowling_consistency(df)
    wv = compute_wicket_value(df)
    ratings = compute_bowling_ratings(agg, consistency, wv)
    
    specialist = ratings[ratings["bowler_id"] == 201].iloc[0]
    expensive = ratings[ratings["bowler_id"] == 202].iloc[0]
    
    assert specialist["economy_pressure"] < expensive["economy_pressure"]
    assert specialist["impact_per_ball_pressure"] > expensive["impact_per_ball_pressure"]
    assert specialist["bowling_pressure_rating"] > expensive["bowling_pressure_rating"]


def test_bowling_legal_ball_counting():
    """Ensure wides/no-balls are excluded from legal ball counts in economy calculations."""
    records = [
        # Over with 6 legal balls + 2 wides
        {"bowler_id": 301, "is_legal": True, "bowler_runs": 1, "is_bowler_wicket": False, "is_wicket": False,
         "is_dot": False, "is_four": False, "is_six": False, "is_wide": False, "is_noball": False,
         "match_id": 1, "pressure_category": "high", "expected_bowling_runs": 1.2, "bowling_impact": 0.2}
    ] * 6 + [
        {"bowler_id": 301, "is_legal": False, "bowler_runs": 1, "is_bowler_wicket": False, "is_wicket": False,
         "is_dot": False, "is_four": False, "is_six": False, "is_wide": True, "is_noball": False,
         "match_id": 1, "pressure_category": "high", "expected_bowling_runs": 1.2, "bowling_impact": 0.2}
    ] * 2
    
    df = pd.DataFrame(records)
    agg = compute_bowling_aggregates(df)
    row = agg[agg["pressure_category"] == "high"].iloc[0]
    
    assert row["total_deliveries"] == 8, "Total deliveries should be 8"
    assert row["legal_balls"] == 6, "Legal balls must be exactly 6"
    assert row["bowler_runs_conceded"] == 8, "Bowler conceded 6 + 2 = 8 runs"
    # Economy is 8 runs in 1 over (6 legal balls) = 8.00 RPO
    assert row["economy"] == 8.0, "Economy rate must be calculated per 6 legal balls"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

