# Prompt log - Funds and walk-forward backtest (portfolios.py)

## What I wanted
I wanted to build a combined equity+crypto fund with at least two optimisation methods,
backtested out-of-sample with no look-ahead bias, reusing my Part A foundation from last week's assignment

## Prompt(s)
I Worked through the backtest logic interactively in the console first , Ibuilt
equal-weight manually, confirmed the walk-forward loop mechanics (rebalance
dates, weight application and holding periods) by hand before inputing any
function, then asked Claude for the equivalent code to formalise into my
src/portfolios.py part in the project.

## What the assistant produced
compute_weights() (equal_weight, min_variance via scipy), oos_backtest()
(walk-forward, monthly rebalancing, 126-day initial window), performance_metrics()
(return, vol, Sharpe, max drawdown).

## What was wrong or risky
- The independent AI code review (Codex, via PyCharm) flagged that my
  oos_backtest()'s historical window included the rebalance date's own
  return, contradicting the function's own docstring which said "not
  including" that date. This was a real mistake or maybe an inconsistency, not just a style
  issue - it meant the model could theoretically use same-day information.
- I verified this myself before fixing it: confirmed the equal-weight fund's
  results were completely unaffected by the change (since it doesn't use
  historical returns at all), while minimum-variance's numbers shifted only
  marginally (e.g. annualised return 7.014% -> 7.013%) - reassuring evidence
  the original bug had not meaningfully distorted my results, but it was
  still worth fixing for methodological correctness.
- I initially only built one asset universe (combined). A later review
  pointed out equity-only and crypto-only funds would strengthen the
  Innovation criterion, which I then added by re-running the same
  backtest function on subsets of my returns panel.

## What I changed and why
- Changed history = wide_returns.loc[:reb_date, tickers] to
  history = wide_returns.loc[:reb_date, tickers].iloc[:-1], strictly
  excluding the rebalance date, removing any ambiguity for a reader.
- Extended the fund menu from 1 universe to 3 (Combined, Equity-Only,
  Crypto-Only), each with both methods, after confirming the code
  generalised cleanly to any subset of tickers without changes.
