
import os
import statistics
from datetime import datetime

def calculate_daily_averages(): 
    data_folder = os.path.join(os.getcwd(), "data")
    tickers = [f.split('_')[0] for f in os.listdir(data_folder) if f.endswith('_data.csv')]

    for ticker in tickers:
        input_file = os.path.join(data_folder, f"{ticker}_data.csv")
        output_file = os.path.join(data_folder, f"{ticker}_daily_average.csv")
        
        # Read existing averages if file exists
        existing_averages = {}
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for line in f:
                    date, avg = line.strip().split(',')
                    existing_averages[date] = float(avg)

        # Remove today's date from existing averages if present
        today = datetime.now().strftime('%Y-%m-%d')
        if today in existing_averages:
            del existing_averages[today]
            
        # Rewrite the output file with updated existing averages
        with open(output_file, 'w') as f:
            for date, avg in existing_averages.items():
                f.write(f"{date},{avg:.2f}\n")
                
        # Calculate new averages
        new_averages = {}
        with open(input_file, 'r') as f:
            next(f)  # Skip header
            for line in f:
                timestamp, ratio = line.strip().split(',')
                if 'AVERAGE' not in timestamp:
                    date = timestamp.split()[0]
                    if date not in existing_averages:
                        if date not in new_averages:
                            new_averages[date] = []
                        new_averages[date].append(float(ratio))

        # Calculate and append new averages
        with open(output_file, 'a') as f:
            for date, ratios in new_averages.items():
                avg = statistics.mean(ratios)
                f.write(f"{date},{avg:.2f}\n")

        print(f"Daily averages calculated and appended for {ticker}")
