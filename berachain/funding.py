import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time

def plotting():

    funding = "https://velo.xyz/api/m/funding?coin=BERA&range=604800000&resolution=1%20hour"
    response = requests.get(funding)
    funding = response.json()['d']
    df_funding = pd.DataFrame(funding, columns=['timestamp', 'exchange', 'funding'])
    df_funding['timestamp'] = pd.to_datetime(df_funding['timestamp'], unit='s')

    price = "https://velo.xyz/api/m/closes?coin=BERAUSDT&range=604800000&resolution=1%20hour"
    response = requests.get(price)
    price = response.json()['d']
    df_price = pd.DataFrame(price, columns = ['timestamp','price'])
    df_price['timestamp'] = pd.to_datetime(df_price['timestamp'], unit='s')

    # Create figure and axis
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Plot funding rates on primary y-axis
    sns.lineplot(data=df_funding, x='timestamp', y='funding', hue='exchange', ax=ax1)
    ax1.set_ylabel("Funding Rate")
    ax1.set_xlabel("Timestamp")
    ax1.tick_params(axis='y')
    ax1.legend(title="Exchange", loc="best")

    # Create secondary y-axis
    ax2 = ax1.twinx()
    sns.lineplot(data=df_price, x='timestamp', y='price', color='black', linestyle="--", ax=ax2)
    ax2.set_ylabel("Price")
    ax2.tick_params(axis='y', colors='black')

    # Formatting
    plt.title("$BERA Funding Rates & Price Over Time")
    ax1.grid(True)
    plt.xticks(rotation=45)
    
    plt.savefig('bera_funding.png')
    

def send_photo_telegram(photo, caption, chat_id=""):
    #url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendPhoto"
    token = ""
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    proxy_choice = return_proxies()
    proxy = {
        "http": f"http://{proxy_choice}",
        "https": f"http://{proxy_choice}",
    }

    photo = open(photo, "rb")

    files = {
        "photo": photo,
    }

    if chat_id is None:
        if "_" in os.getenv("TELEGRAM_CHAT_ID"):
            ids = os.getenv("TELEGRAM_CHAT_ID").split("_")

            body = {
                "chat_id": ids[0],
                "message_thread_id": ids[1],
                "caption": caption,
            }
        else:
            body = {
                "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
                "caption": caption,
            }
    else:
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


if __name__ == "__main__":
    while True:
        plotting()
        send_photo_telegram('bera_funding.png','Bera Funding')
        time.sleep(60*60*12)
