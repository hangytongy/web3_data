from velodata import lib as velo
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests

def init_client():
    api_key = '4a2a1de7c0d440c983bf5b0e7f1fc366'
    # new velo client
    client = velo.client(api_key)
    return client 

def get_exchanges(client):
    exchanges = [x['exchange'] for x in client.get_futures()]
    exchanges = list(set(exchanges))
    print(exchanges)
    return exchanges

def open_interest(client,start_time,end_time,token,interval):
    
    exchanges = get_exchanges(client)

    # from one hour ago in 1 minute resolution
    params = {
          'type': 'futures',
          'columns': ['funding_rate', 'coin_open_interest_close'],
          'exchanges': exchanges,
          'coins': [token],
          'begin': start_time,
          'end': end_time,
          'resolution': interval
        }

    # returns dataframe
    df = client.get_rows(params)

    try:
        # oi-weighted funding = SUM(funding*OI) / SUM(OI)
        df['funding_rate'] = df['funding_rate'] * df['coin_open_interest_close']
        df = df.groupby(df['time']).sum(numeric_only=True)
        df['funding_rate'] = df['funding_rate'] / df['coin_open_interest_close']
        
        return df
    except:
        return pd.DataFrame()

def get_price_history(token,interval,end_time,start_time):
    # Binance API endpoint for historical klines
    url = "https://api.binance.com/api/v3/klines"
    
    # Parameters for the API call
    #end_time = int(datetime.now().timestamp() * 1000)
    #start_time = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
    
    print(end_time)
    print(start_time)
    
    symbol = token + 'USDT'
    
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time,
        'endTime': end_time,
        'limit': 1000  # Maximum limit allowed by Binance API
    }

    # Make the API request
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Parse the response into a DataFrame
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close Time', 'Quote Asset Volume', 'Number of Trades',
            'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
        ])

        # Convert 'Open Time' and 'Close Time' to datetime
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')

        # Set 'Open Time' as the index
        df.set_index('Open Time', inplace=True)

        # Optionally, drop unnecessary columns
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Convert 'Close' to numeric
        df['Close'] = pd.to_numeric(df['Close'])

        return df
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None