# AGENTS.md - my instructions for Codex (PyCharm AI Chat)

## Project context
FINS3645 FinTech Project 2026, Part B (Funds, Sentiment & App - Stations 3-4).
Full brief: PROJECT_BRIEF.md. Reuses my own Part A foundation.

## How I used Codex in this project
Same as Part A: Codex is used as an independent reviewer, not my primary
coding assistant. I build and test code myself (with Claude) interactively in
the console first, then ask Codex to check the finished code against the Part
B rubric.

## Working rules for review tasks
- I Check specifically against PROJECT_BRIEF.md's Part B requirements (funds,
  backtest rules, sentiment lag, fusion, required output filenames, app
  requirements) and the marking rubric, not general code quality.
- I also ruled out any specific gaps with the exact rubric wording that supports the
  claim, so I can verify it myself before acting on it.

## What Codex caught that I acted on
- Flagged that my original oos_backtest() included the rebalance date's own
  return in the historical window used to compute weights, even though the
  docstring said "not including" that date. I verified this was a real
  inconsistency and fixed it to strictly exclude the rebalance date.
- Flagged that fund_weights.csv, fund_returns.csv, and performance_metrics.csv
  had an unnamed index column ("Unnamed: 0") instead of a proper "date"/"fund"
  header. Fixed with index_label in to_csv().
- Flagged that streamlit_app.py, the report, and the AI prompt logs were all
  still in starter/placeholder state at that point in the project - used as
  a checklist for what to build next.
- Flagged that my Allocation tab only let users split between 2 of the 6
  funds, when the rubric asks users to "set an allocation across funds"
  (plural). Fixed by rebuilding the tab to generate a slider for every fund
  dynamically, with weights auto-normalised to 100%.
- Flagged that my Sharpe barplot only showed 3 funds, out of date after
  expanding the fund menu - the chart no longer matched
  performance_metrics.csv. Fixed by rebuilding it to plot every fund
  present in the metrics table dynamically.
- Pointed out my fund menu only covered the required minimum at that point,
  and that equity-only/crypto-only funds would strengthen Innovation. I
  extended the backtest to run on subsets of the returns panel, producing
  six funds across three asset universes with no changes to the underlying
  backtest logic itself.
