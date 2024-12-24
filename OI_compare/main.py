import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from velodata import lib as velo
import numpy as np
from functools import reduce
import seaborn as sns
from post_telegram import send_photo_telegram

sns.set()

def init_client():
    api_key = '4a2a1de7c0d440c983bf5b0e7f1fc366'
    # new velo client
    client = velo.client(api_key)
    return client 

def get_tickers():
    client = init_client()
    velo_coins = [x['coin'] for x in client.get_spot()]
    velo_coins = pd.unique(velo_coins)

    return velo_coins.tolist()
    
def get_oi(symbol):
    btc_oi_url = f"https://velo.xyz/api/m/oi?coin={symbol}&range=2592000000&resolution=24%20hours"

    response = requests.get(btc_oi_url)
    df = pd.DataFrame(response.json()['d'],columns=['timestamp','paltform','oi'])
    df['time'] = df['timestamp'].apply(lambda x : datetime.fromtimestamp(x).date())
    df = df.drop(columns = ['timestamp'])
    df = df.groupby('time').sum('oi')

    return df

def query_cme(token,all_alts_oi):
    url = f'https://velo.xyz/api/m/cmeOi?product={token}&range=3592000000&resolution=1%20day'
    response = requests.get(url)
    data = response.json()['d']
    data_dict = {'timestamp' : [row[0] for row in data], 'value' : [row[1] for row in data]}
    df = pd.DataFrame(data_dict)
    df['time'] = pd.to_datetime(df['timestamp'], unit = 's')
    df = df.set_index('time')

    #fill in missing CME OI data
    full_date_range = pd.date_range(start=df.index.min(), end=all_alts_oi.index.max(), freq='D')
    df = df.reindex(full_date_range)
    df['value'] = df['value'].ffill()
    df = df.drop(columns = ['timestamp'])
    df.index = df.index.date
    cond1 = df.index >= all_alts_oi.index.min()
    df = df[cond1]
    
    return df

def merge_data(oi,cme):
    df = pd.merge(oi, cme, left_index=True, right_index=True, how='outer')
    df['oi'] = df['oi'] + df['value']
    df = df.drop(columns = ['value'])

    return df

def plot_data(all_alts_oi,btc,eth, cme):
    # Plotting the 'price_sum' on the y-axis with the date on the x-axis
    plt.figure(figsize=(10, 6))
    plt.plot(all_alts_oi.index, all_alts_oi['alts_sum'], marker='o', color='b', label='Alts oi')
    plt.plot(btc.index, btc['oi'], marker='o', color='orange', label='BTC oi')
    plt.plot(eth.index, eth['oi'], marker='o', color='green', label='ETH oi')
    
    
    # Adding labels and title
    plt.xlabel('Date')
    plt.ylabel('OI')
    plt.title('OI crypto')
    
    # Optional: Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Display the legend
    plt.legend()
    
    # Show the plot
    plt.tight_layout()  # Adjust layout for better spacing

    if cme:
        plt.savefig('oi_plot_cme.png')
    else:
        plt.savefig('oi_plot.png')

def main():

    #get all tickers without BTC and ETH
    tickers = get_tickers()
    tickers.remove('BTC')
    tickers.remove('ETH')

    #get OI for all alt tickers
    alts_oi = []
    
    for ticker in tickers:
        df = get_oi(ticker)
        alts_oi.append(df)
        print(f"appended for {ticker}")

    #combine all alts to get overall OI for alts only
    for i, df in enumerate(alts_oi):
        alts_oi[i] = df.rename(columns={col: f"{col}_df{i+1}" for col in df.columns})
    
    # Merge all dataframes using reduce
    merged_df = reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how='outer'), alts_oi)
    
    # Sum the OI columns to get overall OI
    merged_df['alts_sum'] = merged_df.filter(like='oi').sum(axis=1)
    all_alts_oi = merged_df.drop(columns=merged_df.filter(like='oi').columns)

    #Get major's OI
    btc_oi = get_oi('BTC')
    eth_oi = get_oi('ETH')

    #Get major's CME OI
    btc_cme = query_cme('BTC',all_alts_oi)
    eth_cme = query_cme('ETH',all_alts_oi)

    #Combine Major's OI
    btc_oi_merge = merge_data(btc_oi,btc_cme)
    eth_oi_merge = merge_data(eth_oi,eth_cme)

    #plot all data w/o CME
    plot_data(all_alts_oi,btc_oi,eth_oi,False)
    send_photo_telegram('oi_plot.png',"OI BTC vs ETH vs Alts w/o CME")
    
    #plot all data w CME
    plot_data(all_alts_oi,btc_oi_merge,eth_oi_merge,True)
    send_photo_telegram('oi_plot_cme.png',"OI BTC vs ETH vs Alts w CME")

if __name__ == "__main__":
    main()