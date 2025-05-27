import requests
import logging
import time
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
        max_retries = 3
        retry_delay = 5  # seconds

        while True:
            for attempt in range(max_retries):
                try:
                    resp = self.session.get(url, params=params, timeout=10)
                    if resp.status_code == 451:
                        logger.error("Access denied (HTTP 451). This might be due to regional restrictions. Please check your VPN connection.")
                        return []
                    resp.raise_for_status()
                    klines = resp.json()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to fetch data after {max_retries} attempts: {str(e)}")
                        return []
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
            
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
        max_retries = 3
        retry_delay = 5  # seconds

        while True:
            for attempt in range(max_retries):
                try:
                    resp = self.session.get(url, params=params, timeout=10)
                    if resp.status_code == 451:
                        logger.error("Access denied (HTTP 451). This might be due to regional restrictions. Please check your VPN connection.")
                        return {}
                    resp.raise_for_status()
                    klines = resp.json()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to fetch data after {max_retries} attempts: {str(e)}")
                        return {}
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
            
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
        if not klines:
            logger.error(f"Failed to fetch historical rates for {symbol}")
            return ""
            
        usdt_rub = self.fetch_usdt_rub_rates(days)
        if not usdt_rub:
            logger.error("Failed to fetch USDT/RUB rates")
            return ""
        
        # Mapping of crypto symbols to their primary keys
        crypto_pk_map = {
            'BTC': 5,
            'ETH': 6,
            'TON': 7
        }
        
        if symbol not in crypto_pk_map:
            logger.warning(f"Unsupported crypto symbol: {symbol}")
            return ""
        
        filename = "rates.json"
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../backend/fixtures', filename)
        
        try:
            # Load existing data if file exists
            existing_data = []
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as jsonfile:
                        existing_data = json.load(jsonfile)
                except json.JSONDecodeError as e:
                    logger.error(f"Error reading existing rates file: {str(e)}")
                    return ""
            
            # Create new entries
            new_entries = []
            for k in klines:
                try:
                    date = datetime.utcfromtimestamp(k[0] // 1000)
                    close_usdt = float(k[4])
                    rub = usdt_rub.get(date.strftime('%Y-%m-%d'))
                    if rub is not None:
                        price_rub = close_usdt * rub
                        timestamp = date.strftime('%Y-%m-%dT%H:%M:%S+03:00')
                        
                        # Find existing entry for this currency and date
                        existing_entry = None
                        for entry in existing_data:
                            if (entry['fields']['currency'] == crypto_pk_map[symbol] and
                                entry['fields']['timestamp'] == timestamp):
                                existing_entry = entry
                                break
                        
                        if existing_entry:
                            # Update existing entry
                            existing_entry['fields']['cost'] = round(price_rub, 4)
                        else:
                            # Add new entry
                            new_entries.append({
                                'model': 'api.rate',
                                'pk': len(existing_data) + len(new_entries) + 1,
                                'fields': {
                                    'currency': crypto_pk_map[symbol],
                                    'cost': round(price_rub, 4),
                                    'timestamp': timestamp
                                }
                            })
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Error processing rate entry: {str(e)}")
                    continue
            
            if not new_entries and not any(entry['fields']['currency'] == crypto_pk_map[symbol] for entry in existing_data):
                logger.warning(f"No valid rates found for {symbol}")
                return ""
            
            # Combine existing and new entries
            all_entries = existing_data + new_entries
            
            # Write combined data back to file
            try:
                with open(filepath, 'w', encoding='utf-8') as jsonfile:
                    json.dump(all_entries, jsonfile, indent=2, ensure_ascii=False)
            except IOError as e:
                logger.error(f"Error writing to rates file: {str(e)}")
                return ""
            
            logger.info(f"Saved/updated {len(new_entries)} {symbol}/RUB rates in {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Unexpected error saving data to JSON: {str(e)}")
            return ""

if __name__ == "__main__":
    b = BinanceCryptoRates()
    for symbol in ['BTC', 'ETH', 'TON']:
        b.save_crypto_rub_rates(symbol)