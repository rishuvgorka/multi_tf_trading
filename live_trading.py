import time
import pandas as pd
from binance_client import BinanceClient
from strategy import MultiTimeframeStrategy

client = BinanceClient()
POSITION_CSV = 'ouFiles/position.csv'
TRADE_LOG = 'ouFiles/live_trades.csv'

def load_position():
    try:
        return pd.read_csv(POSITION_CSV).iloc[0].to_dict()
    except:
        return {"side": "None", "entry_price": 0, "sl": 0, "tp": 0}

def save_position(pos_dict):
    pd.DataFrame([pos_dict]).to_csv(POSITION_CSV, index=False)

def log_trade(row):
    try:
        df = pd.read_csv(TRADE_LOG)
        df = pd.concat([df, pd.DataFrame([row])])
    except:
        df = pd.DataFrame([row])
    df.to_csv(TRADE_LOG, index=False)

def run_live():
    df_15m = client.get_klines('15m', 100)
    df_1h = client.get_klines('1h', 100)
    price = df_15m['close'].iloc[-1]
    pos = load_position()

    # SL/TP monitoring
    if pos['side'] != 'None':
        if (pos['side'] == 'BUY' and (price <= pos['sl'] or price >= pos['tp'])) or \
           (pos['side'] == 'SELL' and (price >= pos['sl'] or price <= pos['tp'])):
            log_trade({"timestamp": df_15m.index[-1], "side": "EXIT_" + pos['side'], "price": price})
            save_position({"side": "None", "entry_price": 0, "sl": 0, "tp": 0})
            print("Exited", pos['side'], "at", price)
        return

    strategy = MultiTimeframeStrategy(df_15m, df_1h)
    signal = strategy.get_signal()
    if not signal:
        return

    usdt = client.get_balance('USDT')
    coin_price = client.get_price()
    qty = round((usdt * 0.95) / coin_price, 6)

    order = client.place_market_order(signal['signal'], qty)
    if 'status' in order and order['status'] == 'FILLED':
        sl = signal['price'] * (0.99 if signal['signal'] == 'BUY' else 1.01)
        tp = signal['price'] * (1.03 if signal['signal'] == 'BUY' else 0.97)
        save_position({"side": signal['signal'], "entry_price": signal['price'], "sl": sl, "tp": tp})
        log_trade({"timestamp": signal['timestamp'], "side": signal['signal'], "price": signal['price']})
        print("Entered", signal['signal'], "at", signal['price'])

if __name__ == "__main__":
    while True:
        try:
            run_live()
        except Exception as e:
            print("Error:", e)
        time.sleep(60)

