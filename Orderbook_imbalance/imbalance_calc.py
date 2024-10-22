import requests

def depth_info(symbol, percentage):
    base_url = 'https://api.binance.com'
    endpoint = '/api/v3/ticker/24hr'
    params = {'symbol': symbol}
    depth_endpoint='/api/v3/depth'
    limit = 5000
    depth_params = {'symbol': symbol, 'limit': limit}

    try:
        response = requests.get(base_url + endpoint, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        price = float(data['lastPrice'])

        percentage = percentage / 100
        min_price_bid = price - (price * (1 - percentage))
        max_price_ask = price + (price * (1 - percentage))

        depth_response = requests.get(base_url + depth_endpoint, depth_params)
        depth_response.raise_for_status()

        depth_data = depth_response.json()
        bids=depth_data['bids']
        asks=depth_data['asks']
        if len(bids) == 0 or len(asks) == 0:
            return

        # Calculate bid depth from min_price_bid to price
        bids_depth = sum(float(bid[1]) for bid in bids if min_price_bid <= float(bid[0]) <= price)
        bids_depth = round(bids_depth, 2)

        # Calculate ask depth from price to max_price_ask
        asks_depth = sum(float(ask[1]) for ask in asks if price <= float(ask[0]) <= max_price_ask)
        asks_depth = round(asks_depth, 2)
 
  
        bid_to_ask = round(bids_depth/asks_depth, 2)
        return bid_to_ask

    except requests.exceptions.RequestException as e:
        return f"Error fetching market data: {e}"
