import main
import time
from misc_func import get_tickers, get_top_100_tokens_by_volume

days = 30
interval = '1h'  #hour = h, day = d

top_100_tokens = get_top_100_tokens_by_volume()
print("top 100 tokens by vol fetched")
print(top_100_tokens)
tokens= get_tickers(top_100_tokens)
print(f"total tickers = {len(tokens)}")

if __name__ == "__main__":
    while True:
        for token in tokens:
            print(token)
            main.run_main(days,token,interval)
        print("sleep 1hour............")
        time.sleep(60*60)