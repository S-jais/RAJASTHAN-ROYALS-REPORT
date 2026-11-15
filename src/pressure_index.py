"""
pressure_index.py — Calculate the ball-level Pressure Index (0-1).

The Pressure Index is a composite score measuring the difficulty of the match
situation at the point of each delivery. It is designed to work for both
first-innings and second-innings contexts.

Components:
  1. Chase Urgency (2nd innings only): Based on required run rate vs historical norms
  2. Resource Pressure: Based on wickets lost relative to balls remaining
  3. Innings Phase Pressure: Based on over number and phase context
  4. Match Competitiveness (2nd innings only): Based on win probability estimates
"""
import numpy as np
import pandas as pd


def compute_chase_urgency(df):
    """
    Chase urgency for second-innings deliveries.
    
    Uses required run rate compared to historical scoring benchmarks.
    A required RR of 6.0 in T20s is average; 10+ is very high pressure.
    
    Normalized using a logistic function centred around the historical
    average scoring rate.
    """
    chase = df["is_chase"].values
    rrr = df["required_rr"].values
    balls_rem = df["balls_remaining"].values
    wickets_rem = df["wickets_remaining"].values
    
    urgency = np.zeros(len(df))
    
    mask = chase & (balls_rem > 0)
    
    # Logistic function: as RRR increases beyond average (~8 RPO), pressure rises
    # At RRR=8, urgency ~ 0.5; at RRR=12, urgency ~ 0.88; at RRR=15+, urgency ~ 0.95+
    rrr_component = 1.0 / (1.0 + np.exp(-0.5 * (rrr[mask] - 9.0)))
    
    # Wicket-adjusted urgency: fewer wickets with high RRR = more pressure
    wicket_factor = 1.0 - (wickets_rem[mask] - 1) / 9.0  # 0 when 10 wkts, 1 when 1 wkt
    wicket_factor = np.clip(wicket_factor, 0, 1)
    
    # Balls remaining factor: fewer balls = more pressure (when chasing)
    balls_factor = 1.0 - balls_rem[mask] / 120.0
    balls_factor = np.clip(balls_factor, 0, 1)
    
    # Combined chase urgency (weighted)
    urgency[mask] = (
        0.50 * rrr_component + 
        0.30 * wicket_factor + 
        0.20 * balls_factor
    )
    
    urgency = np.clip(urgency, 0, 1)
    return urgency


def compute_resource_pressure(df):
    """
    Resource pressure based on wickets fallen relative to innings stage.
    
    A team that has lost 5 wickets by over 10 is under more resource pressure
    than a team that has lost 2 wickets by over 10.
    
    Uses a modified Duckworth-Lewis-style resource concept.
    """
    wickets_lost = 10 - df["wickets_remaining"].values
    balls_rem = df["balls_remaining"].values.astype(float)
    total_balls = df["total_innings_balls"].values.astype(float)
    
    # Resource remaining estimate (simplified DLS-inspired)
    # Proportion of balls remaining
    balls_frac = np.clip(balls_rem / np.maximum(total_balls, 1), 0, 1)
    
    # Wicket depletion factor
    # More wickets lost = higher pressure, especially with fewer balls remaining
    wicket_depletion = wickets_lost / 10.0
    
    # Resource pressure: high when wickets lost is high relative to progress
    # If you've lost many wickets early, resource pressure is high
    expected_wickets = (1 - balls_frac) * 10.0 * 0.5  # Expect ~5 wickets in full innings
    wicket_excess = np.maximum(wickets_lost - expected_wickets, 0) / 10.0
    
    # Combine: direct wicket depletion + excess wicket loss
    resource_pressure = 0.6 * wicket_depletion + 0.4 * wicket_excess
    
    # Extra pressure when very few wickets remain (tail-ender effect)
    tail_mask = df["wickets_remaining"].values <= 3
    resource_pressure[tail_mask] = np.maximum(
        resource_pressure[tail_mask], 
        0.6 + 0.13 * (3 - df["wickets_remaining"].values[tail_mask])
    )
    
    return np.clip(resource_pressure, 0, 1)


def compute_phase_pressure(df):
    """
    Innings phase pressure.
    
    Death overs inherently have higher pressure due to the acceleration
    requirements and the finality of the innings.
    Powerplay has moderate pressure due to fielding restrictions.
    Middle overs are baseline.
    """
    phase = df["innings_phase"].values
    over_0idx = df["over_0idx"].values
    
    phase_pressure = np.zeros(len(df))
    
    # Powerplay (overs 1-6): moderate pressure due to fielding restrictions
    pp_mask = phase == "powerplay"
    # Slight increase through the powerplay
    phase_pressure[pp_mask] = 0.25 + 0.05 * (over_0idx[pp_mask] / 5.0)
    
    # Middle overs (7-15): baseline, gradually increasing
    mid_mask = phase == "middle"
    phase_pressure[mid_mask] = 0.15 + 0.15 * ((over_0idx[mid_mask] - 6) / 8.0)
    
    # Death overs (16-20): high pressure, increasing sharply
    death_mask = phase == "death"
    phase_pressure[death_mask] = 0.50 + 0.40 * ((over_0idx[death_mask] - 15) / 4.0)
    
    return np.clip(phase_pressure, 0, 1)


