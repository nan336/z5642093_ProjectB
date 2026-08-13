# Prompt log - Sentiment model, fusion, and Streamlit app

## What I wanted
Score my Part A headline panel with VADER and build a lagged sector sentiment
index then fold it into a fund via a tilt, and build an app that reads only
precomputed results.

## Prompt(s)
Same interactive-first approach: tested VADER scoring, calendar reindexing,
forward-fill, and the one-day lag manually on a single ticker in the console,
verifying each step by hand, before writing src/sentiment.py or src/fusion.py.
For the app, asked Claude to build it tab by tab, testing each tab live in
the browser before adding the next.

## What the assistant produced
score_headlines() (VADER, calendar-reindexed, forward-filled, lagged),
sector_sentiment_index(), apply_sentiment() (multiplicative tilt), and a
4-tab Streamlit app (Funds, Allocation, Sentiment, Data).

## What was wrong or risky
- Renaming a pandas Series before charting was necessary - st.bar_chart()
  crashed with an Altair encoding error because a Series named after a
  Timestamp (containing colons) broke Altair's parsing. Fixed by renaming
  the Series before charting.
- My first Allocation tab only let users split between 2 of the 6 funds.
  An AI review pointed out the rubric wants allocation "across funds"
  (plural, implying more than 2), so I rebuilt it to generate a slider for
  every fund dynamically from fund_returns.columns, normalising weights to
  sum to 100% automatically.
- My first Sharpe  barplot at the start had only 3 funds so i change it,  and expanded it
  to 6 base funds + 1 sentiment-tilted fund. An AI review caught this
  mismatch against my own performance_metrics.csv; fixed by rebuilding the
  chart to plot every fund in the metrics dict dynamically.
- I  kept the fusion mechanism's renormalisation side-effect
  (crypto's total weight drifts slightly with aggregate equity sentiment)
  rather than engineering it away, since the project brief explicitly says
  a naive first attempt is acceptable - i chose to put this it in the report.

## What I changed and why
- I Fixed the Altair chart crash by renaming the Series before st.bar_chart().
- I Rebuilt the Allocation tab to cover all 6 funds with normalised sliders.
- Rebuilt the Sharpe barplot to dynamically include all funds, not a fixed
  sample of 3.
- Kept (rather than "fixed") the crypto-weight renormalisation drift as a
  stated, accepted simplification for this baseline fusion attempt.
