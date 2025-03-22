import requests
from datetime import datetime

class MoexCurrencyRates:
    BASE_URL = "https://www.moex.com/api/"

    def __init__(self):
        pass

    def fetch_currency_rates(self):
        """Fetch currency rates from MOEX."""
        url = f"{self.BASE_URL}currency_rates"
        response = requests.get(url)
        if response.status_code == 200:
            return self.parse_currency_rates(response.json())
        else:
            raise Exception("Failed to fetch data from MOEX")

    def parse_currency_rates(self, data):
        """Parse the currency rates data from MOEX."""
        rates = []
        for item in data['rates']:
            rate = {
                'currency': item['currency'],
                'price': item['price'],
                'datetime': datetime.strptime(item['datetime'], '%Y-%m-%dT%H:%M:%S')
            }
            rates.append(rate)
        return rates

# Example usage
if __name__ == "__main__":
    moex_rates = MoexCurrencyRates()
    try:
        rates = moex_rates.fetch_currency_rates()
        for rate in rates:
            print(f"Currency: {rate['currency']}, Price: {rate['price']}, DateTime: {rate['datetime']}")
    except Exception as e:
        print(e)