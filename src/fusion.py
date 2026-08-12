"""Station 3 (extension) - fuse sentiment into the funds.

Tilt or factor: combine your sentiment signal with the portfolio weights,
look-ahead safe, then test whether it adds value. An honest negative result,
explained, is good work.
"""
import pandas as pd


def apply_sentiment(weights: pd.Series, sentiment: pd.Series, tilt_strength: float = 0.5) -> pd.Series:
    """Tilt weights toward high-sentiment names.

    weights: base weights for one rebalance date (must already be look-ahead
             safe - formed only from past return data).
    sentiment: lagged sentiment score for the same date (already shifted by at
               least one trading day, so this is also look-ahead safe). Tickers
               with no sentiment (e.g. crypto) get a neutral tilt factor of 1.
    tilt_strength: how strongly sentiment shifts weight away from the base.
    """
    tilt_factor = 1 + (tilt_strength * sentiment)
    tilt_factor = tilt_factor.reindex(weights.index).fillna(1.0)

    tilted = weights * tilt_factor
    tilted = tilted / tilted.sum()
    return tilted
