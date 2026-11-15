"""
test_data_validation.py — Unit tests for data validation, cricket rules, extras and wickets.
"""
import pytest
import pandas as pd
import numpy as np
from src.data_loader import prepare_ball_by_ball, compute_innings_state


def create_mock_delivery_df():
    """Create a mock ball-by-ball dataframe with known test cases."""
    rows = [
        # Normal dot ball
        {
            "match_id": 1, "innings": 1, "overid": 1, "over_ball_num": 1, "innings_ball_num": 1,
            "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 101, "striker_name": "Batter A",
            "non_striker_id": 102, "non_striker_name": "Batter B", "bowler_id": 201, "bowler_name": "Bowler X",
            "runs": 0, "is_four": False, "is_six": False, "is_wicket": False,
            "dismissal_type_id": np.nan, "dismissal_type": np.nan, "dismissed_player_id": np.nan,
            "extras_type": np.nan, "extras1_runs": 6, "extras_2_runs": 0,
        },
        # Normal 4
        {
            "match_id": 1, "innings": 1, "overid": 1, "over_ball_num": 2, "innings_ball_num": 2,
            "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 101, "striker_name": "Batter A",
            "non_striker_id": 102, "non_striker_name": "Batter B", "bowler_id": 201, "bowler_name": "Bowler X",
            "runs": 4, "is_four": True, "is_six": False, "is_wicket": False,
            "dismissal_type_id": np.nan, "dismissal_type": np.nan, "dismissed_player_id": np.nan,
            "extras_type": np.nan, "extras1_runs": 6, "extras_2_runs": 0,
        },
        # Wide delivery (extras_type='wide', extras1_runs=2, extras_2_runs=0)
        {
            "match_id": 1, "innings": 1, "overid": 1, "over_ball_num": 3, "innings_ball_num": 3,
            "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 101, "striker_name": "Batter A",
            "non_striker_id": 102, "non_striker_name": "Batter B", "bowler_id": 201, "bowler_name": "Bowler X",
            "runs": 0, "is_four": False, "is_six": False, "is_wicket": False,
            "dismissal_type_id": np.nan, "dismissal_type": np.nan, "dismissed_player_id": np.nan,
            "extras_type": "wide", "extras1_runs": 2, "extras_2_runs": 0,
        },
        # No-ball delivery (extras_type='Overstep', extras1_runs=1, extras_2_runs=0, batter ran 2)
        {
            "match_id": 1, "innings": 1, "overid": 1, "over_ball_num": 4, "innings_ball_num": 4,
            "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 101, "striker_name": "Batter A",
            "non_striker_id": 102, "non_striker_name": "Batter B", "bowler_id": 201, "bowler_name": "Bowler X",
            "runs": 2, "is_four": False, "is_six": False, "is_wicket": False,
            "dismissal_type_id": np.nan, "dismissal_type": np.nan, "dismissed_player_id": np.nan,
            "extras_type": "Overstep", "extras1_runs": 1, "extras_2_runs": 0,
        },
        # Leg-bye delivery (extras_type='legbyes', extras1_runs=3, extras_2_runs=1)
        {
            "match_id": 1, "innings": 1, "overid": 1, "over_ball_num": 5, "innings_ball_num": 5,
            "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 101, "striker_name": "Batter A",
            "non_striker_id": 102, "non_striker_name": "Batter B", "bowler_id": 201, "bowler_name": "Bowler X",
            "runs": 0, "is_four": False, "is_six": False, "is_wicket": False,
            "dismissal_type_id": np.nan, "dismissal_type": np.nan, "dismissed_player_id": np.nan,
            "extras_type": "legbyes", "extras1_runs": 3, "extras_2_runs": 1,
        },
        # Bowler-credited dismissal: Bowled
        {
            "match_id": 1, "innings": 1, "overid": 2, "over_ball_num": 1, "innings_ball_num": 6,
            "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 101, "striker_name": "Batter A",
            "non_striker_id": 102, "non_striker_name": "Batter B", "bowler_id": 201, "bowler_name": "Bowler X",
            "runs": 0, "is_four": False, "is_six": False, "is_wicket": True,
            "dismissal_type_id": 1.0, "dismissal_type": "Bowled", "dismissed_player_id": 101,
            "extras_type": np.nan, "extras1_runs": 6, "extras_2_runs": 0,
        },
        # Non-bowler dismissal: Run-out of non-striker
        {
            "match_id": 1, "innings": 1, "overid": 2, "over_ball_num": 2, "innings_ball_num": 7,
            "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 103, "striker_name": "Batter C",
            "non_striker_id": 102, "non_striker_name": "Batter B", "bowler_id": 201, "bowler_name": "Bowler X",
            "runs": 1, "is_four": False, "is_six": False, "is_wicket": True,
            "dismissal_type_id": 4.0, "dismissal_type": "RunOut", "dismissed_player_id": 102,
            "extras_type": np.nan, "extras1_runs": 6, "extras_2_runs": 0,
        },
    ]
    return pd.DataFrame(rows)


