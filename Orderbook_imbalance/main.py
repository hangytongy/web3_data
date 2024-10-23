import imbalance_calc as imbalance
import requests
import os
import csv
import time
import statistics
from datetime import datetime, date

tickers = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
percentage = 50
last_processed_date = None

def run_app(tickers, percentage):
    global last_processed_date
    current_date = date.today()

    if last_processed_date is not None and current_date > last_processed_date:
        calculate_daily_averages(last_processed_date)

    for ticker in tickers:
        result = imbalance.depth_info(ticker, percentage)
        if result is not None:
            save_result_to_csv(ticker, result)

    print(f"Data collection completed at {datetime.now()}")
    last_processed_date = current_date
    

def save_result_to_csv(ticker, result, is_daily_average=False, avg_date=None):
    directory = os.getcwd()
    data_path = os.path.join(directory,"data")
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    filename = os.path.join(data_path, f"{ticker}_data.csv")

    if is_daily_average:
        timestamp = f"{avg_date.strftime('%Y-%m-%d')} AVERAGE"
    else:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    bid_ask_ratio = result 

    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:  # If file doesn't exist, write header
            writer.writerow(['Timestamp', 'Bid Ask Ratio'])
        writer.writerow([timestamp, bid_ask_ratio])

def calculate_daily_averages(day): #this function is redundant 
    day_str = day.strftime('%Y-%m-%d')
    for ticker in tickers:
        filename = os.path.join(os.getcwd(), "data", f"{ticker}_data.csv")
        if os.path.exists(filename):
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                day_ratios = [float(row[1]) for row in reader if row[0].startswith(day_str) and 'AVERAGE' not in row[0]]
            
            if day_ratios:
                average = statistics.mean(day_ratios)
                save_result_to_csv(ticker, average, is_daily_average=True, avg_date=day)
                print(f"Daily average calculated for {ticker} on {day_str}")
                
            else:
                print(f"No data found for {ticker} on {day_str}")
        else:
            print(f"No data file found for {ticker}")

if __name__ == "__main__":
    print("Starting the application...")
    if last_processed_date is None: #redundant
        last_processed_date = date.today() # redundant 
    run_app(tickers, percentage)
    print("Application run completed.")