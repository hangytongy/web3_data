import requests
import os
import random
from dotenv import load_dotenv

load_dotenv()


def send_photo_telegram(photo, caption, chat_id=os.getenv("chat_id")):
    #url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendPhoto"
    token = os.getenv("tele_token")
    url = f"https://api.telegram.org/bot{token}/sendPhoto"

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