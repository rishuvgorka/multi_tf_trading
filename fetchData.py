import pandas as pd
import requests
import time

def fetch_klines(symbol, interval, start_ts, end_ts, limit=1000):
    url = "https://api.binance.com/api/v3/klines"
    all_klines = []
    while start_ts < end_ts:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ts,
            "endTime": end_ts,
            "limit": limit
        }
        response = requests.get(url, params=params)
        data = response.json()
        if not data:
            break
        all_klines.extend(data)
        last_time = data[-1][0]
        start_ts = last_time + 1
        time.sleep(0.3)  # Respect rate limits
    df = pd.DataFrame(data=all_klines, columns=[
        'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close_time', 'Quote_asset_volume', 'Number_of_trades',
        'Taker_buy_base', 'Taker_buy_quote', 'Ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    return df

# Time range for ~90 days
symbol = "BTCUSDT"
end = int(time.time() * 1000)
start = end - 90 * 24 * 60 * 60 * 1000  # 90 days in ms

#downloading 15m data
print("Fetching 15m data...")
df_15m = fetch_klines(symbol, "15m", start, end)
df_15m.to_csv("inFiles/15m_data.csv")

#download 1h data
print("Fetching 1h data...")
df_1h = fetch_klines(symbol, "1h", start, end)
df_1h.to_csv("inFiles/1h_data.csv")


