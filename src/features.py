"""Station 2 - your features: return features and headline text assembly.

Build your return (and optional risk) features here, and assemble the headlines
into a daily text panel. Part A is assembly only - scoring the text into sentiment
(and lagging the signal) is the Station 3 model, built in Part B, not here.
"""
import pandas as pd


def daily_returns(prices: pd.DataFrame, price_col: str = "adjClose") -> pd.DataFrame:
    """Simple daily returns per ticker. Use adjClose."""
    df = prices.copy()
    df = df.sort_values(["ticker", "date"])
    df["return"] = df.groupby("ticker")[price_col].pct_change()
    return df[["ticker", "date", "return"]]


def assemble_headline_panel(headlines: pd.DataFrame, trading_dates) -> pd.DataFrame:
    """Assemble the headlines into a daily panel per ticker and sector.
    ...
    """
    trading_calendar = pd.DataFrame({
        "trading_date": pd.to_datetime(sorted(set(trading_dates))).astype("datetime64[ns]")
    })

    df = headlines.sort_values("date").copy()
    df["date"] = df["date"].astype("datetime64[ns]")

    aligned = pd.merge_asof(
        df, trading_calendar,
        left_on="date", right_on="trading_date",
        direction="forward"
    )

    # drop headlines with no valid next trading day (after the sample's last trading day)
    n_dropped = aligned["trading_date"].isna().sum()
    aligned = aligned.dropna(subset=["trading_date"])

    # aggregate to one row per (trading_date, ticker, sector)
    panel = (
        aligned.groupby(["trading_date", "ticker", "sector"])
        .agg(
            headline_count=("title", "count"),
            headlines=("title", lambda x: " || ".join(x)),
        )
        .reset_index()
    )
    return panel
