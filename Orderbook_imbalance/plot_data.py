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
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
        
    # Plot Bid-Ask Ratio
    for ticker, df in all_data.items():
        ax1.plot(df['Timestamp'], df['Bid Ask Ratio'], label=f'{ticker} Bid-Ask Ratio')
        
    ax1.set_title('Average Bid-Ask Ratio Over Time')
    ax1.set_ylabel('Bid-Ask Ratio')
    ax1.legend()
    ax1.grid(True)
        
    # Get and plot price data
    start_date = min(df['Timestamp'].min() for df in all_data.values()).strftime("%d %b, %Y")
    for ticker in all_data.keys():
        symbol = f'{ticker}USDT'
        price_data = get_price_data(symbol, start_date)
        ax2.plot(price_data['timestamp'], price_data['close'], label=f'{ticker} Price')
        
    ax2.set_title('Price Over Time')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Price (USDT)')
    ax2.legend()
    ax2.grid(True)
        
    # Rotate and align the tick labels so they look better
    plt.gcf().autofmt_xdate()
        
    # Save the plot
    plt.savefig('bid_ask_ratio_and_price.png')
    plt.close()

# Call the function to plot the data
all_data = get_average_data()
plot_data(all_data)


