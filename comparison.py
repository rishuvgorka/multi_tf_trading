import pandas as pd

backtest = pd.read_csv("ouFiles/backtest_trades.csv")
live = pd.read_csv("ouFiles/live_trades.csv")

match_count = 0
for _, row in backtest.iterrows():
    matches = live[
        (live['side'] == row['side']) &
        (abs(pd.to_datetime(live['timestamp']) - pd.to_datetime(row['timestamp'])) < pd.Timedelta(minutes=15))
    ]
    if not matches.empty:
        match_count += 1

print(f"Matched trades: {match_count}/{len(backtest)}")

