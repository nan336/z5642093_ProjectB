"""Station 1 - your ETL: load and clean the data.

Load raw data through src.data_access (see context/DATA_GUIDE.md). Add your own
integrity checks. Do not commit data files.
"""
import pandas as pd
from src import data_access


def load_clean_equities():
    """Load equity prices and run Station 1 integrity checks."""
    df = data_access.load_equity_prices().copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

    # duplicate check
    n_dupes = df.duplicated(subset=["ticker", "date"], keep="first").sum()
    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")

    # missing-date audit
    all_dates = df["date"].unique()
    counts = df.groupby("ticker")["date"].nunique()
    missing = len(all_dates) - counts
    missing_tickers = missing[missing > 0]

    # outlier screen (flag only, don't drop)
    df["ret"] = df.groupby("ticker")["adjClose"].pct_change()
    outliers = df[df["ret"].abs() > 0.20]
    df = df.drop(columns=["ret"])

    # price/volume internal consistency checks
    bad_high_low = df[df["high"] < df["low"]]
    bad_price = df[df["adjClose"] <= 0]
    bad_volume = df[df["volume"] < 0]

    report = {
        "n_rows": len(df),
        "n_duplicates_dropped": int(n_dupes),
        "n_tickers_missing_dates": len(missing_tickers),
        "n_outliers": len(outliers),
        "outliers": outliers,
        "n_bad_high_low": len(bad_high_low),
        "n_bad_price": len(bad_price),
        "n_bad_volume": len(bad_volume),
    }
    return df, report


def load_clean_crypto():
    """Load crypto prices (365-day calendar) and run Station 1 integrity checks."""
    df = data_access.load_crypto_prices().copy()
    df["date"] = pd.to_datetime(df["date"])

    # cap the stray 2024-01-01 rows
    df = df[df["date"] <= "2023-12-31"]

    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

    # duplicate check
    n_dupes = df.duplicated(subset=["ticker", "date"], keep="first").sum()
    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")

    # missing-date audit
    all_dates = df["date"].unique()
    counts = df.groupby("ticker")["date"].nunique()
    missing = len(all_dates) - counts
    missing_tickers = missing[missing > 0]

    # outlier screen (flag only, don't drop)
    df["ret"] = df.groupby("ticker")["adjClose"].pct_change()
    outliers = df[df["ret"].abs() > 0.20]
    df = df.drop(columns=["ret"])

    # price/volume internal consistency checks
    bad_high_low = df[df["high"] < df["low"]]
    bad_price = df[df["adjClose"] <= 0]
    bad_volume = df[df["volume"] < 0]

    report = {
        "n_rows": len(df),
        "n_duplicates_dropped": int(n_dupes),
        "n_tickers_missing_dates": len(missing_tickers),
        "n_outliers": len(outliers),
        "outliers": outliers,
        "n_bad_high_low": len(bad_high_low),
        "n_bad_price": len(bad_price),
        "n_bad_volume": len(bad_volume),
    }
    return df, report




def load_clean_news():
    """Load news headlines and run Station 1 integrity checks."""
    df = data_access.load_news_headlines().copy()
    df["date"] = pd.to_datetime(df["date"])

    # duplicate check - ticker+date+title, NOT ticker+date (many headlines/day is normal)
    n_dupes = df.duplicated(subset=["ticker", "date", "title"], keep="first").sum()
    df = df.drop_duplicates(subset=["ticker", "date", "title"], keep="first")

    # normalise tz-aware UTC -> tz-naive day, so it can align with price dates later
    df["date"] = df["date"].dt.tz_convert(None).dt.normalize()

    # blank publisher count (data-quality note, not something to fix in Part A)
    n_blank_publisher = int(df["publisher"].isna().sum() + (df["publisher"] == "").sum())

    report = {
        "n_rows": len(df),
        "n_duplicates_dropped": int(n_dupes),
        "n_blank_publisher": n_blank_publisher,
        "date_min": df["date"].min(),
        "date_max": df["date"].max(),
    }
    return df, report
