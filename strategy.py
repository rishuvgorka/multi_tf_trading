from backtesting import Strategy
import pandas as pd
from backtesting.lib import crossover

def calculate_rsi(df, period=14):
    delta = df.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

class MultiTimeframeStrategy(Strategy):
    def init(self):
        price = self.data.Close

        # Indicators from 15m
        self.ema_20 = self.I(lambda x: pd.Series(x).ewm(span=20, adjust=False).mean(), price)
        self.rsi_14 = self.I(lambda x: calculate_rsi(pd.Series(x), 14), price)

        # External 1H trend confirmation
        self.trend_signal = self.data.trend_signal

    def next(self):
        close = self.data.Close[-1]
        ema = self.ema_20[-1]
        rsi = self.rsi_14[-1]
        trend = self.trend_signal[-1]

        if trend and close > ema and rsi < 70:
            if not self.position:
                self.buy(sl=close * 0.99, tp=close * 1.03, size=1)
        elif not trend and close < ema and rsi > 30:
            if not self.position:
                self.sell(sl=close * 1.01, tp=close * 0.97, size = 1)

