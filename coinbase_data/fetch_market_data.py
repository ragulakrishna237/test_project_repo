import requests
import json
import time
from datetime import datetime, timedelta

# Note: While you have an API key and secret, Coinbase's Historical Market Data (Candles) 
# is available on their Public API. This means you don't actually need to use your 
# private keys to get pricing data! (Keys are mostly for checking personal balances or trading).

def fetch_market_data(product_id):
    """
    Fetches the last 3 hours of market data for a given asset.
    """
    # Coinbase API endpoint for historical candles
    url = f"https://api.exchange.coinbase.com/products/{product_id}/candles"
    
    # Calculate timestamps for the last 3 hours
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=3)
    
    # Granularity in seconds. 300 seconds = 5-minute intervals.
    granularity = 300 
    
    params = {
        "start": start_time.isoformat() + "Z",
        "end": end_time.isoformat() + "Z",
        "granularity": granularity
    }
    
    headers = {"Accept": "application/json"}
    
    print(f"Fetching last 3 hours of data for {product_id}...")
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # The Coinbase API returns an array of arrays: [time, low, high, open, close, volume]
        # We will map this to a readable dictionary so it is easy to understand.
        formatted_data = []
        for row in data:
            formatted_data.append({
                "timestamp": datetime.fromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M:%S'),
                "low": row[1],
                "high": row[2],
                "open": row[3],
                "close": row[4],
                "volume": row[5]
            })
        return formatted_data
    else:
        print(f"Error fetching {product_id}: {response.text}")
        return None

if __name__ == "__main__":
    # Coinbase trades cryptocurrencies, so we will use BTC and ETH as our "stocks"
    assets = ["BTC-USD", "ETH-USD"]
    
    all_data = {}
    
    for asset in assets:
        data = fetch_market_data(asset)
        if data:
            # Sort the data from oldest to newest so it graphs correctly left-to-right
            all_data[asset] = sorted(data, key=lambda x: x["timestamp"])
            print(f"Successfully fetched {len(data)} records for {asset}.")
            
        # Sleep for a moment to respect Coinbase's API rate limits
        time.sleep(1) 
        
    # Store the integrated data locally
    output_file = "coinbase_market_data.json"
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=4)
        
    print(f"\nAll market data successfully saved to {output_file}!")
