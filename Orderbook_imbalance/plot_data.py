import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from datetime import datetime, timedelta
from get_daily_average import calculate_daily_averages

def get_average_data():
    calculate_daily_averages()  # Ensure daily averages are up to date
    data_folder = os.path.join(os.getcwd(), "data")
    tickers = ['BTC', 'ETH', 'SOL']
    all_data = {}

    for ticker in tickers:
        filename = os.path.join(data_folder, f"{ticker}USDT_daily_average.csv")
        if os.path.exists(filename):
            df = pd.read_csv(filename, names=['Timestamp', 'Bid Ask Ratio'], parse_dates=['Timestamp'])
            df['Bid Ask Ratio'] = df['Bid Ask Ratio'].astype(float)
            all_data[ticker] = df
        else:
            print(f"No daily average file found for {ticker}")

    return all_data

def get_price_data(symbol, start_date):
    client = Client()
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, start_date)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['close'] = df['close'].astype(float)
    return df[['timestamp', 'close']]

def plot_data(all_data):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 18), sharex=True)
    axes = [ax1, ax2, ax3]
    
    start_date = min(df['Timestamp'].min() for df in all_data.values()).strftime("%d %b, %Y")
    
    for i, (ticker, df) in enumerate(all_data.items()):
        ax = axes[i]
        ax2 = ax.twinx()
        
        # Plot Price data
        symbol = f'{ticker}USDT'
        price_data = get_price_data(symbol, start_date)
        ax.plot(price_data['timestamp'], price_data['close'], label=f'{ticker} Price', color='blue')
        
        # Plot Bid-Ask Ratio
        ax2.bar(df['Timestamp'], df['Bid Ask Ratio'], label=f'{ticker} Bid-Ask Ratio', color='red', alpha=0.5, width=1)
        
        ax.set_title(f'{ticker} Price and Bid-Ask Ratio Over Time')
        ax.set_ylabel('Price (USDT)', color='blue')
        ax2.set_ylabel('Bid-Ask Ratio', color='red')
        
        ax.tick_params(axis='y', labelcolor='blue')
        ax2.tick_params(axis='y', labelcolor='red')
        
        ax.grid(True)
        
        # Combine legends
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.xlabel('Date')
    
    # Rotate and align the tick labels so they look better
    plt.gcf().autofmt_xdate()
    
    # Adjust layout and save the plot
    plt.tight_layout()
    plt.savefig('price_and_bid_ask_ratio.png')
    plt.close()

# Call the function to plot the data
all_data = get_average_data()
plot_data(all_data)


