"""Reproduce your Part B results. Run from the project root:

    python scripts/run_part_b.py
"""
import sys
import pathlib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src import etl  # noqa: E402
from src import features  # noqa: E402
from src import portfolios  # noqa: E402
from src import sentiment as sentiment_module  # noqa: E402


def main():
    eq, _ = etl.load_clean_equities()
    cr, _ = etl.load_clean_crypto()
    print("equities:", eq.shape, "crypto:", cr.shape)

    eq_returns = features.daily_returns(eq)
    cr_returns = features.daily_returns(cr)

    equity_calendar = pd.DataFrame({"date": pd.to_datetime(sorted(eq["date"].unique()))})
    cr_returns_aligned = equity_calendar.merge(cr_returns, on="date", how="left")
    combined_returns = pd.concat([eq_returns, cr_returns_aligned], ignore_index=True)

    wide_returns = combined_returns.pivot(index="date", columns="ticker", values="return")

    equity_tickers = eq["ticker"].unique()
    crypto_tickers = cr["ticker"].unique()
    wide_returns_equity = wide_returns[equity_tickers]
    wide_returns_crypto = wide_returns[crypto_tickers]

    # --- Station 3: build funds ---
    methods = ["equal_weight", "min_variance"]
    universes = {
        "Combined": wide_returns,
        "Equity-Only": wide_returns_equity,
        "Crypto-Only": wide_returns_crypto,
    }
    fund_returns = {}
    fund_weights = {}
    fund_metrics = {}
    fund_results = {}

    for universe_name, universe_returns in universes.items():
        for method in methods:
            result = portfolios.oos_backtest(universe_returns, method=method)
            metrics = portfolios.performance_metrics(result["returns"])
            fund_name = f"{universe_name} {method.replace('_', ' ').title()}"

            fund_results[fund_name] = result
            fund_returns[fund_name] = result["returns"]
            fund_weights[fund_name] = result["weights"]
            fund_metrics[fund_name] = metrics
            print(f"{fund_name}: {metrics}")

    # --- Save required output files ---
    fund_returns_df = pd.DataFrame(fund_returns)
    fund_returns_df.to_csv("results/data/fund_returns.csv", index_label="date")

    weights_frames = []
    for fund_name, w_df in fund_weights.items():
        w = w_df.copy()
        w["fund"] = fund_name
        weights_frames.append(w)
    fund_weights_df = pd.concat(weights_frames)
    fund_weights_df.to_csv("results/data/fund_weights.csv", index_label="date")

    metrics_df = pd.DataFrame(fund_metrics).T
    metrics_df.to_csv("results/tables/performance_metrics.csv", index_label="fund")

    print("Saved fund_returns.csv, fund_weights.csv, performance_metrics.csv")

