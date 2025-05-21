import requests
import logging
from datetime import datetime, timedelta
import os
import json
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceCryptoRates:
    BASE_URL = "https://api.binance.com/api/v3/"
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data')
    SUPPORTED_PAIRS = {
        'BTC': 'BTCUSDT',
        'ETH': 'ETHUSDT',
        'TON': 'TONUSDT',
        # Add more crypto symbols as needed
    }
    USDT_RUB_PAIR = 'USDTRUB'

    def __init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})

    def fetch_historical_rates(self, symbol: str, days: int = 1825) -> List[Dict[str, Any]]:
        if symbol not in self.SUPPORTED_PAIRS:
            raise ValueError(f"Unsupported symbol: {symbol}")
        pair = self.SUPPORTED_PAIRS[symbol]
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        url = f"{self.BASE_URL}klines"
        params = {
            'symbol': pair,
            'interval': '1d',
            'startTime': start_time,
            'endTime': end_time,
            'limit': 1000
        }
        all_klines = []
        while True:
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            klines = resp.json()
            if not klines:
                break
            all_klines.extend(klines)
            if len(klines) < 1000:
                break
            params['startTime'] = klines[-1][0] + 86400000
        logger.info(f"Fetched {len(all_klines)} daily klines for {pair}")
        return all_klines

    def fetch_usdt_rub_rates(self, days: int = 1825) -> Dict[str, float]:
        pair = self.USDT_RUB_PAIR
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        url = f"{self.BASE_URL}klines"
        params = {
            'symbol': pair,
            'interval': '1d',
            'startTime': start_time,
            'endTime': end_time,
            'limit': 1000
        }
        all_klines = []
        while True:
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            klines = resp.json()
            if not klines:
                break
            all_klines.extend(klines)
            if len(klines) < 1000:
                break
            params['startTime'] = klines[-1][0] + 86400000
        logger.info(f"Fetched {len(all_klines)} daily klines for {pair}")
        date_to_price = {}
        for k in all_klines:
            date = datetime.utcfromtimestamp(k[0] // 1000).strftime('%Y-%m-%d')
            close = float(k[4])
            date_to_price[date] = close
        return date_to_price

    def save_crypto_rub_rates(self, symbol: str, days: int = 1825):
        klines = self.fetch_historical_rates(symbol, days)
        usdt_rub = self.fetch_usdt_rub_rates(days)
        rates = []
        for k in klines:
            date = datetime.utcfromtimestamp(k[0] // 1000).strftime('%Y-%m-%d')
            close_usdt = float(k[4])
            rub = usdt_rub.get(date)
            if rub is not None:
                price_rub = close_usdt * rub
                rates.append({
                    'date': date,
                    'currency': symbol,
                    'code': symbol,
                    'nominal': 1,
                    'price': round(price_rub, 4)
                })
        filename = f"{symbol.lower()}_rub_5year_rates_{datetime.now().strftime('%Y-%m-%d')}.json"
        filepath = os.path.join(self.DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rates, f, indent=4, ensure_ascii=False)
        logger.info(f"Saved {len(rates)} {symbol}/RUB rates to {filepath}")
        return filepath

if __name__ == "__main__":
    b = BinanceCryptoRates()
    for symbol in ['BTC', 'ETH', 'TON']:
        b.save_crypto_rub_rates(symbol)