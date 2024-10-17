import os
import time
from datetime import datetime
from tqdm import tqdm

import ccxt
import pandas as pd
import requests

import matplotlib.pyplot as plt

from dotenv import load_dotenv

import post_telegram

load_dotenv()

binance_futures_tickers = requests.get(
    "https://fapi.binance.com/fapi/v1/ticker/24hr"
).json()
binance_futures_tickers = [
    t
    for t in binance_futures_tickers
    if datetime.now().timestamp() - t["closeTime"] / 1000 < 86400 # cuz some alts delisted
]
tickers = [t["symbol"] for t in binance_futures_tickers if t["symbol"].endswith("USDT")]
binance = ccxt.binance()
binance.options["defaultType"] = "future"
today_date = datetime.today().strftime("%Y-%m-%d")

moving_averages = [50, 100, 200]
#directory = os.getenv("CHARTS_DIRECTORY")
directory = os.getcwd()
timeframe = "1d"  # <--------- Change this to get data for different timeframes

# Use only if you have the same filepath
if not os.path.exists(f"./data/{today_date}_{timeframe}"):
    os.makedirs(f"./data/{today_date}_{timeframe}")

# # Inefficient way to get data but respects the rate limit in the event of other scripts running
for ticker in tqdm(tickers):
    future = binance.fetch_ohlcv(ticker.replace("USDT", "/USDT"), timeframe, limit=5000)
    df = pd.DataFrame(future)
    df.set_index(0, inplace=True)
    df.columns = ["open", "high", "low", "close", "volume"]
    df.volume = df.volume * df.close
    df.index = pd.to_datetime(df.index, unit="ms")
    df.to_csv(f"./data/{today_date}_{timeframe}/{ticker.replace('USDT', '')}.csv")
    time.sleep(1.5)  # We are allowed 1200 requests per minute hence 1.25s

for moving_average in moving_averages:
    charts_file = os.path.join(directory, f"sal_{moving_average}MA.png")

    #price_history = pd.DataFrame()
    df_list = []
    for ticker in tickers:
        df = pd.read_csv(f"./data/{today_date}_{timeframe}/{ticker.replace('USDT', '')}.csv", index_col=0)
        #price_history[ticker] = df["close"]
        df_list.append(df["close"].rename(ticker))
    price_history = pd.concat(df_list, axis=1)

    # Assuming price_history is already defined and loaded with historical data
    price_history.index = pd.to_datetime(price_history.index)
    price_history.sort_index(inplace=True)
    # Calculate moving averages
    moving_averages = price_history.rolling(window=moving_average, min_periods=5).mean()

    # Slice to the last 400 days
    moving_averages = moving_averages.iloc[-400:]
    tmp_price_history = price_history.iloc[-400:]

    # Determine if prices are above their moving averages
    above_ma = tmp_price_history > moving_averages

    # Count the number of tickers above their moving average
    num_above_ma = above_ma.sum(axis=1)

    # Convert to percentage
    num_above_ma_percentage = (num_above_ma / len(tmp_price_history.columns)) * 100
    
    #percentage ma is below 93%
    upper_threshold = 6
    
    bottom_ma = num_above_ma_percentage[num_above_ma_percentage < upper_threshold]
    bottom_ma = -bottom_ma
    
    #percentage ma is above 77%
    lower_threshold = 77
    
    top_ma = num_above_ma_percentage[num_above_ma_percentage > lower_threshold]
    

    # Get current percentage
    current_percentage = num_above_ma_percentage.iloc[-1]

    # Get Bitcoin prices
    bitcoin_prices = tmp_price_history["BTCUSDT"]
    bitcoin_prices = bitcoin_prices.reindex(tmp_price_history.index)  # Ensure the indices match
    
    # Plot the results
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot the percentage of tickers above the 50-day moving average
    ax1.bar(num_above_ma_percentage.index, num_above_ma_percentage,width = 0.6,alpha=0.5,label="Percentage of Tickers above MA")
    ax1.bar(bottom_ma.index, bottom_ma, width = 0.6, color = 'green')
    ax1.bar(top_ma.index, top_ma, width = 0.6, color = 'red')

    ax1.set_title(f"Percentage of Tickers above {moving_average}-day Moving Average Over Time and Bitcoin Prices")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Percentage of Tickers")
    ax1.grid(True)

    # Add buffer to the right
    ax1.set_xlim(tmp_price_history.index[0], tmp_price_history.index[-1] + pd.DateOffset(days=30))

    ax2 = ax1.twinx()
    
    ax2.plot(bitcoin_prices.index, bitcoin_prices, color = 'black', label = 'BTC price')
    ax2.set_ylabel("Bitcoin Prices")

    ax1.legend(loc="upper left", bbox_to_anchor=(0, 1), ncol=1)
    ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.9), ncol=1)

    fig.savefig(charts_file)
    post_telegram.send_photo_telegram(charts_file, f"Percentage of Coins {moving_average} Days MA Chart vs BTC")