"""
test_rankings.py — Unit tests for ranking logic, Empirical Bayes shrinkage, and determinism.
"""
import pytest
import numpy as np
import pandas as pd
from src.statistical_shrinkage import empirical_bayes_shrinkage


def test_shrinkage_behavior():
    """Verify that players with small samples get shrunk more toward the mean than veterans."""
    ratings_df = pd.DataFrame([
        # High raw rating, huge sample (Veteran)
        {"player_id": 1, "raw_rating": 0.90, "pressure_balls": 250},
        # High raw rating, tiny sample (Rookie fluke)
        {"player_id": 2, "raw_rating": 0.90, "pressure_balls": 15},
        # Average player, moderate sample
        {"player_id": 3, "raw_rating": 0.50, "pressure_balls": 80},
        # Low rating, huge sample
        {"player_id": 4, "raw_rating": 0.20, "pressure_balls": 200},
    ])
    
    shrunk = empirical_bayes_shrinkage(
        ratings_df,
        rating_col="raw_rating",
        sample_col="pressure_balls",
        id_col="player_id",
        min_sample=50
    )
    
    vet = shrunk[shrunk["player_id"] == 1].iloc[0]
    rookie = shrunk[shrunk["player_id"] == 2].iloc[0]
    pop_mean = shrunk["raw_rating"].mean()
    
    # Rookie shrinkage factor should be higher than veteran
    assert rookie["shrinkage_factor"] > vet["shrinkage_factor"], "Rookie should have higher shrinkage factor"
    
    # Rookie shrunk rating should be pulled closer to population mean than veteran
    assert abs(rookie["shrunk_rating"] - pop_mean) < abs(vet["shrunk_rating"] - pop_mean), \
        "Rookie rating should be pulled closer to mean than veteran rating"
        
    # Veteran retains higher shrunk rating than rookie despite identical raw rating
    assert vet["shrunk_rating"] > rookie["shrunk_rating"], \
        "Veteran with large sample must outrank rookie with small sample given same raw score"


def test_ranking_determinism():
    """Verify that ranking calculations are deterministic given identical inputs."""
    data = pd.DataFrame([
        {"player_id": 1, "score": 0.82, "balls": 120},
        {"player_id": 2, "score": 0.74, "balls": 95},
        {"player_id": 3, "score": 0.91, "balls": 40},
    ])
    
    r1 = empirical_bayes_shrinkage(data, "score", "balls", "player_id", min_sample=50)
    r2 = empirical_bayes_shrinkage(data, "score", "balls", "player_id", min_sample=50)
    
    pd.testing.assert_frame_equal(r1, r2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

