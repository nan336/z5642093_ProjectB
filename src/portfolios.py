"""Station 3 - your funds: optimal portfolios + out-of-sample backtest.

Build at least a combined equity-plus-crypto fund with two optimisation methods.
Backtest rules: walk-forward, no look-ahead, weights from past data only, annualise
with 252 (equity) or 365 (crypto). See the brief, Part B.
"""
import pandas as pd


def compute_weights(available_returns: pd.DataFrame, available_tickers, method: str) -> pd.Series:
    """Compute portfolio weights for a given method, using only past data.

    available_returns: historical returns up to (not including) the rebalance date,
                        for the tickers with data available at that point.
    """
    if method == "equal_weight":
        n_assets = len(available_tickers)
        weights = pd.Series(1 / n_assets, index=available_tickers)

    elif method == "min_variance":
        import numpy as np
        from scipy.optimize import minimize

        history = available_returns.dropna(axis=0, how="any")
        cov_matrix = history.cov().values
        n = cov_matrix.shape[0]

        def portfolio_variance(weights, cov_matrix):
            return weights @ cov_matrix @ weights

        constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1})
        bounds = [(0, 1) for _ in range(n)]
        init_guess = np.ones(n) / n

        opt_result = minimize(portfolio_variance, init_guess, args=(cov_matrix,),
                               method="SLSQP", bounds=bounds, constraints=constraints)
        weights = pd.Series(opt_result.x, index=history.columns)

    else:
        raise ValueError(f"Unknown method: {method}")
    return weights


def oos_backtest(wide_returns: pd.DataFrame, method: str = "equal_weight",
                  initial_window_days: int = 126) -> dict:
    """Walk-forward out-of-sample backtest with monthly rebalancing.

    No look-ahead: weights at each rebalance date are computed only from data
    up to (not including) that date, then held until the next rebalance date.
    """
    wide_returns = wide_returns.copy()
    wide_returns.index = pd.to_datetime(wide_returns.index)

    # monthly rebalance calendar, snapped to actual trading days
    month_starts = wide_returns.resample("MS").first().index
    rebalance_dates = [wide_returns.index[wide_returns.index >= d][0] for d in month_starts]

    # only rebalance dates after the initial estimation window
    live_rebalance_dates = [
        d for d in rebalance_dates
        if wide_returns.index.get_loc(d) >= initial_window_days
    ]

    portfolio_returns = []
    weights_over_time = {}

    for i, reb_date in enumerate(live_rebalance_dates):
        if i + 1 < len(live_rebalance_dates):
            next_reb_date = live_rebalance_dates[i + 1]
        else:
            next_reb_date = wide_returns.index[-1]

        period_mask = (wide_returns.index > reb_date) & (wide_returns.index <= next_reb_date)
        period_returns = wide_returns.loc[period_mask]

        available_tickers = wide_returns.loc[reb_date].dropna().index
        history = wide_returns.loc[:reb_date, available_tickers].iloc[:-1]

        weights = compute_weights(history, available_tickers, method)
        weights_over_time[reb_date] = weights

        daily_port_ret = (period_returns[available_tickers] * weights).sum(axis=1)
        portfolio_returns.append(daily_port_ret)

    portfolio_returns = pd.concat(portfolio_returns)
    weights_df = pd.DataFrame(weights_over_time).T

    return {
        "returns": portfolio_returns,
        "weights": weights_df,
        "first_live_date": live_rebalance_dates[0],
        "n_rebalances": len(live_rebalance_dates),
    }
def performance_metrics(daily_returns: pd.Series, periods_per_year: int = 252,
                         risk_free_rate: float = 0.0) -> dict:
    """Annualised return, annualised volatility, Sharpe, and max drawdown."""
    ann_return = (1 + daily_returns.mean()) ** periods_per_year - 1
    ann_vol = daily_returns.std() * (periods_per_year ** 0.5)
    sharpe = (ann_return - risk_free_rate) / ann_vol

    growth = (1 + daily_returns).cumprod()
    running_max = growth.cummax()
    drawdown = (growth - running_max) / running_max
    max_drawdown = drawdown.min()

    return {
        "annualised_return": ann_return,
        "annualised_volatility": ann_vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
    }

def oos_backtest_with_sentiment(wide_returns: pd.DataFrame, sentiment_lagged: pd.DataFrame,
                                  base_method: str = "equal_weight", tilt_strength: float = 0.5,
                                  initial_window_days: int = 126) -> dict:
    """Same as oos_backtest, but applies a sentiment tilt to the base weights
    at each rebalance date, using fusion.apply_sentiment (look-ahead safe)."""
    from src import fusion

    wide_returns = wide_returns.copy()
    wide_returns.index = pd.to_datetime(wide_returns.index)

    month_starts = wide_returns.resample("MS").first().index
    rebalance_dates = [wide_returns.index[wide_returns.index >= d][0] for d in month_starts]
    live_rebalance_dates = [d for d in rebalance_dates if wide_returns.index.get_loc(d) >= initial_window_days]

    portfolio_returns = []
    weights_over_time = {}

    for i, reb_date in enumerate(live_rebalance_dates):
        next_reb_date = live_rebalance_dates[i + 1] if i + 1 < len(live_rebalance_dates) else wide_returns.index[-1]
        period_mask = (wide_returns.index > reb_date) & (wide_returns.index <= next_reb_date)
        period_returns = wide_returns.loc[period_mask]

        available_tickers = wide_returns.loc[reb_date].dropna().index
        history = wide_returns.loc[:reb_date, available_tickers].iloc[:-1]

        base_weights = compute_weights(history, available_tickers, base_method)
        sentiment_asof = sentiment_lagged.loc[:reb_date].iloc[-1]
        tilted_weights = fusion.apply_sentiment(base_weights, sentiment_asof, tilt_strength)

        weights_over_time[reb_date] = tilted_weights
        daily_port_ret = (period_returns[available_tickers] * tilted_weights).sum(axis=1)
        portfolio_returns.append(daily_port_ret)

    portfolio_returns = pd.concat(portfolio_returns)
    weights_df = pd.DataFrame(weights_over_time).T

    return {
        "returns": portfolio_returns,
        "weights": weights_df,
        "first_live_date": live_rebalance_dates[0],
        "n_rebalances": len(live_rebalance_dates),
    }
