import requests
import time
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


# === CONFIGURATION ===
URL = "https://velo.xyz/api/m/skew?coin=BTC&range=604800000&resolution=1%20hour"
THRESHOLD = 0.15        # change to 0.15 (15%)
SLEEP_INTERVAL = 120 * 60  # 2 hours
RESET_SLEEP = 6 * 60 * 60  # 6 hours
SAVE_PATH = "btc_1w_skew.png"

options_skew = []


def fetch_skew_data(url):
    """Fetch latest BTC skew data."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.SSLError as e:
        print(f"[SSL ERROR] {e}")
    except requests.exceptions.RequestException as e:
        print(f"[REQUEST ERROR] {e}")
    return None


def process_latest_data(data):
    """Extract and process latest timestamp and skew value."""
    latest_timestamp = data["d"][-1][0]
    latest_skew = data["d"][-1][1]
    latest_time = datetime.fromtimestamp(latest_timestamp).strftime("%Y-%m-%d %H:%M")
    print(f"[{latest_time}] Latest skew: {latest_skew:.4f}")
    return latest_time, latest_skew


def plot_skew(data):
    data = data["d"]

    # === CREATE DATAFRAME ===
    df = pd.DataFrame(data, columns=["timestamp", "1w", "1m", "3m", "6m"])
    df["time"] = pd.to_datetime(df["timestamp"], unit="s")

    # === PLOT 1W SKEW ===
    plt.figure(figsize=(12, 6))
    plt.plot(df["time"], df["1w"], color="#1f77b4", linewidth=2.5)

    # === BEAUTIFY ===
    plt.title("Bitcoin 1W Options Skew (VELO.xyz)", fontsize=16, fontweight="bold", pad=15)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("1W Skew", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()

    # === AXIS & STYLE ===
    plt.xticks(rotation=45)
    plt.gcf().autofmt_xdate()

    # === SAVE & SHOW ===
    plt.savefig(SAVE_PATH, dpi=300, bbox_inches="tight")
    print(f"✅ Chart saved to {SAVE_PATH}")

def send_telegram_alert(fig_path,caption, chat_id = os.getenv('CHAT_ID')):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendPhoto"

    photo = open(fig_path, "rb")

    files = {
        "photo": photo,
    }


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
    


def main():
    global options_skew
    print("📈 Starting BTC skew monitor...")
    count = 0

    while True:
        data = fetch_skew_data(URL)
        if not data:
            print("⚠️ No data, retrying in 1 minute...")
            time.sleep(60)
            continue

        latest_timestamp, latest_skew = process_latest_data(data)

        # Track significant skew changes
        if latest_skew > THRESHOLD:
            print(f"Skew more than threshold {THRESHOLD}, appneding...")
            options_skew.append({latest_timestamp: latest_skew})

        # Handle first data point
        if len(options_skew) < 2:
            print("⏳ Waiting for next data point...")
            time.sleep(SLEEP_INTERVAL)
            continue

        # Compare old vs new skew
        old_skew_time, old_skew = list(options_skew[0].items())[0]
        new_skew_time, new_skew = list(options_skew[1].items())[0]

        print(f"Comparing: old={old_skew:.4f} new={new_skew:.4f}")

        if new_skew > old_skew:
            plot_skew(data)
            msg = f"BTC 1w skew increased from {old_skew:.2%} to {new_skew:.2%} during {old_skew_time} to {new_skew_time}"
            send_telegram_alert(SAVE_PATH,msg)
            options_skew.clear()
            print(f"😴 Sleeping {RESET_SLEEP/3600:.1f} hours...")
            time.sleep(RESET_SLEEP)
        else:
            print("📉 Skew did not increase — keeping previous value only.")
            options_skew = [options_skew[-1]]
            count += 1
            #if no new data in 1 week, restart
            if count >= (604800/SLEEP_INTERVAL):
                count = 0
                options_skew.clear()

        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
