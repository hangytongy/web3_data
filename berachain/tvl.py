import pandas as pd
import requests
import matplotlib.pyplot as plt
import time

def get_tvl():
    url = "https://api.llama.fi/v2/historicalChainTvl/Berachain"
    response = requests.get(url)
    df = pd.DataFrame(response.json())
    df['date'] = pd.to_datetime(df['date'], unit = 's')

    plt.figure(figsize = (12,5))
    plt.plot(df['date'], df['tvl'])
    plt.xlabel('Date')
    plt.ylabel('TVL')
    plt.title("Berachain TVL from Defillama")
    plt.grid()
    plt.savefig('bera_tvl.png')


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
        get_tvl()
        send_photo_telegram('bera_tvl.png','Berachain TVL')
        time.sleep(60*60*24)
