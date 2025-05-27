import subprocess
import logging
import os
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_rates_file():
    """Create a backup of the current rates.json file."""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../backend/fixtures')
    rates_file = os.path.join(fixtures_dir, 'rates.json')
    
    if os.path.exists(rates_file):
        backup_name = f'rates_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        backup_file = os.path.join(fixtures_dir, backup_name)
        
        try:
            with open(rates_file, 'r', encoding='utf-8') as src, open(backup_file, 'w', encoding='utf-8') as dst:
                json.dump(json.load(src), dst, indent=2, ensure_ascii=False)
            logger.info(f'Created backup: {backup_file}')
            return True
        except Exception as e:
            logger.error(f'Failed to create backup: {str(e)}')
            return False
    return True

def clear_rates_file():
    """Clear the rates.json file to start fresh."""
    rates_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../backend/fixtures/rates.json')
    try:
        with open(rates_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        logger.info('Cleared rates.json file')
        return True
    except Exception as e:
        logger.error(f'Failed to clear rates.json: {str(e)}')
        return False

def run_rate_fetchers():
    """Run both CBR and Binance rate fetchers."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cbr_script = os.path.join(current_dir, 'cbr_currency_rates.py')
    binance_script = os.path.join(current_dir, 'binance_crypto_rates.py')
    
    try:
        # Create backup of current rates
        if not backup_rates_file():
            return False
            
        # Clear rates file to start fresh
        if not clear_rates_file():
            return False
        
        # Run CBR rates fetcher
        logger.info('Starting CBR rates fetcher...')
        subprocess.run(['python', cbr_script], check=True)
        
        # Run Binance rates fetcher
        logger.info('Starting Binance rates fetcher...')
        subprocess.run(['python', binance_script], check=True)
        
        logger.info('Successfully updated all rates')
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f'Error running rate fetchers: {str(e)}')
        return False
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return False

if __name__ == '__main__':
    run_rate_fetchers()