def compute_match_competitiveness(df):
    """
    Match competitiveness and leverage for second-innings deliveries.
    
    Combines:
    - Closeness: High when win probability is near 50-50 (Bernoulli variance 4*P*(1-P))
    - Crisis leverage: As required run rate increases, urgency ensures pressure does not
      drop even if win probability tilts towards the bowling side.
    """
    chase = df["is_chase"].values
    runs_req = df["runs_required"].values
    balls_rem = df["balls_remaining"].values
    wickets_rem = df["wickets_remaining"].values
    
    competitiveness = np.zeros(len(df))
    mask = chase & (balls_rem > 0)
    
    if not np.any(mask):
        return competitiveness
        
    rrr = np.where(balls_rem[mask] > 0, runs_req[mask] * 6.0 / balls_rem[mask], 99.0)
    resource = np.maximum(wickets_rem[mask] / 10.0, 0.1)
    
    difficulty = rrr / (8.0 * resource)
    win_prob = 1.0 / (1.0 + np.exp(1.5 * (difficulty - 1.0)))
    
    # Bernoulli variance peaks at 0.5 where it equals 1.0
    closeness = 4.0 * win_prob * (1.0 - win_prob)
    
    # Crisis leverage: ensures high RRR tension never deflates pressure
    crisis_floor = 1.0 / (1.0 + np.exp(-0.4 * (rrr - 10.0)))
    
    competitiveness[mask] = np.maximum(closeness, crisis_floor)
    return np.clip(competitiveness, 0, 1)


def compute_first_innings_pressure(df):
    """
    First-innings specific pressure.
    
    Combines:
    - Resource pressure (wickets vs stage)
    - Phase pressure (death overs are harder)
    - Par score pressure (am I behind/ahead of typical scoring)
    """
    first_inn = ~df["is_chase"].values
    cum_runs = df["cum_runs_before"].values
    balls_bowled = df["cum_legal_balls_before"].values
    
    # Estimate par score at current stage using historical T20 average (~150 in 120 balls)
    par_rate = 150.0 / 120.0  # ~1.25 runs per ball
    expected_runs = balls_bowled * par_rate
    
    # Par pressure: below par = more pressure to accelerate
    par_diff = np.where(
        first_inn & (balls_bowled > 6),  # Only after a few balls
        (expected_runs - cum_runs) / np.maximum(expected_runs, 1),
        0
    )
    par_pressure = np.clip(par_diff * 0.5 + 0.25, 0, 1)
    par_pressure[~first_inn] = 0
    
    return par_pressure


def calculate_pressure_index(df, config=None):
    """
    Calculate the final Pressure Index for every delivery.
    
    Returns the DataFrame with added pressure columns.
    """
    if config is None:
        config = {
            "first_innings": {
                "resource_weight": 0.45,
                "phase_weight": 0.35,
                "par_score_weight": 0.20,
            },
            "second_innings": {
                "chase_urgency_weight": 0.45,
                "resource_weight": 0.25,
                "phase_weight": 0.15,
                "match_competitiveness_weight": 0.15,
            },
        }
    
    # Compute individual components
    df = df.copy()
    df["pi_chase_urgency"] = compute_chase_urgency(df)
    df["pi_resource"] = compute_resource_pressure(df)
    df["pi_phase"] = compute_phase_pressure(df)
    df["pi_competitiveness"] = compute_match_competitiveness(df)
    df["pi_first_inn_par"] = compute_first_innings_pressure(df)
    
    # Combine for first innings
    fi = config["first_innings"]
    first_pi = (
        fi["resource_weight"] * df["pi_resource"] +
        fi["phase_weight"] * df["pi_phase"] +
        fi["par_score_weight"] * df["pi_first_inn_par"]
    )
    
    # Combine for second innings
    si = config["second_innings"]
    second_pi = (
        si["chase_urgency_weight"] * df["pi_chase_urgency"] +
        si["resource_weight"] * df["pi_resource"] +
        si["phase_weight"] * df["pi_phase"] +
        si["match_competitiveness_weight"] * df["pi_competitiveness"]
    )
    
    # Select based on innings
    df["pressure_index"] = np.where(df["is_chase"], second_pi, first_pi)
    df["pressure_index"] = np.clip(df["pressure_index"], 0, 1)
    
    return df


def classify_pressure(df, high_pct=75, normal_pct=25):
    """
    Classify deliveries into pressure categories based on percentile thresholds.
    
    Returns DataFrame with 'pressure_category' column.
    """
    high_threshold = np.percentile(df["pressure_index"].dropna(), high_pct)
    normal_threshold = np.percentile(df["pressure_index"].dropna(), normal_pct)
    
    conditions = [
        df["pressure_index"] >= high_threshold,
        df["pressure_index"] <= normal_threshold,
    ]
    choices = ["high", "normal"]
    df["pressure_category"] = np.select(conditions, choices, default="intermediate")
    
    df["high_pressure_threshold"] = high_threshold
    df["normal_pressure_threshold"] = normal_threshold
    
    return df, high_threshold, normal_threshold

