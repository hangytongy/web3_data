import main
import time
from misc_func import get_tickers, get_top_100_tokens_by_volume
import post_telegram
import os

current_dir = os.getcwd()
init_bot_dir = os.path.join(current_dir,"init_bot.png")

#post_telegram.send_photo_telegram(init_bot_dir, f"Initialize OI price prediction bot")

days = 30
interval = '1h'  #hour = h, day = d, min = m : hyperparam
upper_percentile = 95 #hyperparam
max_ratio = 1 #hyperparam

top_100_tokens = get_top_100_tokens_by_volume()
print("top 100 tokens by vol fetched")
print(top_100_tokens)
tokens= get_tickers(top_100_tokens)
print(f"total tickers = {len(tokens)}")

if __name__ == "__main__":
    while True:
        for token in tokens:
            print(token)
            main.run_main(days,token,interval,upper_percentile,max_ratio)
        print("sleep 1hour............")
        time.sleep(60*60)