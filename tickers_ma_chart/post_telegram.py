import requests
import os
import random

def return_proxies():
    proxies = [
        "chanhouyong:Welcome@prc@sg.proxymesh.com:31280",
        "chanhouyong:Welcome@prc@jp.proxymesh.com:31280",
    ]

    proxy = random.choice(proxies)

    return proxy


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

    response = requests.post(url, data=body, files=files, proxies=proxy)

    return response.text