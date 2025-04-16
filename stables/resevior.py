import requests
import time

# Constants
RUSD_URL = "https://eth.blockscout.com/api/v2/tokens/0x09D4214C03D01F49544C0448DBE3A27f768F2b34"
TVL_URL = "https://app.reservoir.xyz/api/website"

TELE_CHAT_ID = ''
THREAD_ID = ''
TELE_API_KEY = ''

def get_data():
    try:
        rusd_resp = requests.get(RUSD_URL, timeout=10)
        tvl_resp = requests.get(TVL_URL, timeout=10)

        rusd_resp.raise_for_status()
        tvl_resp.raise_for_status()

        rusd = float(rusd_resp.json().get('exchange_rate', 0))
        tvl = float(tvl_resp.json().get('tvlRaw', 0))

        return rusd, tvl
    except (requests.RequestException, ValueError) as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        return None, None


def post_message(message):
    url = f"https://api.telegram.org/bot{TELE_API_KEY}/sendMessage"
    payload = {
        'chat_id': TELE_CHAT_ID,
        'message_thread_id': THREAD_ID,
        'text': message,
        'parse_mode': "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("[✅] Message posted successfully.")
    except requests.RequestException as e:
        print(f"[ERROR] Failed to send message: {e}")


def check_thresholds(rusd, tvl):
    alerts = []
    if rusd is not None and rusd < 0.998:
        alerts.append(f"⚠️ <b>RUSD</b> is below 0.998 — currently <b>{rusd:.4f}</b>")
    if tvl is not None and tvl < 190_000_000:
        alerts.append(f"📉 <b>RUSD TVL</b> has fallen to <b>{tvl:,.0f}</b>")
    return alerts


def main():
    while True:
        rusd, tvl = get_data()

        if rusd is None or tvl is None:
            print("⚠️ Skipping this check due to fetch error.")
        else:
            alerts = check_thresholds(rusd, tvl)
            if alerts:
                for alert in alerts:
                    post_message(alert)
            else:
                print("✅ All good — checking again in 1 min...")

        time.sleep(60)


if __name__ == "__main__":
    main()