def create_mock_matches_df():
    return pd.DataFrame([{
        "match_id": 1, "comp_id": 100, "match_number": 1, "match_date": "2024-04-01",
        "stage": "League", "venue_id": 1, "venue_country": "India",
        "home_team_id": 10, "home_team": "Team A", "away_team_id": 20, "away_team": "Team B",
        "home_team_captain_id": 101, "away_team_captain_id": 201, "toss_win_team_id": 10,
        "toss_opted": "Batting", "man_of_the_match": 101,
        "first_inn_revised_overs": np.nan, "second_inn_revised_overs": np.nan, "revised_target": np.nan,
        "knock_out": 0, "win_team_id": 10, "result": "Team A Won by 10 runs"
    }])


def create_mock_comps_df():
    return pd.DataFrame([{
        "comp_id": 100, "comp_name": "IPL 2024", "match_format": "T20", "season": "2024"
    }])


def test_wide_ball_conventions():
    """Verify that wides do not count as legal ball or ball faced, but add to team and bowler runs."""
    bbb = create_mock_delivery_df()
    matches = create_mock_matches_df()
    comps = create_mock_comps_df()
    
    df = prepare_ball_by_ball(bbb, matches, comps)
    wide_row = df[df["extras_type"] == "wide"].iloc[0]
    
    assert wide_row["is_legal"] == False, "Wide must NOT be a legal delivery"
    assert wide_row["ball_faced"] == 0, "Wide must NOT count as a ball faced by the batter"
    assert wide_row["batter_runs"] == 0, "Batter receives 0 runs on a wide"
    assert wide_row["bowler_runs"] >= 1, "Wide run MUST be charged to bowler"
    assert wide_row["total_runs"] >= 1, "Wide run MUST be added to total runs"


def test_noball_conventions():
    """Verify that no-balls count as balls faced, not legal ball in over, and are charged to bowler."""
    bbb = create_mock_delivery_df()
    matches = create_mock_matches_df()
    comps = create_mock_comps_df()
    
    df = prepare_ball_by_ball(bbb, matches, comps)
    nb_row = df[df["extras_type"] == "Overstep"].iloc[0]
    
    assert nb_row["is_legal"] == False, "No-ball must NOT count as a legal delivery in over"
    assert nb_row["ball_faced"] == 1, "No-ball counts as ball faced by batter"
    assert nb_row["batter_runs"] == 2, "Batter runs on no-ball must be credited"
    assert nb_row["bowler_runs"] == 3, "Bowler charged with 1 NB penalty + 2 batter runs"


def test_legbyes_conventions():
    """Verify that leg-byes are legal deliveries, count as balls faced, but are NOT charged to bowler."""
    bbb = create_mock_delivery_df()
    matches = create_mock_matches_df()
    comps = create_mock_comps_df()
    
    df = prepare_ball_by_ball(bbb, matches, comps)
    lb_row = df[df["extras_type"] == "legbyes"].iloc[0]
    
    assert lb_row["is_legal"] == True, "Leg-bye delivery is a legal ball"
    assert lb_row["ball_faced"] == 1, "Batter faced the delivery"
    assert lb_row["batter_runs"] == 0, "Leg-byes are not batter runs"
    assert lb_row["bowler_runs"] == 0, "Leg-byes are NOT charged to bowler"
    assert lb_row["total_runs"] == 1, "Leg-bye counts towards team total"


def test_wicket_attribution():
    """Verify distinction between bowler-credited wickets (Bowled) and non-bowler wickets (RunOut)."""
    bbb = create_mock_delivery_df()
    matches = create_mock_matches_df()
    comps = create_mock_comps_df()
    
    df = prepare_ball_by_ball(bbb, matches, comps)
    
    # Bowled dismissal
    bowled = df[df["dismissal_type"] == "Bowled"].iloc[0]
    assert bowled["is_bowler_wicket"] == True, "Bowled dismissal must be credited to bowler"
    assert bowled["dismissed_player_id"] == bowled["striker_id"]
    
    # Run out of non-striker
    runout = df[df["dismissal_type"] == "RunOut"].iloc[0]
    assert runout["is_bowler_wicket"] == False, "Run-out must NOT be credited as bowler wicket"
    assert runout["dismissed_player_id"] == 102, "Non-striker must be correctly identified as dismissed"
    assert runout["striker_id"] == 103, "Striker was NOT dismissed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

