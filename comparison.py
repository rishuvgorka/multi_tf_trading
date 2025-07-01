import pandas as pd

# Load and convert timestamps
backtest = pd.read_csv("ouFiles/backtest_trades.csv")
live = pd.read_csv("ouFiles/live_trades.csv")

backtest['timestamp'] = pd.to_datetime(backtest['timestamp'])
live['timestamp'] = pd.to_datetime(live['timestamp'])

# Filter only entry trades (optional safety check)
live_entries = live[~live['side'].str.startswith('EXIT')]
backtest_entries = backtest[~backtest['side'].str.startswith('EXIT')]

match_count = 0
for _, bt_row in backtest_entries.iterrows():
    matches = live_entries[
        (live_entries['side'] == bt_row['side']) &
        (abs(live_entries['timestamp'] - bt_row['timestamp']) <= pd.Timedelta(minutes=15))
    ]
    if not matches.empty:
        match_count += 1

print(f"Matched trades: {match_count}/{len(backtest_entries)}")

