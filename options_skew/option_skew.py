import requests
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_options_skew():

    url = "https://velo.xyz/api/m/skew?coin=BTC&range=604800000&resolution=1%20hour"
    response = requests.get(url)
    
    data = response.json()['d']
    
    # Create DataFrame
    options_df = pd.DataFrame(data, columns=["timestamp", "1w", "1m", "3m", "6m"])
    
    # Convert Unix timestamp to readable datetime (optional)
    options_df["timestamp"] = pd.to_datetime(options_df["timestamp"], unit='s')
    
    options_df['1W delta 1h'] = options_df['1w'].diff()
    options_df['1W delta 2h'] = options_df['1w'].diff(2)
    options_df['1W delta 3h'] = options_df['1w'].diff(3)
    options_df['1W delta 4h'] = options_df['1w'].diff(4)

    return options_df

def get_btc_price():

    # Binance API endpoint
    url = "https://api.binance.com/api/v3/klines"
    
    # Parameters
    params = {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "limit": 168  # 7 days * 24 hours
    }
    
    # Send request
    response = requests.get(url, params=params)
    data = response.json()
    
    # Extract data
    df = pd.DataFrame(data, columns=[
        "Open time", "Open", "High", "Low", "Close", "Volume",
        "Close time", "Quote asset volume", "Number of trades",
        "Taker buy base volume", "Taker buy quote volume", "Ignore"
    ])
    
    # Convert timestamp and price columns
    df["Open time"] = pd.to_datetime(df["Open time"], unit='ms')
    df["Close"] = df["Close"].astype(float)
    
    # Keep only the necessary columns
    df = df[["Open time", "Close"]]
    df.columns = ["timestamp", "btc_price"]

    return df

def plot(options_df,df,treshold):
    colors = ['green' if val < treshold else 'lightblue' for val in options_df["1W delta 4h"]]

    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plot your 1w data on primary Y axis
    ax1.plot(options_df["timestamp"], options_df["1w"], color='tab:orange', label='Option skew', alpha = 0.8, linestyle = '-')
    
    
    # Plot your 1w data on primary Y axis
    ax1.bar(options_df["timestamp"], options_df["1W delta 4h"], color=colors,width=0.03, label='Option 4h delta')
    ax1.set_xlabel("Date")
    ax1.set_ylabel("1W Option", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.legend(loc='upper left')
    
    # Plot BTC price on secondary Y axis
    ax2 = ax1.twinx()
    ax2.plot(df["timestamp"], df["btc_price"], color='black',markersize=4, label='BTC Price')
    ax2.set_ylabel("BTC Price (USD)")
    ax2.tick_params(axis='y')
    ax2.legend(loc = 'upper right')
    
    # Titles and layout
    plt.title("1W Option vs Bitcoin Price (Hourly)")
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.grid(True)
    
    #plt.show()
    plt.savefig('btc_option_skew.png')

    return 'btc_option_skew.png'

def post_tele_mesasge(fig_path,caption, chat_id = os.getenv('CHAT_ID')):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendPhoto"

    photo = open(fig_path, "rb")

    files = {
        "photo": photo,
    }


    if "_" in chat_id:
        ids = chat_id.split("_")
        body = {
            "chat_id": ids[0],
            "message_thread_id": ids[1],
            "caption": caption,
            }
    else:
        body = {
            "chat_id": chat_id,
            "caption": caption,
            }

    print(body)

    response = requests.post(url, data=body, files=files)

    return response.text
    

def main():
    treshold = -0.045

    options_df = get_options_skew()
    df = get_btc_price()

    if options_df.iloc[-1]['1W delta 4h'] <  treshold:
        fig_path = plot(options_df,df,treshold)
        
        #add function to send pic via telegram
        post_tele_mesasge(fig_path,"BTC Options Skew Signal")

if __name__ == "__main__":
    # use pm2 json to manage the cron 
    main()
    print("cycle done, sleeping 5min........")