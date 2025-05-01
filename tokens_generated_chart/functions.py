import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from dune_client.types import QueryParameter
from dune_client.client import DuneClient
from dune_client.query import QueryBase
import seaborn as sns
import os
from dotenv import load_dotenv

load_dotenv()

sns.set()

def get_price_history(symbol,interval,end_time,start_time):

    print(f"Get price history for {symbol}")
    # Binance API endpoint for historical klines
    url = "https://api.binance.com/api/v3/klines"
    
    # Parameters for the API call
    #end_time = int(datetime.now().timestamp() * 1000)
    #start_time = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
    
    end_time = end_time * 1000
    start_time = start_time * 1000
    
    print(end_time)
    print(start_time)
    
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

        print("price history data collection done")

        return df
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    
def get_tokens_created(api_key,query_id):

    print("get no of tokens created via Dunes")

    dune = DuneClient(
        api_key=api_key,
        base_url="https://api.dune.com",
        request_timeout=600
    )
    
    query = QueryBase(query_id=query_id)
    
    query_result = dune.run_query_dataframe(query=query)

    print("query completed")
    
    return query_result


def transform_query_result(query_result, timestamp):
    query_result['week'] = pd.to_datetime(query_result['week']).dt.date
    dt = pd.to_datetime(timestamp, unit='s').date()
    
    result = query_result[query_result['week'] > dt]
    result = result.sort_values('week')
    sum_result = result.groupby('week').sum()
    
    return sum_result