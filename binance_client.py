import requests, time, hmac, hashlib
import pandas as pd
from urllib.parse import urlencode
from config import API_KEY, API_SECRET, BASE_URL

class BinanceClient:
    def __init__(self, symbol='BTCUSDT'):
        self.symbol = symbol

    def _sign(self, params):
        return hmac.new(API_SECRET.encode(), urlencode(params).encode(), hashlib.sha256).hexdigest()

    def get_klines(self, interval, limit=100):
        url = f"{BASE_URL}/v3/klines"
        params = {"symbol": self.symbol, "interval": interval, "limit": limit}
        r = requests.get(url, params=params)
        df = pd.DataFrame(r.json(), columns=[
            'timestamp','open','high','low','close','volume',
            'close_time','quote_asset_vol','trades','taker_buy_base_vol',
            'taker_buy_quote_vol','ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df[['open','high','low','close','volume']].astype(float)
        return df

    def get_price(self):
        r = requests.get(f"{BASE_URL}/v3/ticker/price", params={"symbol": self.symbol})
        return float(r.json()["price"])

    def get_balance(self, asset='USDT'):
        ts = int(time.time() * 1000)
        params = {'timestamp': ts}
        params['signature'] = self._sign(params)
        headers = {'X-MBX-APIKEY': API_KEY}
        r = requests.get(f"{BASE_URL}/v3/account", params=params, headers=headers)
        balances = r.json()['balances']
        for b in balances:
            if b['asset'] == asset:
                return float(b['free'])
        return 0.0

    def place_market_order(self, side, quantity):
        ts = int(time.time() * 1000)
        params = {
            'symbol': self.symbol,
            'side': side,
            'type': 'MARKET',
            'quantity': quantity,
            'timestamp': ts
        }
        params['signature'] = self._sign(params)
        headers = {'X-MBX-APIKEY': API_KEY}
        return requests.post(f"{BASE_URL}/v3/order", params=params, headers=headers).json()

