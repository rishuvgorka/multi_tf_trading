import pandas as pd
from backtesting import Backtest
from strategy import MultiTimeframeStrategy

def prepare_data(df_15m, df_1h):
    df_1h['sma_50'] = df_1h['Close'].rolling(50).mean()
    df_1h['trend'] = df_1h['Close'] > df_1h['sma_50']
    df_15m['trend_signal'] = df_1h['trend'].resample('15min').ffill().reindex(df_15m.index, method='ffill')
    return df_15m.dropna()

if __name__ == '__main__':
    df_15m = pd.read_csv('../inFiles/15m_data.csv', parse_dates=['timestamp'], index_col='timestamp')
    df_1h = pd.read_csv('../inFiles/1h_data.csv', parse_dates=['timestamp'], index_col='timestamp')

    df = prepare_data(df_15m, df_1h)
    bt = Backtest(df, MultiTimeframeStrategy, cash=1000000, commission=0.001)
    stats = bt.run()
    bt.plot()
    stats['_trades'].to_csv("../ouFiles/backtest_trades.csv", index=False)

