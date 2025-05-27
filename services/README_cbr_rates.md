# CBR Currency Rates Module

This module provides functionality to fetch and store historical exchange rates for multiple currencies (USD, EUR, CNY, AED) against RUB from the Central Bank of Russia (CBR) API.

## Features

- Fetch exchange rates for USD/RUB, EUR/RUB, CNY/RUB, and AED/RUB for any date range
- Retrieve historical data for the past five years
- Save exchange rates to CSV files for further analysis
- Error handling and retry mechanism for API requests
- Detailed logging

## Usage

### Basic Usage

```python
from services.cbr_currency_rates import CBRCurrencyRates

# Create an instance of the CBR currency rates client
cbr_rates = CBRCurrencyRates()

# Fetch USD/RUB rates for the past five years (default currency is USD)
rates_usd = cbr_rates.fetch_five_year_rates()

# Fetch EUR/RUB rates for the past five years
rates_eur = cbr_rates.fetch_five_year_rates("EUR")

# Save the rates to CSV files
filepath_usd = cbr_rates.save_rates_to_csv(rates_usd)
filepath_eur = cbr_rates.save_rates_to_csv(rates_eur)

# Display some of the USD rates
for rate in rates_usd[:3]:
    print(f"Date: {rate.date.strftime('%Y-%m-%d')}, USD/RUB: {rate.price:.4f}")

# Display some of the EUR rates
for rate in rates_eur[:3]:
    print(f"Date: {rate.date.strftime('%Y-%m-%d')}, EUR/RUB: {rate.price:.4f}")
```

### Fetching Rates for a Specific Period

```python
from datetime import datetime
from services.cbr_currency_rates import CBRCurrencyRates

# Create an instance of the CBR currency rates client
cbr_rates = CBRCurrencyRates()

# Define the date range
start_date = datetime(2022, 1, 1)
end_date = datetime(2022, 12, 31)

# Fetch USD/RUB rates for the specified period
rates_usd = cbr_rates.fetch_currency_dynamic(start_date, end_date, "USD")

# Fetch CNY/RUB rates for the specified period
rates_cny = cbr_rates.fetch_currency_dynamic(start_date, end_date, "CNY")

# Save the rates to custom CSV files
filepath_usd = cbr_rates.save_rates_to_csv(rates_usd, "usd_rub_2022.csv")
filepath_cny = cbr_rates.save_rates_to_csv(rates_cny, "cny_rub_2022.csv")
```

### Fetching Rate for a Specific Date

```python
from datetime import datetime
from services.cbr_currency_rates import CBRCurrencyRates

# Create an instance of the CBR currency rates client
cbr_rates = CBRCurrencyRates()

# Fetch USD/RUB rate for a specific date
date = datetime(2023, 5, 15)
rate_usd = cbr_rates.fetch_currency_rate(date, "USD")

# Fetch AED/RUB rate for a specific date
rate_aed = cbr_rates.fetch_currency_rate(date, "AED")

if rate_usd:
    print(f"USD/RUB on {date.strftime('%Y-%m-%d')}: {rate_usd.price:.4f}")
else:
    print(f"No USD/RUB rate available for {date.strftime('%Y-%m-%d')}")
    
if rate_aed:
    print(f"AED/RUB on {date.strftime('%Y-%m-%d')}: {rate_aed.price:.4f}")
else:
    print(f"No AED/RUB rate available for {date.strftime('%Y-%m-%d')}")
```

## Running the Script

A convenience script is provided to fetch and save the rates for multiple currencies (USD, EUR, CNY, AED) against RUB for the past five years:

```bash
python scripts/fetch_cbr_rates.py
```

This script will:
1. Fetch all rates for USD/RUB, EUR/RUB, CNY/RUB, and AED/RUB for the past five years from the CBR API
2. Save the data to separate CSV files in the `data` directory
3. Display statistics about the retrieved rates for each currency

## Data Format

The CSV file contains the following columns:
- `date`: The date of the exchange rate (YYYY-MM-DD)
- `currency`: The currency name (e.g., "Доллар США")
- `code`: The currency code (e.g., "USD")
- `nominal`: The nominal value (typically 1)
- `price`: The exchange rate in rubles

## API Reference

The module uses the CBR XML API described at https://cbr.ru/development/SXML/

Specifically, it uses the following endpoints:
- `XML_daily.asp` - for fetching rates on a specific date
- `XML_dynamic.asp` - for fetching rates over a date range

## Requirements

- Python 3.6+
- requests
- xml.etree.ElementTree (standard library)