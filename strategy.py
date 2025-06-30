import pandas as pd

class MultiTimeframeStrategy:
    def __init__(self, df_15m, df_1h):
        self.df_15m = df_15m
        self.df_1h = df_1h

    def calculate_indicators(self):
        self.df_15m['EMA20'] = self.df_15m['close'].ewm(span=20).mean()
        self.df_15m['RSI14'] = self._calculate_rsi(self.df_15m)
        self.df_1h['SMA50'] = self.df_1h['close'].rolling(50).mean()

    def _calculate_rsi(self, df, period=14):
        delta = df['close'].diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = -delta.clip(upper=0).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def get_signal(self):
        self.calculate_indicators()
        last_15m = self.df_15m.iloc[-1]
        last_1h = self.df_1h.iloc[-1]

        trend_up = last_1h['close'] > last_1h['SMA50']
        if trend_up and last_15m['close'] > last_15m['EMA20'] and last_15m['RSI14'] < 70:
            return {"signal": "BUY", "price": last_15m['close'], "timestamp": last_15m.name}
        elif not trend_up and last_15m['close'] < last_15m['EMA20'] and last_15m['RSI14'] > 30:
            return {"signal": "SELL", "price": last_15m['close'], "timestamp": last_15m.name}
        else:
            return None

