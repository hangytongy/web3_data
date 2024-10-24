import requests
import pandas as pd
from get_oi_data import init_client
from datetime import datetime, timedelta


def get_colors(df):
    colors_ratio = df['Ratio'].apply(lambda x : 'lime' if x > 0 else 'red')
    colors_OI = df['open_interest_change_%'].apply(lambda x :'lime' if x > 0 else 'red' )
    
    return colors_ratio,colors_OI



def get_tickers(top_100_tokens):
    client = init_client()
    velo_coins = [x['coin'] for x in client.get_spot()]
    velo_coins = pd.unique(velo_coins)

    list_of_symbols = []

    # Convert velo_coins to a set for faster lookup
    velo_coins_set = set(velo_coins)

    # Iterate through the Binance tickers
    for symbol in top_100_tokens:
        
        # Check if the symbol starts with any velo_coin
        if symbol[:-4] in velo_coins_set and symbol.endswith('USDT'):
            list_of_symbols.append(symbol[:-4])

    return list_of_symbols

def get_top_100_tokens_by_volume():
    # Binance API endpoint for 24hr ticker price change statistics
    url = 'https://api.binance.com/api/v3/ticker/24hr'

    # Send a request to the API
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        # Create a list of tuples (symbol, volume)
        token_volumes = [(item['symbol'], float(item['quoteVolume'])) for item in data if item['symbol'][-4:] == "USDT"]
        
        # Sort the list by volume in descending order and get the top 50
        top_100_token_volumes = sorted(token_volumes, key=lambda x: x[1], reverse=True)[:100]

        # Extract only the token symbols
        top_100_token_symbols = [token for token, volume in top_100_token_volumes]

        return top_100_token_symbols
    else:
        print(f"Failed to fetch data from Binance. Status code: {response.status_code}")
        return []

def loss_function(dump,df_merge,token,days):
    #get predicted dump row - time and close
    score = 0
    for row in dump.index:
        dump_time = dump.loc[row, 'time']
        dump_close = dump.loc[row, 'Close']
        
        #from predicted dump time and close, get the data for the next 2 days from df_merge
        dump_time_end = dump_time + timedelta(days=days)
        cond1 = df_merge['time'] >= dump_time
        cond2 = df_merge['time'] <= dump_time_end
        df_frame = df_merge[cond1 & cond2]
        
        # if at any instance, df_merge Close is lower than dump Close, score + 1
        df_frame = df_frame.copy()
        df_frame.loc[:, 'score'] = df_frame['Close'].apply(lambda x: 1 if x < dump_close else 0)
        scoring = df_frame['score'].sum()
        
        if scoring > 0:
            score += 1
    # get average of scores to get accuracy rate for the token
    accuracy = round(score/len(dump) * 100,2)
    #return accuracy rate for that token
    print(f"accurary for {token} is {accuracy}%")
    return accuracy

