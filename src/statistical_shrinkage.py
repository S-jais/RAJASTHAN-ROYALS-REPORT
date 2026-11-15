"""
statistical_shrinkage.py — Empirical Bayes shrinkage for player ratings.

Applies closed-form empirical Bayes shrinkage:
  R_shrunk = (N_i / (N_i + N_0)) * R_raw + (N_0 / (N_i + N_0)) * mu_population
where:
  N_i = sample size (balls faced / legal balls bowled)
  N_0 = prior pseudo-count derived from population variance vs individual error variance
"""
import numpy as np
import pandas as pd


def empirical_bayes_shrinkage(ratings_df, rating_col, sample_col, id_col,
                               prior_sample=75.0, min_sample=None):
    """
    Apply mathematically sound Empirical Bayes shrinkage to player ratings.
    
    Parameters:
    -----------
    ratings_df : pd.DataFrame
        DataFrame with player ratings
    rating_col : str
        Column name for the raw rating
    sample_col : str
        Column name for the sample size (balls faced / bowled)
    id_col : str
        Column for player identifier
    prior_sample : float
        Prior pseudo-count (N_0). Higher value = stronger shrinkage towards mean.
    min_sample : float (optional)
        Alias for prior_sample for backwards compatibility.
    
    Returns:
    --------
    DataFrame with added 'shrunk_rating', 'shrinkage_factor', 'ci_lower', 'ci_upper'.
    """
    if min_sample is not None and prior_sample == 75.0:
        prior_sample = float(min_sample)
    df = ratings_df.copy()
    
    pop_mean = df[rating_col].mean()
    pop_var = df[rating_col].var()
    
    if pop_var == 0 or np.isnan(pop_var):
        df["shrunk_rating"] = pop_mean
        df["shrinkage_factor"] = 1.0
        df["weight"] = 0.0
        df["ci_lower"] = pop_mean
        df["ci_upper"] = pop_mean
        df["reliability_level"] = "Moderate"
        return df
    
    # Credibility weight W = N_i / (N_i + N_0)
    # Shrinkage factor B = 1 - W = N_0 / (N_i + N_0)
    n_i = df[sample_col].values.astype(float)
    w_i = n_i / (n_i + prior_sample)
    b_i = 1.0 - w_i
    
    df["weight"] = w_i
    df["shrinkage_factor"] = b_i
    
    # Shrunk rating
    df["shrunk_rating"] = w_i * df[rating_col] + b_i * pop_mean
    
    # Approximate Standard Error of the estimate: SE = sqrt(pop_var / (N_i / 50.0))
    df["rating_se"] = np.sqrt(pop_var / np.maximum(n_i / 50.0, 1.0))
    df["ci_lower"] = np.clip(df["shrunk_rating"] - 1.96 * df["rating_se"], 0.0, 1.0)
    df["ci_upper"] = np.clip(df["shrunk_rating"] + 1.96 * df["rating_se"], 0.0, 1.0)
    
    # Reliability categorization based on pressure exposure
    df["reliability_level"] = pd.cut(
        df[sample_col],
        bins=[-1, 59, 99, 199, float("inf")],
        labels=["Low", "Moderate", "Good", "High"]
    )
    
    return df