# --- Station 3: sentiment ---
    news, _ = etl.load_clean_news()
    trading_days = sorted(eq["date"].unique())
    panel = features.assemble_headline_panel(news, trading_days)

    sentiment_lagged = sentiment_module.score_headlines(panel, trading_days)

    ticker_sector = eq[["ticker", "sector"]].drop_duplicates().set_index("ticker")["sector"]
    sector_index = sentiment_module.sector_sentiment_index(sentiment_lagged, ticker_sector)
    sector_index.to_csv("results/data/sector_sentiment_index.csv", index=False)

    print("Saved sector_sentiment_index.csv")

    # --- Station 3: fusion (before vs after) ---
    result_base = fund_results["Combined Equal Weight"]
    result_tilted = portfolios.oos_backtest_with_sentiment(wide_returns, sentiment_lagged, base_method="equal_weight")

    metrics_base = portfolios.performance_metrics(result_base["returns"])
    metrics_tilted = portfolios.performance_metrics(result_tilted["returns"])

    fusion_comparison = pd.DataFrame({
        "Base (Equal Weight)": metrics_base,
        "Sentiment-Tilted": metrics_tilted,
    }).T
    fusion_comparison.to_csv("results/tables/fusion_comparison.csv")

    print("Saved fusion_comparison.csv")
    print(fusion_comparison)

    # --- Figures ---
    growth_eq = (1 + result_base["returns"]).cumprod()
    growth_mv = (1 + fund_results["Combined Min Variance"]["returns"]).cumprod()
    growth_tilted = (1 + result_tilted["returns"]).cumprod()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(growth_eq.index, growth_eq.values, label="Combined Equal Weight")
    ax.plot(growth_mv.index, growth_mv.values, label="Combined Min Variance")
    ax.plot(growth_tilted.index, growth_tilted.values, label="Sentiment-Tilted Equal Weight", linestyle="--")
    ax.set_title("Growth of $1: Fund Comparison (Aug 2020 - Dec 2023)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value of $1 invested")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/figures/fund_growth_comparison.png", dpi=150)
    plt.close(fig)

    running_max = growth_eq.cummax()
    drawdown_eq = (growth_eq - running_max) / running_max
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(drawdown_eq.index, drawdown_eq.values, 0, color="crimson", alpha=0.4)
    ax.plot(drawdown_eq.index, drawdown_eq.values, color="crimson")
    ax.set_title("Drawdown: Combined Equal Weight Fund (Aug 2020 - Dec 2023)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/figures/drawdown_equal_weight.png", dpi=150)
    plt.close(fig)

    top_holdings = fund_results["Combined Min Variance"]["weights"].mean().sort_values(ascending=False).head(8).index
    fig, ax = plt.subplots(figsize=(12, 6))
    for ticker in top_holdings:
        ax.plot(fund_results["Combined Min Variance"]["weights"].index,
                fund_results["Combined Min Variance"]["weights"][ticker], label=ticker)
    ax.set_title("Portfolio Weights Over Time: Combined Min Variance Fund (Top 8 Average Holdings)")
    ax.set_xlabel("Rebalance Date")
    ax.set_ylabel("Weight")
    ax.legend(loc="upper left", ncol=2, fontsize=8)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/figures/weights_over_time_min_variance.png", dpi=150)
    plt.close(fig)

    all_fund_metrics = dict(fund_metrics)
    all_fund_metrics["Sentiment-Tilted Equal Weight"] = metrics_tilted

    fig, ax = plt.subplots(figsize=(11, 6))
    fund_labels = [name.replace(" ", "\n") for name in all_fund_metrics.keys()]
    sharpe_vals = [m["sharpe_ratio"] for m in all_fund_metrics.values()]
    ax.bar(fund_labels, sharpe_vals, color="steelblue")
    ax.set_title("Sharpe Ratio Across All Funds and Methods (Aug 2020 - Dec 2023)")
    ax.set_ylabel("Sharpe Ratio")
    ax.grid(alpha=0.3, axis="y")
    plt.xticks(rotation=20, ha="right", fontsize=8)
    plt.tight_layout()
    plt.savefig("results/figures/sharpe_by_fund.png", dpi=150)
    plt.close(fig)

    sector_pivot = sector_index.pivot(index="date", columns="sector", values="sentiment_lagged")
    sector_pivot.index = pd.to_datetime(sector_pivot.index)
    sector_pivot_smooth = sector_pivot.rolling(20).mean()
    fig, ax = plt.subplots(figsize=(12, 6))
    for sector in ["Energy", "Healthcare", "Tech"]:
        ax.plot(sector_pivot_smooth.index, sector_pivot_smooth[sector], label=sector, alpha=0.8)
    ax.set_title("Sector Sentiment Index Over Time (20-day rolling average, 2020-2023)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Lagged Sentiment (VADER compound, smoothed)")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/figures/sector_sentiment_over_time.png", dpi=150)
    plt.close(fig)

    metrics_compare = pd.DataFrame({"Base (Equal Weight)": metrics_base, "Sentiment-Tilted": metrics_tilted})
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    metric_names = ["annualised_return", "annualised_volatility", "sharpe_ratio", "max_drawdown"]
    titles = ["Annualised Return", "Annualised Volatility", "Sharpe Ratio", "Max Drawdown"]
    for ax, metric, title in zip(axes.flat, metric_names, titles):
        values = metrics_compare.loc[metric]
        ax.bar(values.index, values.values, color=["steelblue", "seagreen"])
        ax.set_title(title)
        ax.grid(alpha=0.3, axis="y")
        ax.tick_params(axis="x", rotation=15)
    fig.suptitle("Fusion Before vs After: Base vs Sentiment-Tilted Fund (2020-2023)")
    plt.tight_layout()
    plt.savefig("results/figures/fusion_before_after.png", dpi=150)
    plt.close(fig)

    print("Saved all Station 3 figures")

if __name__ == "__main__":
    main()
