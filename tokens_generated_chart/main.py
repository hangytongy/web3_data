import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from dune_client.types import QueryParameter
from dune_client.client import DuneClient
from dune_client.query import QueryBase
import seaborn as sns
import os
from functions import get_price_history,get_tokens_created,transform_query_result
from post_telegram import send_photo_telegram
from dotenv import load_dotenv
import time

load_dotenv()

sns.set()



end_time = datetime.now()
start_time = datetime.now() + timedelta(days = -400)

#change to timestamp (s)
start_time = int(start_time.timestamp())
end_time = int(end_time.timestamp())

api_key=os.getenv("api_key")
query_id=int(os.getenv("query_id"))

query_result = get_tokens_created(api_key, query_id)

sum_result = transform_query_result(query_result, start_time)





symbols = ["SOLUSDT","BTCUSDT"]
interval = "1d"


for symbol in symbols:
    # Get the  price history
    price_history = get_price_history(symbol,interval,end_time,start_time)


    fig, ax1 = plt.subplots(figsize=(25, 10))


    ax1.bar(sum_result.index, sum_result['num_tokens'], label = 'no of tokens', linewidth = 5, color = 'red', edgecolor = 'lightblue')
    ax1.set_xlabel('date')
    ax1.set_ylabel('no of tokens created', color = 'blue')


    ax2 = ax1.twinx()
    ax2.plot(price_history.index, price_history['Close'], label = 'btc price', color = 'black')
    ax2.set_ylabel('$', color = 'black')

    plt.title(f"no of tokens created vs price of {symbol}", fontsize = 20)
    plt.legend(loc='best')
    plt.xticks(rotation=90)
    plt.savefig(f"no_of_tokens_{symbol}.png")
    time.sleep(2)

    print(f"{symbol} send photo to telegram")
    send_photo_telegram(f"no_of_tokens_{symbol}.png",f"No of tokens generated vs {symbol}")