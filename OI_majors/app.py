import main
import time
from misc_func import get_tickers, get_top_100_tokens_by_volume
import post_telegram
import os

current_dir = os.getcwd()
init_bot_dir = os.path.join(current_dir,"init_bot.png")

#post_telegram.send_photo_telegram(init_bot_dir, f"Initialize OI price prediction bot")

days = 7
interval = '1h'  #hour = h, day = d

tokens = ['BTC','ETH','SOL']

if __name__ == "__main__":
    while True:
        for token in tokens:
            print(token)
            main.run_main(days,token,interval)
        print("sleep 1hour............")
        time.sleep(60*60)