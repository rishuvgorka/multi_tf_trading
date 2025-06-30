from binance.client import Client
import pandas as pd
import os

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

client = Client(api_key, api_secret)

def fetch_ohlcv(symbol="BTCUSDT", interval="15m", limit=1000):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'num_trades',
        'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

# Fetch and save
df_15m = fetch_ohlcv(interval=Client.KLINE_INTERVAL_15MINUTE)
df_15m.to_csv("inFiles/15m_data.csv")

df_1h = fetch_ohlcv(interval=Client.KLINE_INTERVAL_1HOUR)
df_1h.to_csv("inFiles/1h_data.csv")

