"""Station 3 - your sentiment model and index from news headlines.

This is the model step: score each headline, aggregate to a daily per-ticker score,
then to an equal-weight sector index. Headlines are a noisy proxy, so lag to avoid
look-ahead.
"""
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer


def score_headlines(panel: pd.DataFrame, trading_dates) -> pd.DataFrame:
    """Apply VADER to the assembled headline panel, then lag by one trading day.

    Gaps (ticker-days with no headlines) are forward-filled before lagging, so
    the lag always means "the previous trading day's most recent sentiment",
    not just "the previous row of available data".
    """
    sia = SentimentIntensityAnalyzer()

    panel = panel.copy()
    panel["sentiment_compound"] = panel["headlines"].apply(
        lambda text: sia.polarity_scores(text)["compound"]
    )

    sentiment_wide = panel.pivot(index="trading_date", columns="ticker", values="sentiment_compound")
    sentiment_wide.index = pd.to_datetime(sentiment_wide.index)

    full_calendar = pd.to_datetime(sorted(set(trading_dates)))
    sentiment_wide = sentiment_wide.reindex(full_calendar)

    sentiment_filled = sentiment_wide.ffill()
    sentiment_lagged = sentiment_filled.shift(1)

    return sentiment_lagged


def sector_sentiment_index(sentiment_lagged: pd.DataFrame, ticker_sector: pd.Series) -> pd.DataFrame:
    """Build a daily sentiment index per sector (equal-weight across tickers)."""
    sentiment_long = sentiment_lagged.reset_index().melt(
        id_vars="index", var_name="ticker", value_name="sentiment_lagged"
    )
    sentiment_long = sentiment_long.rename(columns={"index": "date"})
    sentiment_long["sector"] = sentiment_long["ticker"].map(ticker_sector)

    index_df = (
        sentiment_long.groupby(["date", "sector"])["sentiment_lagged"]
        .mean()
        .reset_index()
    )
    return index_df
