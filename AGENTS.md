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
- Check specifically against PROJECT_BRIEF.md's Part B requirements (funds,
  backtest rules, sentiment lag, fusion, required output filenames, app
  requirements) and the marking rubric, not general code quality.
- Point out specific gaps with the exact rubric wording that supports the
  claim, so I can verify it myself before acting on it.

## What Codex caught that I acted on
- Flagged that my original oos_backtest() included the rebalance date's own
  return in the historical window used to compute weights, even though the
  docstring said "not including" that date. I verified this was a real
  inconsistency (even if arguably defensible under one interpretation) and
  fixed it to strictly exclude the rebalance date, removing any ambiguity.
- Flagged that fund_weights.csv, fund_returns.csv, and performance_metrics.csv
  had an unnamed index column ("Unnamed: 0") instead of a proper "date"/"fund"
  header. Fixed with index_label in to_csv().
- Flagged that streamlit_app.py, the report, and the AI prompt logs were all
  still in starter/placeholder state at that point in the project - accurate,
  and used as a checklist for what to build next.
