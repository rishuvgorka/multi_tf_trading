import pandas as pd
from backtesting import Backtest,Strategy
from strategy import MultiTimeframeStrategy

class BacktestStrategy(Strategy):
    def init(self):
        self.ema20 = self.I(lambda x: pd.Series(x).ewm(span=20).mean(), self.data.Close)
        self.rsi14 = self.I(self._calculate_rsi, self.data.Close)
        self.trend_signal = self.data.trend_signal  # already preprocessed

    def _calculate_rsi(self, prices, period=14):
        delta = pd.Series(prices).diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = -delta.where(delta < 0, 0).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def next(self):
        price = self.data.Close[-1]

        if self.trend_signal[-1]:
            if price > self.ema20[-1] and self.rsi14[-1] < 70:
                if not self.position:
                    sl = price * 0.99
                    tp = price * 1.03
                    self.buy(sl=sl, tp=tp)

        elif not self.trend_signal[-1]:
            if price < self.ema20[-1] and self.rsi14[-1] > 30:
                if not self.position:
                    sl = price * 1.01
                    tp = price * 0.97
                    self.sell(sl=sl, tp=tp)


def prepare_data(df_15m, df_1h):
    df_1h['sma_50'] = df_1h['Close'].rolling(50).mean()
    df_1h['trend'] = df_1h['Close'] > df_1h['sma_50']
    df_15m['trend_signal'] = df_1h['trend'].resample('15min').ffill().reindex(df_15m.index, method='ffill')
    return df_15m.dropna()

if __name__ == '__main__':
    df_15m = pd.read_csv('inFiles/15m_data.csv', parse_dates=['timestamp'], index_col='timestamp')
    df_1h = pd.read_csv('inFiles/1h_data.csv', parse_dates=['timestamp'], index_col='timestamp')

    df = prepare_data(df_15m, df_1h)
    bt = Backtest(df, BacktestStrategy, cash=1000000, commission=0.001)
    stats = bt.run()
    bt.plot()
    stats['_trades'].to_csv("ouFiles/backtest_trades.csv", index=False)

