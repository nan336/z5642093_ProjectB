# CLAUDE.md - my agent instructions for FINS3645 Part B

## Project context
FINS3645 FinTech Project 2026, Part B (Funds, Sentiment & App - Stations 3-4).
Full brief: PROJECT_BRIEF.md. Reuses my own Part A foundation (src/etl.py,
src/features.py, copied across and verified identical results).
Building: six out-of-sample funds across three asset universes (Combined,
Equity-Only, Crypto-Only) and two optimisation methods (Equal Weight,
Minimum-Variance), a VADER sentiment index, a sentiment-tilt fusion, and a
Streamlit app for Compass Invest.

## Working rules
- Walk-forward backtest only: weights at each rebalance date computed strictly
  from data before that date (history.iloc[:-1] excludes the rebalance date
  itself, after a Codex review flagged the original version as including it).
- Monthly rebalancing, 6-month (126 trading day) initial estimation window.
  First live backtest date: 2020-08-03.
- Sentiment must be lagged by at least one trading day, using the full equity
  trading calendar (not just "the previous row with data") - gaps are
  forward-filled first, then shifted, so the lag always means "yesterday's
  trading day", not "whenever the last headline happened to land".
- Sentiment/fusion applies to equity tickers only - crypto has no news data,
  so it gets a neutral tilt factor (no change).
- The deployed Streamlit app must only read precomputed results/ files -
  never recompute backtests or run VADER live in the app itself.
- Required output filenames must match exactly: results/data/fund_returns.csv,
  fund_weights.csv, sector_sentiment_index.csv,
  results/tables/performance_metrics.csv.

## How I check AI output
- Test every new function interactively in the PyCharm console first, with
  real numbers I can sanity-check by hand, before writing it into src/ files.
- Restart the console after editing any module (stale-import issues are
  common otherwise).
- Ask an independent AI reviewer (Codex, via PyCharm) to check finished code
  against the rubric, then verify each flagged issue myself before fixing it.
- Keep a prompt log per task in ai/.
